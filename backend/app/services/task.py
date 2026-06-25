import json
import logging
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.dataset_files import resolve_storage_path
from app.core.runner.process import ProcessRunner
from app.core.storage.factory import get_storage
from app.core.storage.paths import StoragePaths
from app.exceptions import TaskStateError
from app.models.model import MLModel
from app.models.task import TERMINAL_STATUSES, Task, TaskStatus
from app.repositories.dataset import DatasetRepository
from app.repositories.dataset_version import DatasetExportRepository
from app.repositories.model import MLModelRepository
from app.repositories.task import TaskRepository
from app.schemas.task import TaskArtifactItem, TaskCreate

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
            dataset_version_id=data.dataset_version_id,
            dataset_export_id=data.dataset_export_id,
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
                config["weight_path"] = str(resolve_storage_path(model.weight_path))
            else:
                raise ValueError("所选预训练模型缺少权重文件")

        if entity.dataset_export_id:
            export_repo = DatasetExportRepository(self.session)
            dataset_export = await export_repo.get_by_id(entity.dataset_export_id)
            if dataset_export and dataset_export.data_yaml_path:
                config["data_yaml_path"] = str(resolve_storage_path(dataset_export.data_yaml_path))
            else:
                raise ValueError("Selected dataset export is missing dataset.yaml")
        elif entity.dataset_id:
            dataset_repo = DatasetRepository(self.session)
            dataset = await dataset_repo.get_by_id(entity.dataset_id)
            if dataset and dataset.storage_path:
                config["data_yaml_path"] = str(resolve_storage_path(dataset.storage_path))
            else:
                raise ValueError("所选数据集缺少 data.yaml 配置")

        config["project_dir"] = str(StoragePaths.run_root(task_id))
        config["run_name"] = "eval" if entity.task_type == "evaluation" else "train"

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
        elif result.get("status") == TaskStatus.FAILED.value:
            entity.status = TaskStatus.FAILED
            entity.error_message = result.get("error", "Unknown error")
            entity.result = result
            entity.finished_at = datetime.now(timezone.utc)
        return await self.repo.update(entity)

    async def delete_task(self, task_id: uuid.UUID) -> bool:
        entity = await self.repo.get_by_id(task_id)
        if not entity:
            return False
        if entity.status not in TERMINAL_STATUSES:
            await self.runner.cancel(str(task_id))
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

    async def list_artifacts(self, task_id: uuid.UUID) -> list[TaskArtifactItem]:
        entity = await self.repo.get_by_id(task_id)
        if not entity:
            return []

        run_name = "eval" if entity.task_type == "evaluation" else "train"
        run_dir = StoragePaths.task_run_dir(task_id, run_name)
        if not run_dir.exists():
            return []

        artifact_names = [
            "results.png",
            "results.csv",
            "labels.jpg",
            "train_batch0.jpg",
            "train_batch1.jpg",
            "train_batch2.jpg",
            "train_batch3.jpg",
            "train_batch4.jpg",
            "val_batch0_labels.jpg",
            "val_batch0_pred.jpg",
            "confusion_matrix.png",
            "confusion_matrix_normalized.png",
            "BoxPR_curve.png",
            "BoxP_curve.png",
            "BoxR_curve.png",
            "BoxF1_curve.png",
        ]
        items: list[TaskArtifactItem] = []
        for filename in artifact_names:
            path = run_dir / filename
            if path.exists():
                items.append(
                    TaskArtifactItem(
                        key=filename.rsplit(".", 1)[0],
                        filename=filename,
                        url=f"/api/v1/tasks/{task_id}/artifacts/{filename}",
                    )
                )
        return items

    async def get_artifact_path(self, task_id: uuid.UUID, filename: str) -> Path | None:
        entity = await self.repo.get_by_id(task_id)
        if not entity:
            return None
        run_name = "eval" if entity.task_type == "evaluation" else "train"
        path = StoragePaths.task_run_dir(task_id, run_name) / filename
        if not path.exists() or not path.is_file():
            return None
        return path

    async def export_model(self, task_id: uuid.UUID) -> MLModel | None:
        entity = await self.repo.get_by_id(task_id)
        if not entity or entity.status != TaskStatus.COMPLETED:
            return None
        result = entity.result or {}
        weight_path_str = result.get("weight_path")
        if not weight_path_str:
            return None

        source_path = resolve_storage_path(weight_path_str)
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
