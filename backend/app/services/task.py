import json
import logging
import time
import uuid
from csv import DictReader
from collections.abc import Mapping
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.dataset_files import resolve_storage_path
from app.core.runner.process import ProcessRunner
from app.core.storage.factory import get_storage
from app.core.storage.paths import StoragePaths
from app.exceptions import NotFoundError, TaskStateError, ValidationError
from app.models.dataset_version import DatasetExport, DatasetVersion
from app.models.model import MLModel
from app.models.task import TERMINAL_STATUSES, Task, TaskStatus
from app.repositories.dataset import DatasetRepository
from app.repositories.dataset_version import (
    DatasetExportRepository,
    DatasetVersionRepository,
)
from app.repositories.model import MLModelRepository
from app.repositories.task import TaskRepository
from app.schemas.task import TaskArtifactItem, TaskCreate

logger = logging.getLogger(__name__)

_WORKER_MODULES: dict[str, str] = {
    "training": "app.runners.train_worker",
    "evaluation": "app.runners.eval_worker",
}
_RESULT_SYNC_GRACE_SECONDS = 15


class TaskService:
    def __init__(self, session: AsyncSession) -> None:
        self.repo = TaskRepository(session)
        self.session = session
        self.runner = ProcessRunner()
        self.storage = get_storage()
        self.model_repo = MLModelRepository(session)
        self.dataset_repo = DatasetRepository(session)
        self.export_repo = DatasetExportRepository(session)
        self.version_repo = DatasetVersionRepository(session)

    async def list_tasks(
        self, offset: int = 0, limit: int = 20, task_type: str | None = None
    ) -> list[Task]:
        if task_type:
            return await self.repo.list_by_type(
                task_type,
                offset=offset,
                limit=limit,
            )
        return await self.repo.list(offset=offset, limit=limit)

    async def get_task(self, task_id: uuid.UUID) -> Task | None:
        return await self.repo.get_by_id(task_id)

    async def create_task(self, data: TaskCreate) -> Task:
        config = dict(data.config or {})
        dataset_id = data.dataset_id
        dataset_version_id = data.dataset_version_id

        if data.task_type == "training":
            export = await self._require_ready_training_export(data.dataset_export_id)
            version = await self._get_dataset_version_or_raise(export.dataset_version_id)
            config = await self._build_training_task_config(
                config=config,
                export=export,
                version=version,
                model_id=data.model_id,
            )
            dataset_id = export.dataset_id
            dataset_version_id = export.dataset_version_id

        entity = Task(
            name=data.name,
            task_type=data.task_type,
            model_id=data.model_id,
            dataset_id=dataset_id,
            dataset_version_id=dataset_version_id,
            dataset_export_id=data.dataset_export_id,
            config=config,
        )
        return await self.repo.create(entity)

    async def start_task(self, task_id: uuid.UUID) -> Task | None:
        entity = await self.repo.get_by_id(task_id)
        if not entity:
            return None
        if entity.status != TaskStatus.PENDING:
            raise TaskStateError(
                f"Cannot start task in status {entity.status.value}"
            )

        config = dict(entity.config or {})
        config["task_id"] = str(task_id)
        config["worker_module"] = _WORKER_MODULES.get(
            entity.task_type,
            "app.runners.train_worker",
        )

        if entity.model_id:
            model = await self.model_repo.get_by_id(entity.model_id)
            if model and model.weight_path:
                config["weight_path"] = str(resolve_storage_path(model.weight_path))
                config["model_name"] = model.name
                config["model_version"] = model.version or "--"
            else:
                raise ValidationError("所选预训练模型缺少权重文件")

        if entity.task_type == "training":
            dataset_export = await self._require_ready_training_export(
                entity.dataset_export_id
            )
            config["data_yaml_path"] = str(
                resolve_storage_path(str(dataset_export.data_yaml_path))
            )
            config["training_input_mode"] = "dataset_export"
        elif entity.dataset_export_id:
            dataset_export = await self.export_repo.get_by_id(entity.dataset_export_id)
            if dataset_export and dataset_export.data_yaml_path:
                config["data_yaml_path"] = str(
                    resolve_storage_path(dataset_export.data_yaml_path)
                )
            else:
                raise ValidationError("所选数据导出记录缺少 dataset.yaml")
        elif entity.dataset_id:
            dataset = await self.dataset_repo.get_by_id(entity.dataset_id)
            if dataset and dataset.storage_path:
                config["data_yaml_path"] = str(
                    resolve_storage_path(dataset.storage_path)
                )
            else:
                raise ValidationError("所选数据集缺少 data.yaml 配置")

        config["project_dir"] = str(StoragePaths.run_root(task_id))
        config["run_name"] = (
            "eval" if entity.task_type == "evaluation" else "train"
        )

        result = await self.runner.run(str(task_id), config)
        entity.config = config
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
        if not result and entity.task_type == "training":
            result = await self._recover_training_result(task_id)
        if not result:
            if not await self.runner.is_running(str(task_id)):
                if self._should_wait_for_result_files(task_id):
                    return entity
                entity.status = TaskStatus.FAILED
                entity.error_message = "训练进程已退出，但未生成结果文件"
                entity.finished_at = datetime.now(timezone.utc)
                return await self.repo.update(entity)
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
        await self._delete_task_artifacts(task_id)
        await self.repo.delete(entity)
        return True

    async def _delete_task_artifacts(self, task_id: uuid.UUID) -> None:
        task_relative_path = self._storage_relative(StoragePaths.task_root(task_id))
        run_relative_path = self._storage_relative(StoragePaths.run_root(task_id))
        await self.storage.delete_dir(task_relative_path)
        await self.storage.delete_dir(run_relative_path)

    async def get_history(self, task_id: uuid.UUID) -> list[dict[str, Any]]:
        try:
            history = await self._load_task_json(task_id, "history.json")
        except OSError:
            return []
        if isinstance(history, list):
            return history
        return []

    async def get_log_content(self, task_id: uuid.UUID, stream: str) -> str:
        if stream not in {"stdout", "stderr"}:
            return ""

        log_path = (
            StoragePaths.task_stdout(task_id)
            if stream == "stdout"
            else StoragePaths.task_stderr(task_id)
        )
        if not log_path.exists():
            return ""

        try:
            return log_path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            return ""

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

    async def get_artifact_path(
        self,
        task_id: uuid.UUID,
        filename: str,
    ) -> Path | None:
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
        if not entity:
            return None
        if entity.status != TaskStatus.COMPLETED:
            entity = await self.sync_result(task_id)
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
            key: result[key]
            for key in (
                "best_epoch",
                "map50",
                "map50_95",
                "precision",
                "recall",
                "train_duration_seconds",
                "train_duration_minutes",
                "weight_size_mb",
                "parameter_count",
                "model_parameters",
            )
            if key in result
        }
        model = MLModel(
            name=f"{entity.name}_model",
            framework=config.get("framework", "ultralytics"),
            model_source="trained",
            status="ready",
            dataset_id=entity.dataset_id,
            metrics=metrics,
        )
        model = await self.model_repo.create(model)

        target_relative = str(Path("models") / str(model.id) / source_path.name)
        source_relative = str(source_path.relative_to(settings.storage_path))
        content = await self.storage.load(source_relative)
        await self.storage.save(target_relative, content)

        model.weight_path = str(StoragePaths.model_dir(model.id) / source_path.name)
        model.model_size_mb = float(
            result.get("weight_size_mb") or round(len(content) / (1024 * 1024), 2)
        )
        parameters = result.get("model_parameters")
        if isinstance(parameters, str) and parameters and parameters != "--":
            model.parameters = parameters
        return await self.model_repo.update(model)

    async def _recover_training_result(
        self,
        task_id: uuid.UUID,
    ) -> dict[str, Any] | None:
        run_dir = StoragePaths.task_run_dir(task_id, "train")
        best_weight = run_dir / "weights" / "best.pt"
        results_csv = run_dir / "results.csv"

        if not best_weight.exists() or not results_csv.exists():
            return None

        metrics = self._read_training_metrics_from_csv(results_csv)
        if metrics is None:
            return None

        if await self._read_task_progress(task_id) < 100:
            return None

        return {
            "status": TaskStatus.COMPLETED.value,
            **metrics,
            "weight_path": str(best_weight),
            "weight_size_mb": round(best_weight.stat().st_size / (1024 * 1024), 2),
        }

    async def _read_task_progress(self, task_id: uuid.UUID) -> int:
        progress_payload = await self._load_task_json(task_id, "progress.json")
        if not isinstance(progress_payload, dict):
            return 0
        try:
            return int(progress_payload.get("progress", 0))
        except (TypeError, ValueError):
            return 0

    def _should_wait_for_result_files(self, task_id: uuid.UUID) -> bool:
        now = time.time()
        candidate_paths = [
            StoragePaths.task_stdout(task_id),
            StoragePaths.task_stderr(task_id),
            StoragePaths.task_progress(task_id),
            StoragePaths.task_run_dir(task_id, "train") / "results.csv",
            StoragePaths.task_run_dir(task_id, "train") / "weights" / "best.pt",
        ]

        for path in candidate_paths:
            try:
                if not path.exists():
                    continue
                modified_seconds = now - path.stat().st_mtime
                if modified_seconds <= _RESULT_SYNC_GRACE_SECONDS:
                    return True
            except OSError:
                continue

        return False

    async def _load_task_json(
        self,
        task_id: uuid.UUID,
        filename: str,
    ) -> dict[str, Any] | list[dict[str, Any]] | None:
        relative_path = self._storage_relative(
            StoragePaths.task_root(task_id) / filename
        )
        if not await self.storage.exists(relative_path):
            return None
        try:
            content = await self.storage.load(relative_path)
            payload = json.loads(content)
        except (ValueError, OSError):
            return None
        if isinstance(payload, dict):
            return payload
        if isinstance(payload, list):
            return payload
        return None

    @staticmethod
    def _storage_relative(path: Path) -> str:
        return str(path.relative_to(settings.storage_path))

    @staticmethod
    def _read_training_metrics_from_csv(results_csv: Path) -> dict[str, float | int] | None:
        try:
            with results_csv.open("r", encoding="utf-8", newline="") as fp:
                rows = list(DictReader(fp))
        except OSError:
            return None

        if not rows:
            return None

        score_key = "metrics/mAP50-95(B)"
        if score_key not in rows[0]:
            score_key = "metrics/mAP50(B)"

        final_row: dict[str, str] | None = None
        best_score: float | None = None

        for row in rows:
            try:
                score = float(row.get(score_key, 0) or 0)
            except (TypeError, ValueError):
                continue
            if best_score is None or score > best_score:
                best_score = score
                final_row = row

        if not final_row:
            return None

        def _to_float(key: str) -> float:
            value = final_row.get(key, 0)
            try:
                return float(value)
            except (TypeError, ValueError):
                return 0.0

        return {
            "best_epoch": int(_to_float("epoch")),
            "map50": _to_float("metrics/mAP50(B)"),
            "map50_95": _to_float("metrics/mAP50-95(B)"),
            "precision": _to_float("metrics/precision(B)"),
            "recall": _to_float("metrics/recall(B)"),
        }

    async def _require_ready_training_export(
        self, dataset_export_id: uuid.UUID | None
    ) -> DatasetExport:
        if not dataset_export_id:
            raise ValidationError("训练任务必须选择训练输入导出记录")

        export = await self.export_repo.get_by_id(dataset_export_id)
        if not export:
            raise NotFoundError("训练输入导出记录不存在")
        if export.status != "success":
            raise ValidationError(
                "训练输入导出记录尚未准备完成，请选择已成功导出的记录"
            )
        if not export.data_yaml_path:
            raise ValidationError("训练输入导出记录缺少 dataset.yaml，无法启动训练")
        return export

    async def _get_dataset_version_or_raise(
        self, version_id: uuid.UUID
    ) -> DatasetVersion:
        version = await self.version_repo.get_by_id(version_id)
        if not version:
            raise NotFoundError("训练输入对应的数据集版本不存在")
        return version

    async def _build_training_task_config(
        self,
        config: dict[str, Any],
        export: DatasetExport,
        version: DatasetVersion,
        model_id: uuid.UUID | None,
    ) -> dict[str, Any]:
        enriched = dict(config)
        dataset = await self.dataset_repo.get_by_id(export.dataset_id)
        model = await self.model_repo.get_by_id(model_id) if model_id else None

        summary = self._read_export_summary(export.validation_summary)
        split_counts = self._read_number_map(summary.get("split_counts"))
        class_names = self._read_class_names(version.label_schema_snapshot)

        enriched.update(
            {
                "training_input_mode": "dataset_export",
                "dataset_id": str(export.dataset_id),
                "dataset_version_id": str(export.dataset_version_id),
                "dataset_export_id": str(export.id),
                "dataset_name": dataset.name if dataset else "--",
                "dataset_version_name": version.version_name,
                "dataset_export_name": export.export_name,
                "export_format": export.export_format,
                "data_yaml_path": export.data_yaml_path or "",
                "export_created_at": export.created_at.isoformat(),
                "export_notes": self._read_export_notes(export),
                "split_counts": split_counts,
                "split_summary": self._format_split_summary(split_counts),
                "class_count": int(summary.get("class_count") or len(class_names)),
                "class_names": class_names,
                "image_count": int(summary.get("image_count") or 0),
                "box_count": int(summary.get("box_count") or 0),
                "model_name": model.name if model else enriched.get("model_name", "--"),
                "model_version": (
                    model.version
                    if model and model.version
                    else enriched.get("model_version", "--")
                ),
            }
        )
        return enriched

    @staticmethod
    def _read_export_summary(
        validation_summary: dict[str, Any] | None,
    ) -> dict[str, Any]:
        if not validation_summary:
            return {}
        summary = validation_summary.get("summary")
        return summary if isinstance(summary, dict) else {}

    @staticmethod
    def _read_export_notes(export: DatasetExport) -> str:
        split_config = export.split_config
        if isinstance(split_config, Mapping):
            notes = split_config.get("notes")
            if isinstance(notes, str) and notes:
                return notes
        return "--"

    @staticmethod
    def _read_number_map(value: Any) -> dict[str, int]:
        if not isinstance(value, Mapping):
            return {}
        return {str(key): int(raw_value or 0) for key, raw_value in value.items()}

    @staticmethod
    def _read_class_names(label_schema_snapshot: Any) -> list[str]:
        if not isinstance(label_schema_snapshot, list):
            return []
        class_names: list[str] = []
        for item in label_schema_snapshot:
            if not isinstance(item, Mapping):
                continue
            name = item.get("name")
            if isinstance(name, str) and name:
                class_names.append(name)
        return class_names

    @staticmethod
    def _format_split_summary(split_counts: dict[str, int]) -> str:
        if not split_counts:
            return "--"
        ordered = ["train", "val", "test"]
        parts = [
            f"{split} {split_counts[split]}"
            for split in ordered
            if split in split_counts
        ]
        if not parts:
            parts = [f"{split} {count}" for split, count in split_counts.items()]
        return " / ".join(parts)
