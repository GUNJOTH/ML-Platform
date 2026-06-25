from __future__ import annotations

import asyncio
import json
import re
import shutil
import uuid
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.dataset_files import extract_class_names, read_yaml_payload, resolve_storage_path
from app.core.storage.factory import get_storage
from app.core.storage.paths import StoragePaths
from app.exceptions import NotFoundError, ValidationError
from app.models.annotation import Annotation
from app.models.dataset import Dataset, Image, Label
from app.models.dataset_version import DatasetExport, DatasetVersion
from app.repositories.annotation import AnnotationRepository
from app.repositories.dataset import DatasetRepository, ImageRepository
from app.repositories.dataset_version import DatasetExportRepository, DatasetVersionRepository
from app.repositories.label import LabelRepository
from app.repositories.task import TaskRepository
from app.schemas.dataset_version import (
    DatasetExportCreate,
    DatasetVersionCreate,
    DatasetVersionValidationIssue,
    DatasetVersionValidationResult,
)


class DatasetVersionService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.dataset_repo = DatasetRepository(session)
        self.image_repo = ImageRepository(session)
        self.label_repo = LabelRepository(session)
        self.annotation_repo = AnnotationRepository(session)
        self.version_repo = DatasetVersionRepository(session)
        self.export_repo = DatasetExportRepository(session)
        self.task_repo = TaskRepository(session)
        self.storage = get_storage()

    async def list_versions(
        self, dataset_id: uuid.UUID | None = None, offset: int = 0, limit: int = 50
    ) -> list[DatasetVersion]:
        if dataset_id:
            return await self.version_repo.list_by_dataset(dataset_id, offset=offset, limit=limit)
        return await self.version_repo.list(offset=offset, limit=limit)

    async def get_version(self, version_id: uuid.UUID) -> DatasetVersion | None:
        return await self.version_repo.get_by_id(version_id)

    async def create_version(self, data: DatasetVersionCreate) -> DatasetVersion:
        dataset = await self.dataset_repo.get_by_id(data.dataset_id)
        if not dataset:
            raise NotFoundError("Dataset not found")

        snapshot = await self._build_snapshot(dataset, include_splits=data.include_splits)
        validation = self._validate_snapshot(snapshot, include_splits=data.include_splits)
        if not validation.passed:
            raise ValidationError(self._build_validation_error_message(validation))

        entity = DatasetVersion(
            dataset_id=data.dataset_id,
            version_name=data.version_name,
            version_code=self._slugify(data.version_name),
            description=data.description,
            status="frozen",
            source_type=data.source_type,
            export_format=data.export_format.lower(),
            include_splits=data.include_splits,
            split_strategy=data.split_strategy,
            split_config=data.split_config or snapshot["split_counts"],
            label_schema_snapshot=snapshot["labels"],
            stats_snapshot=snapshot["stats"],
            validation_summary=validation.model_dump(),
            frozen_at=datetime.now(timezone.utc),
        )
        return await self.version_repo.create(entity)

    async def validate_version_draft(
        self, data: DatasetVersionCreate
    ) -> DatasetVersionValidationResult:
        dataset = await self.dataset_repo.get_by_id(data.dataset_id)
        if not dataset:
            raise NotFoundError("Dataset not found")

        snapshot = await self._build_snapshot(dataset, include_splits=data.include_splits)
        return self._validate_snapshot(snapshot, include_splits=data.include_splits)

    async def validate_version(self, version_id: uuid.UUID) -> DatasetVersionValidationResult:
        version = await self.version_repo.get_by_id(version_id)
        if not version:
            raise NotFoundError("Dataset version not found")

        dataset = await self.dataset_repo.get_by_id(version.dataset_id)
        if not dataset:
            raise NotFoundError("Dataset not found")

        include_splits = version.include_splits or ["train", "val", "test"]
        snapshot = await self._build_snapshot(dataset, include_splits=include_splits)
        result = self._validate_snapshot(snapshot, include_splits=include_splits)
        version.validation_summary = result.model_dump()
        version.status = "frozen" if result.passed else "draft"
        await self.version_repo.update(version)
        return result

    async def list_exports(
        self,
        dataset_id: uuid.UUID | None = None,
        dataset_version_id: uuid.UUID | None = None,
        offset: int = 0,
        limit: int = 50,
    ) -> list[DatasetExport]:
        return await self.export_repo.list_filtered(
            dataset_id=dataset_id,
            dataset_version_id=dataset_version_id,
            offset=offset,
            limit=limit,
        )

    async def get_export(self, export_id: uuid.UUID) -> DatasetExport | None:
        return await self.export_repo.get_by_id(export_id)

    async def create_export(self, data: DatasetExportCreate) -> DatasetExport:
        version = await self.version_repo.get_by_id(data.dataset_version_id)
        if not version:
            raise NotFoundError("Dataset version not found")

        validation = await self.validate_version(version.id)
        entity = DatasetExport(
            dataset_id=version.dataset_id,
            dataset_version_id=version.id,
            export_name=data.export_name,
            export_format=data.export_format.lower(),
            status="pending",
            split_config={"splits": data.splits, "extras": data.extras, "notes": data.notes},
            validation_summary=validation.model_dump(),
        )
        entity = await self.export_repo.create(entity)

        if not validation.passed:
            entity.status = "failed"
            entity.error_message = "Dataset version validation failed"
            return await self.export_repo.update(entity)

        entity.status = "exporting"
        await self.export_repo.update(entity)

        try:
            await self._materialize_yolo_export(entity, version, data)
            entity.status = "success"
            entity.finished_at = datetime.now(timezone.utc)
            return await self.export_repo.update(entity)
        except Exception as exc:
            entity.status = "failed"
            entity.error_message = str(exc)
            entity.finished_at = datetime.now(timezone.utc)
            return await self.export_repo.update(entity)

    async def delete_version(self, version_id: uuid.UUID) -> None:
        version = await self.version_repo.get_by_id(version_id)
        if not version:
            raise NotFoundError("Dataset version not found")

        exports = await self.export_repo.list_filtered(
            dataset_version_id=version_id,
            offset=0,
            limit=100000,
        )
        for export in exports:
            await self._delete_export_entity(export)

        await self._detach_tasks_for_version(version_id)
        await self.version_repo.delete(version)

    async def delete_export(self, export_id: uuid.UUID) -> None:
        export = await self.export_repo.get_by_id(export_id)
        if not export:
            raise NotFoundError("Dataset export not found")
        await self._delete_export_entity(export)

    async def _build_snapshot(
        self, dataset: Dataset, include_splits: list[str] | None
    ) -> dict[str, Any]:
        images = await self.image_repo.list_by_dataset(dataset.id, offset=0, limit=100000)
        labels = await self.label_repo.list_by_dataset(dataset.id)
        annotations = await self.annotation_repo.list_by_dataset(dataset.id)
        valid_splits = set(include_splits or ["train", "val", "test"])

        if labels and annotations:
            return self._build_snapshot_from_database(
                images=images,
                labels=labels,
                annotations=annotations,
                valid_splits=valid_splits,
            )

        yolo_snapshot = self._build_snapshot_from_yolo_files(dataset, valid_splits)
        if yolo_snapshot is not None:
            return yolo_snapshot

        return self._build_snapshot_from_database(
            images=images,
            labels=labels,
            annotations=annotations,
            valid_splits=valid_splits,
        )

    def _build_snapshot_from_database(
        self,
        images: list[Image],
        labels: list[Label],
        annotations: list[Annotation],
        valid_splits: set[str],
    ) -> dict[str, Any]:
        annotations_by_image: dict[uuid.UUID, list[Annotation]] = defaultdict(list)
        for annotation in annotations:
            annotations_by_image[annotation.image_id].append(annotation)

        split_counter: Counter[str] = Counter()
        annotated_image_count = 0
        box_count = 0
        missing_file_count = 0
        class_counter: Counter[str] = Counter()
        label_map = {label.id: label for label in labels}

        for image in images:
            if image.split not in valid_splits:
                continue
            split_counter[image.split] += 1
            image_annotations = annotations_by_image.get(image.id, [])
            if image_annotations:
                annotated_image_count += 1
            box_count += len(image_annotations)
            if not self._resolve_path(image.file_path).exists():
                missing_file_count += 1
            for annotation in image_annotations:
                label = label_map.get(annotation.label_id)
                if label:
                    class_counter[label.name] += 1

        return {
            "labels": [
                {
                    "id": str(label.id),
                    "name": label.name,
                    "color": label.color,
                    "sort_order": label.sort_order,
                }
                for label in labels
            ],
            "stats": {
                "image_count": sum(split_counter.values()),
                "annotated_image_count": annotated_image_count,
                "unannotated_image_count": max(sum(split_counter.values()) - annotated_image_count, 0),
                "box_count": box_count,
                "class_count": len(labels),
                "class_distribution": dict(class_counter),
                "missing_file_count": missing_file_count,
                "split_counts": dict(split_counter),
            },
            "split_counts": dict(split_counter),
            "images": images,
            "annotations_by_image": annotations_by_image,
            "source_mode": "database",
        }

    def _build_snapshot_from_yolo_files(
        self, dataset: Dataset, valid_splits: set[str]
    ) -> dict[str, Any] | None:
        if not dataset.storage_path:
            return None

        data_yaml_path = resolve_storage_path(dataset.storage_path)
        if not data_yaml_path.exists():
            return None

        payload = read_yaml_payload(data_yaml_path)
        class_names = extract_class_names(payload)
        path_root = payload.get("path")
        dataset_root = (
            resolve_storage_path(path_root)
            if isinstance(path_root, str) and path_root
            else data_yaml_path.parent
        )

        split_counter: Counter[str] = Counter()
        class_counter: Counter[str] = Counter()
        box_count = 0
        annotated_image_count = 0
        unannotated_image_count = 0
        missing_file_count = 0
        yolo_labels_by_key: dict[tuple[str, str], list[str]] = {}
        yolo_image_paths_by_key: dict[tuple[str, str], Path] = {}
        issues: list[dict[str, str]] = []

        for split in ("train", "val", "test"):
            if split not in valid_splits:
                continue
            split_ref = payload.get(split)
            if not isinstance(split_ref, str) or not split_ref:
                continue

            image_dir = self._resolve_dataset_subpath(dataset_root, split_ref)
            label_dir = self._infer_label_dir(dataset_root, split_ref)
            if not image_dir.exists():
                continue

            for image_path in self._iter_image_files(image_dir):
                split_counter[split] += 1
                stem = image_path.stem
                yolo_image_paths_by_key[(split, stem)] = image_path
                label_path = label_dir / f"{stem}.txt"
                lines: list[str] = []
                if label_path.exists():
                    lines = [
                        line.strip()
                        for line in label_path.read_text(encoding="utf-8").splitlines()
                        if line.strip()
                    ]
                if lines:
                    annotated_image_count += 1
                else:
                    unannotated_image_count += 1
                yolo_labels_by_key[(split, stem)] = lines

                for line in lines:
                    parts = line.split()
                    if len(parts) != 5:
                        issues.append(
                            {
                                "code": "INVALID_YOLO_ROW",
                                "message": f"{label_path.name} 中存在格式错误的标注行",
                                "level": "error",
                            }
                        )
                        continue
                    try:
                        class_index = int(float(parts[0]))
                        coords = [float(value) for value in parts[1:]]
                    except ValueError:
                        issues.append(
                            {
                                "code": "INVALID_YOLO_VALUE",
                                "message": f"{label_path.name} 中存在非数字标注值",
                                "level": "error",
                            }
                        )
                        continue
                    if class_index < 0 or class_index >= len(class_names):
                        issues.append(
                            {
                                "code": "INVALID_CLASS_ID",
                                "message": f"{label_path.name} 中引用的类别索引 {class_index} 超出范围",
                                "level": "error",
                            }
                        )
                        continue
                    if any(value < 0 or value > 1 for value in coords):
                        issues.append(
                            {
                                "code": "INVALID_YOLO_COORD",
                                "message": f"{label_path.name} 中存在超出 0-1 范围的坐标值",
                                "level": "error",
                            }
                        )
                        continue
                    class_counter[class_names[class_index]] += 1
                    box_count += 1

                if not image_path.exists():
                    missing_file_count += 1

        return {
            "labels": [
                {
                    "id": str(index),
                    "name": name,
                    "color": "#FF0000",
                    "sort_order": index,
                }
                for index, name in enumerate(class_names)
            ],
            "stats": {
                "image_count": sum(split_counter.values()),
                "annotated_image_count": annotated_image_count,
                "unannotated_image_count": unannotated_image_count,
                "box_count": box_count,
                "class_count": len(class_names),
                "class_distribution": dict(class_counter),
                "missing_file_count": missing_file_count,
                "split_counts": dict(split_counter),
            },
            "split_counts": dict(split_counter),
            "images": [],
            "annotations_by_image": {},
            "source_mode": "yolo_files",
            "yolo_labels_by_key": yolo_labels_by_key,
            "yolo_image_paths_by_key": yolo_image_paths_by_key,
            "yolo_issues": issues,
        }

    def _validate_snapshot(
        self, snapshot: dict[str, Any], include_splits: list[str]
    ) -> DatasetVersionValidationResult:
        errors: list[DatasetVersionValidationIssue] = []
        warnings: list[DatasetVersionValidationIssue] = []
        stats = snapshot["stats"]
        split_counts: dict[str, int] = snapshot["split_counts"]
        labels = snapshot["labels"]

        if stats["image_count"] == 0:
            errors.append(self._issue("EMPTY_DATASET", "当前版本范围内没有可导出的图片", "error"))
        if not labels:
            errors.append(self._issue("EMPTY_LABELS", "当前数据集没有可用的类别定义", "error"))
        if stats["box_count"] == 0:
            errors.append(self._issue("EMPTY_ANNOTATIONS", "当前版本范围内没有有效标注框", "error"))
        if stats["missing_file_count"] > 0:
            errors.append(
                self._issue(
                    "MISSING_IMAGE_FILES",
                    f"有 {stats['missing_file_count']} 张图片在磁盘中不存在",
                    "error",
                )
            )

        for issue in snapshot.get("yolo_issues", []):
            target = errors if issue["level"] == "error" else warnings
            target.append(self._issue(issue["code"], issue["message"], issue["level"]))

        for split in include_splits:
            if split_counts.get(split, 0) == 0:
                errors.append(
                    self._issue(
                        "EMPTY_SPLIT",
                        f"你选择了 {split} 划分，但该划分下没有任何图片",
                        "error",
                    )
                )

        if stats["unannotated_image_count"] > 0:
            warnings.append(
                self._issue(
                    "UNANNOTATED_IMAGES",
                    f"有 {stats['unannotated_image_count']} 张图片还没有标注",
                    "warning",
                )
            )

        for class_name, count in stats["class_distribution"].items():
            if count < 5:
                warnings.append(
                    self._issue(
                        "LOW_CLASS_SAMPLES",
                        f"类别“{class_name}”当前只有 {count} 个标注样本",
                        "warning",
                    )
                )

        return DatasetVersionValidationResult(
            passed=not errors,
            errors=errors,
            warnings=warnings,
            summary={
                "image_count": stats["image_count"],
                "annotated_image_count": stats["annotated_image_count"],
                "box_count": stats["box_count"],
                "split_counts": split_counts,
                "class_distribution": stats["class_distribution"],
            },
        )

    async def _materialize_yolo_export(
        self, export_entity: DatasetExport, version: DatasetVersion, data: DatasetExportCreate
    ) -> None:
        if data.export_format.lower() != "yolo":
            raise ValueError("Only YOLO export is supported in phase 1")

        dataset = await self.dataset_repo.get_by_id(version.dataset_id)
        if not dataset:
            raise NotFoundError("Dataset not found")

        snapshot = await self._build_snapshot(dataset, include_splits=data.splits)
        export_root = StoragePaths.export_root(export_entity.id)
        if export_root.exists():
            await asyncio.to_thread(shutil.rmtree, export_root, True)

        for split in data.splits:
            (export_root / "images" / split).mkdir(parents=True, exist_ok=True)
            (export_root / "labels" / split).mkdir(parents=True, exist_ok=True)

        labels = version.label_schema_snapshot or snapshot["labels"]
        split_counts: Counter[str] = Counter()

        if snapshot.get("source_mode") == "yolo_files":
            image_paths: dict[tuple[str, str], Path] = snapshot.get("yolo_image_paths_by_key", {})
            label_lines: dict[tuple[str, str], list[str]] = snapshot.get("yolo_labels_by_key", {})
            for (split, stem), source_path in image_paths.items():
                if split not in data.splits or not source_path.exists():
                    continue
                split_counts[split] += 1
                target_image = export_root / "images" / split / source_path.name
                await asyncio.to_thread(shutil.copy2, source_path, target_image)
                label_path = export_root / "labels" / split / f"{stem}.txt"
                label_path.write_text("\n".join(label_lines.get((split, stem), [])), encoding="utf-8")
        else:
            label_index = {item["id"]: idx for idx, item in enumerate(labels)}
            images: list[Image] = snapshot["images"]
            annotations_by_image: dict[uuid.UUID, list[Annotation]] = snapshot["annotations_by_image"]

            for image in images:
                if image.split not in data.splits:
                    continue

                source_path = resolve_storage_path(image.file_path)
                if not source_path.exists():
                    continue

                split_counts[image.split] += 1
                target_image = export_root / "images" / image.split / source_path.name
                await asyncio.to_thread(shutil.copy2, source_path, target_image)

                label_path = export_root / "labels" / image.split / f"{Path(source_path.name).stem}.txt"
                lines: list[str] = []
                for annotation in annotations_by_image.get(image.id, []):
                    yolo_line = self._to_yolo_line(annotation, image, label_index)
                    if yolo_line:
                        lines.append(yolo_line)
                label_path.write_text("\n".join(lines), encoding="utf-8")

        class_names = [item["name"] for item in labels]
        data_yaml_path = export_root / "dataset.yaml"
        yaml_payload = {
            "path": str(export_root),
            "train": "images/train" if "train" in data.splits else "",
            "val": "images/val" if "val" in data.splits else "",
            "test": "images/test" if "test" in data.splits else "",
            "names": class_names,
            "nc": len(class_names),
        }
        data_yaml_path.write_text(yaml.safe_dump(yaml_payload, sort_keys=False), encoding="utf-8")

        manifest_path = export_root / "manifest.json"
        manifest_path.write_text(
            json.dumps(
                {
                    "dataset_id": str(dataset.id),
                    "dataset_version_id": str(version.id),
                    "dataset_export_id": str(export_entity.id),
                    "version_name": version.version_name,
                    "export_name": export_entity.export_name,
                    "format": data.export_format.lower(),
                    "splits": dict(split_counts),
                    "classes": class_names,
                    "generated_at": datetime.now(timezone.utc).isoformat(),
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )

        validation_path = export_root / "validation.json"
        validation_path.write_text(
            json.dumps(export_entity.validation_summary or {}, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        export_entity.output_path = str(export_root)
        export_entity.data_yaml_path = str(data_yaml_path)
        export_entity.manifest_path = str(manifest_path)

    async def _delete_export_entity(self, export: DatasetExport) -> None:
        await self._detach_tasks_for_export(export.id)
        await self._delete_export_artifacts(export)
        await self.export_repo.delete(export)

    async def _delete_export_artifacts(self, export: DatasetExport) -> None:
        export_dir = StoragePaths.export_root(export.id)
        if export_dir.exists():
            await self.storage.delete_dir(str(export_dir.relative_to(settings.storage_path)))

    async def _detach_tasks_for_export(self, export_id: uuid.UUID) -> None:
        tasks = await self.task_repo.list_by_dataset_export(str(export_id))
        for task in tasks:
            task.dataset_export_id = None
            await self.task_repo.update(task)

    async def _detach_tasks_for_version(self, version_id: uuid.UUID) -> None:
        tasks = await self.task_repo.list_by_dataset_version(str(version_id))
        for task in tasks:
            task.dataset_version_id = None
            await self.task_repo.update(task)

    @staticmethod
    def _issue(code: str, message: str, level: str) -> DatasetVersionValidationIssue:
        return DatasetVersionValidationIssue(code=code, message=message, level=level)

    @staticmethod
    def _build_validation_error_message(result: DatasetVersionValidationResult) -> str:
        if not result.errors:
            return "版本校验未通过，请先处理校验问题"
        if len(result.errors) == 1:
            return f"版本校验未通过：{result.errors[0].message}"
        return f"版本校验未通过：{result.errors[0].message}，另有 {len(result.errors) - 1} 个问题"

    @staticmethod
    def _slugify(value: str) -> str:
        slug = re.sub(r"[^a-zA-Z0-9]+", "_", value).strip("_").lower()
        return slug or "dataset_version"

    @classmethod
    def _resolve_dataset_subpath(cls, dataset_root: Path, path_str: str) -> Path:
        path = Path(path_str)
        if path.is_absolute():
            return path
        return dataset_root / path

    @classmethod
    def _infer_label_dir(cls, dataset_root: Path, image_ref: str) -> Path:
        image_path = Path(image_ref)
        parts = list(image_path.parts)
        if "images" in parts:
            parts[parts.index("images")] = "labels"
            return cls._resolve_dataset_subpath(dataset_root, str(Path(*parts)))
        return cls._resolve_dataset_subpath(dataset_root, str(Path("labels") / image_path.name))

    @staticmethod
    def _iter_image_files(image_dir: Path) -> list[Path]:
        image_exts = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
        return sorted(
            [path for path in image_dir.rglob("*") if path.is_file() and path.suffix.lower() in image_exts]
        )

    @staticmethod
    def _to_yolo_line(
        annotation: Annotation, image: Image, label_index: dict[str, int]
    ) -> str | None:
        payload = annotation.data or {}
        x = payload.get("x")
        y = payload.get("y")
        width = payload.get("width")
        height = payload.get("height")
        if None in (x, y, width, height):
            return None
        if image.width <= 0 or image.height <= 0:
            return None

        class_id = label_index.get(str(annotation.label_id))
        if class_id is None:
            return None

        x_center = (float(x) + float(width) / 2) / float(image.width)
        y_center = (float(y) + float(height) / 2) / float(image.height)
        norm_width = float(width) / float(image.width)
        norm_height = float(height) / float(image.height)
        if min(x_center, y_center, norm_width, norm_height) < 0:
            return None

        return (
            f"{class_id} "
            f"{x_center:.6f} {y_center:.6f} {norm_width:.6f} {norm_height:.6f}"
        )

