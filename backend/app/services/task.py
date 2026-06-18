import json
import logging
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.runner.process import ProcessRunner
from app.core.storage.factory import get_storage
from app.core.storage.paths import StoragePaths
from app.exceptions import TaskStateError
from app.models.model import MLModel
from app.models.task import TERMINAL_STATUSES, Task, TaskStatus
from app.repositories.dataset import DatasetRepository
from app.repositories.model import MLModelRepository
from app.repositories.task import TaskRepository
from app.schemas.task import TaskCreate

logger = logging.getLogger(__name__)

_WORKER_MODULES: dict[str, str] = {
    "training": "app.runners.train_worker",
    "evaluation": "app.runners.eval_worker",
}


class TaskService:
    def __init__(self, session: AsyncSession) -> None:
        self.repo = TaskRepository(session)
        self.session = session
        self.runner = ProcessRunner()
        self.storage = get_storage()

    @staticmethod
    def _resolve_path(path_str: str) -> Path:
        p = Path(path_str)
        if p.is_absolute():
            return p
        return settings.storage_path.parent / p

    async def list_tasks(
        self, offset: int = 0, limit: int = 20, task_type: str | None = None
    ) -> list[Task]:
        if task_type:
            return await self.repo.list_by_type(task_type, offset=offset, limit=limit)
        return await self.repo.list(offset=offset, limit=limit)

    async def get_task(self, task_id: uuid.UUID) -> Task | None:
        return await self.repo.get_by_id(task_id)

    async def create_task(self, data: TaskCreate) -> Task:
        entity = Task(
            name=data.name,
            task_type=data.task_type,
            model_id=data.model_id,
            dataset_id=data.dataset_id,
            config=data.config,
        )
        return await self.repo.create(entity)

    async def start_task(self, task_id: uuid.UUID) -> Task | None:
        entity = await self.repo.get_by_id(task_id)
        if not entity:
            return None
        if entity.status != TaskStatus.PENDING:
            raise TaskStateError(f"Cannot start task in status {entity.status.value}")

        config = dict(entity.config or {})
        config["task_id"] = str(task_id)
        config["worker_module"] = _WORKER_MODULES.get(
            entity.task_type, "app.runners.train_worker"
        )

        if entity.model_id:
            model_repo = MLModelRepository(self.session)
            model = await model_repo.get_by_id(entity.model_id)
            if model and model.weight_path:
                config["weight_path"] = str(self._resolve_path(model.weight_path))
            else:
                raise ValueError("所选预训练模型缺少权重文件")

        if entity.dataset_id:
            dataset_repo = DatasetRepository(self.session)
            dataset = await dataset_repo.get_by_id(entity.dataset_id)
            if dataset and dataset.storage_path:
                config["data_yaml_path"] = str(self._resolve_path(dataset.storage_path))
            else:
                raise ValueError("所选数据集缺少 data.yaml 配置")

        result = await self.runner.run(str(task_id), config)
        entity.status = TaskStatus.RUNNING
        entity.started_at = datetime.now(timezone.utc)
        entity.worker_pid = result.get("pid")
        return await self.repo.update(entity)

    async def cancel_task(self, task_id: uuid.UUID) -> Task | None:
        entity = await self.repo.get_by_id(task_id)
        if not entity:
            return None
        if entity.status in TERMINAL_STATUSES:
            return entity
        await self.runner.cancel(str(task_id))
        entity.status = TaskStatus.CANCELLED
        entity.finished_at = datetime.now(timezone.utc)
        return await self.repo.update(entity)

    async def get_progress(self, task_id: uuid.UUID) -> dict[str, Any]:
        progress = await self.runner.get_progress(str(task_id))
        return {"task_id": str(task_id), "progress": progress}

    async def sync_result(self, task_id: uuid.UUID) -> Task | None:
        entity = await self.repo.get_by_id(task_id)
        if not entity or entity.status in TERMINAL_STATUSES:
            return entity
        result = await self.runner.get_result(str(task_id))
        if not result:
            return entity

        if result.get("status") == TaskStatus.COMPLETED.value:
            entity.status = TaskStatus.COMPLETED
            entity.result = result
            entity.progress = 100
            entity.finished_at = datetime.now(timezone.utc)
            if entity.task_type == "training" and result.get("weight_path"):
                await self._register_trained_model(entity, result)
        elif result.get("status") == TaskStatus.FAILED.value:
            entity.status = TaskStatus.FAILED
            entity.error_message = result.get("error", "Unknown error")
            entity.result = result
            entity.finished_at = datetime.now(timezone.utc)
        return await self.repo.update(entity)

    async def _register_trained_model(
        self, task: Task, result: dict[str, Any]
    ) -> None:
        weight_path = result["weight_path"]
        weight_file = self._resolve_path(weight_path)
        size_mb = (
            round(weight_file.stat().st_size / (1024 * 1024), 2)
            if weight_file.exists() else None
        )
        config = task.config or {}
        metrics = {
            k: result[k]
            for k in ("map50", "map50_95", "precision", "recall")
            if k in result
        }
        model = MLModel(
            name=f"{task.name}_output",
            framework=config.get("framework", "ultralytics"),
            model_source="trained",
            status="ready",
            weight_path=str(weight_file),
            model_size_mb=size_mb,
            dataset_id=task.dataset_id,
            metrics=metrics,
        )
        model_repo = MLModelRepository(self.session)
        await model_repo.create(model)

    async def delete_task(self, task_id: uuid.UUID) -> bool:
        entity = await self.repo.get_by_id(task_id)
        if not entity:
            return False
        if entity.status not in TERMINAL_STATUSES:
            raise TaskStateError(f"Cannot delete task in status {entity.status.value}")
        await self.repo.delete(entity)
        relative_path = str(Path("tasks") / str(task_id))
        await self.storage.delete_dir(relative_path)
        return True

    async def get_history(self, task_id: uuid.UUID) -> list[dict[str, Any]]:
        relative_path = str(Path("tasks") / str(task_id) / "history.json")
        if not await self.storage.exists(relative_path):
            return []
        try:
            content = await self.storage.load(relative_path)
            return json.loads(content)
        except (ValueError, OSError):
            return []

    async def export_model(self, task_id: uuid.UUID) -> MLModel | None:
        entity = await self.repo.get_by_id(task_id)
        if not entity or entity.status != TaskStatus.COMPLETED:
            return None
        result = entity.result or {}
        weight_path_str = result.get("weight_path")
        if not weight_path_str:
            return None

        source_path = self._resolve_path(weight_path_str)
        if not source_path.exists():
            return None

        config = entity.config or {}
        metrics = {
            k: result[k]
            for k in ("map50", "map50_95", "precision", "recall")
            if k in result
        }
        model = MLModel(
            name=f"{entity.name}_model",
            framework=config.get("framework", "ultralytics"),
            model_source="trained",
            status="ready",
            dataset_id=entity.dataset_id,
            metrics=metrics,
        )
        model_repo = MLModelRepository(self.session)
        model = await model_repo.create(model)

        target_relative = str(Path("models") / str(model.id) / source_path.name)
        source_relative = str(source_path.relative_to(settings.storage_path))
        content = await self.storage.load(source_relative)
        await self.storage.save(target_relative, content)

        model.weight_path = str(StoragePaths.model_dir(model.id) / source_path.name)
        model.model_size_mb = round(len(content) / (1024 * 1024), 2)
        return await model_repo.update(model)
