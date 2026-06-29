import asyncio
import shutil
import uuid
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dataset_files import (
    build_yolo_label_file_index,
    extract_class_names,
    read_image_size,
    read_yaml_payload,
    resolve_dataset_root_from_image_path,
    resolve_effective_split_from_image_path,
    resolve_storage_path,
    resolve_yolo_label_path,
)
from app.core.storage.paths import StoragePaths
from app.exceptions import NotFoundError
from app.models.annotation import Annotation
from app.models.dataset import Dataset, Image, Label
from app.repositories.annotation import AnnotationRepository
from app.repositories.dataset import DatasetRepository, ImageRepository
from app.repositories.label import LabelRepository


class AnnotationExportService:
    def __init__(self, session: AsyncSession) -> None:
        self.dataset_repo = DatasetRepository(session)
        self.image_repo = ImageRepository(session)
        self.label_repo = LabelRepository(session)
        self.annotation_repo = AnnotationRepository(session)

    async def export_dataset(
        self,
        source_dataset_id: uuid.UUID,
        annotations: dict[str, list[dict[str, Any]]],
        mode: str = "new",
    ) -> Dataset:
        source = await self.dataset_repo.get_by_id(source_dataset_id)
        if not source:
            raise NotFoundError("Source dataset not found")

        labels = await self.label_repo.list_by_dataset(source_dataset_id)
        existing_annotations = await self.annotation_repo.list_by_dataset(source_dataset_id)
        class_names = self._resolve_class_names(source, labels)
        label_map = self._build_label_map(labels, class_names)
        images = await self.image_repo.list_by_dataset(
            source_dataset_id, offset=0, limit=10000
        )
        image_lookup = {str(img.id): img for img in images}
        resolved_splits = {
            str(img.id): self._resolve_effective_split(img)
            for img in images
        }
        annotation_overrides = self._normalize_annotation_payload(annotations)
        annotations_by_image = self._group_annotations_by_image(existing_annotations)
        source_label_index = self._build_source_label_index(source, images)
        export_items = self._build_export_items(
            images=images,
            annotation_overrides=annotation_overrides,
            annotations_by_image=annotations_by_image,
            label_map=label_map,
            resolved_splits=resolved_splits,
            source_label_index=source_label_index,
        )

        staging_dir: Path | None = None
        if mode == "overwrite":
            target_dataset = source
            target_dir = self._resolve_target_dir(source, source_dataset_id)
            staging_dir = await self._stage_export_items_for_overwrite(export_items, target_dir)
            await self._reset_target_dataset(target_dataset.id, target_dir)
        else:
            target_dataset = await self._create_new_dataset(source, labels, class_names)
            target_dir = StoragePaths.dataset_root(target_dataset.id)
            target_dir.mkdir(parents=True, exist_ok=True)
        try:
            split_counts = await self._materialize_export_items(
                export_items=export_items,
                target_id=target_dataset.id,
                target_dir=target_dir,
            )

            yaml_path = self._write_data_yaml(target_dir, class_names)
            self._validate_export_layout(target_dir, split_counts)
            self._clear_label_caches(target_dir)
        finally:
            if staging_dir and staging_dir.exists():
                await asyncio.to_thread(shutil.rmtree, staging_dir, True)

        target_dataset.storage_path = str(yaml_path)
        target_dataset.status = "annotated"
        target_dataset.num_classes = len(class_names)
        target_dataset.train_count = split_counts.get("train", 0)
        target_dataset.val_count = split_counts.get("val", 0)
        target_dataset.test_count = split_counts.get("test", 0)

        return await self.dataset_repo.update(target_dataset)

    @staticmethod
    def _resolve_target_dir(source: Dataset, dataset_id: uuid.UUID) -> Path:
        if source.storage_path:
            return resolve_storage_path(source.storage_path).parent
        return StoragePaths.dataset_root(dataset_id)

    def _resolve_class_names(self, source: Dataset, labels: list[Label]) -> list[str]:
        if labels:
            return [lb.name for lb in labels]

        yaml_path = self._resolve_source_yaml(source)
        if yaml_path and yaml_path.exists():
            try:
                payload = read_yaml_payload(yaml_path)
            except Exception:
                payload = {}
            return extract_class_names(payload)

        return []

    def _build_label_map(
        self, labels: list[Label], class_names: list[str]
    ) -> dict[str, int]:
        if labels:
            return {str(lb.id): idx for idx, lb in enumerate(labels)}

        return {str(index): index for index, _ in enumerate(class_names)}

    @staticmethod
    def _resolve_source_yaml(source: Dataset) -> Path | None:
        if not source.storage_path:
            return None
        return resolve_storage_path(source.storage_path)

    async def _create_new_dataset(
        self,
        source: Dataset,
        labels: list[Label],
        class_names: list[str],
    ) -> Dataset:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        new_dataset = Dataset(
            name=f"{source.name}_{timestamp}",
            description=f"Annotated from {source.name}",
            data_type=source.data_type,
            num_classes=len(class_names),
            train_count=source.train_count,
            val_count=source.val_count,
            test_count=source.test_count,
        )
        created = await self.dataset_repo.create(new_dataset)

        label_specs = self._build_export_labels(labels, class_names)
        for idx, label_spec in enumerate(label_specs):
            await self.label_repo.create(
                Label(
                    dataset_id=created.id,
                    name=label_spec["name"],
                    color=label_spec["color"],
                    sort_order=idx,
                )
            )

        return created

    @staticmethod
    def _build_export_labels(
        labels: list[Label],
        class_names: list[str],
    ) -> list[dict[str, str]]:
        if labels:
            return [
                {
                    "name": label.name,
                    "color": label.color or "#FF0000",
                }
                for label in labels
            ]

        return [
            {
                "name": class_name,
                "color": "#FF0000",
            }
            for class_name in class_names
        ]

    @staticmethod
    def _resolve_image_path(path_str: str) -> Path:
        return resolve_storage_path(path_str)

    @classmethod
    def _resolve_image_size(cls, image: Image) -> tuple[int, int]:
        if image.width > 0 and image.height > 0:
            return image.width, image.height

        image_path = cls._resolve_image_path(image.file_path)
        if not image_path.exists():
            return 0, 0

        return read_image_size(image_path)

    def _build_export_items(
        self,
        *,
        images: list[Image],
        annotation_overrides: dict[str, list[dict[str, Any]]],
        annotations_by_image: dict[uuid.UUID, list[Annotation]],
        label_map: dict[str, int],
        resolved_splits: dict[str, str],
        source_label_index: dict[str, list[Path]],
    ) -> list[dict[str, Any]]:
        export_items: list[dict[str, Any]] = []
        for image in images:
            image_id = str(image.id)
            target_split = resolved_splits.get(image_id, image.split)
            label_lines = self._resolve_label_lines_for_image(
                image=image,
                image_id=image_id,
                annotation_overrides=annotation_overrides,
                annotations_by_image=annotations_by_image,
                label_map=label_map,
                source_label_index=source_label_index,
            )
            export_items.append(
                {
                    "image": image,
                    "source_path": self._resolve_image_path(image.file_path),
                    "target_split": target_split,
                    "label_lines": label_lines,
                    "annotation_status": "annotated" if label_lines else "unannotated",
                }
            )
        return export_items

    def _resolve_label_lines_for_image(
        self,
        *,
        image: Image,
        image_id: str,
        annotation_overrides: dict[str, list[dict[str, Any]]],
        annotations_by_image: dict[uuid.UUID, list[Annotation]],
        label_map: dict[str, int],
        source_label_index: dict[str, list[Path]],
    ) -> list[str]:
        if image_id in annotation_overrides:
            return self._build_label_lines_from_boxes(
                image=image,
                boxes=annotation_overrides[image_id],
                label_map=label_map,
            )

        image_annotations = annotations_by_image.get(image.id, [])
        if image_annotations:
            return self._build_label_lines_from_annotations(
                image=image,
                annotations=image_annotations,
                label_map=label_map,
            )

        return self._read_existing_label_lines(image, source_label_index)

    def _build_label_lines_from_boxes(
        self,
        *,
        image: Image,
        boxes: list[dict[str, Any]],
        label_map: dict[str, int],
    ) -> list[str]:
        img_w, img_h = self._resolve_image_size(image)
        if img_w <= 0 or img_h <= 0:
            return []

        lines: list[str] = []
        for box in boxes:
            bbox = box.get("bbox")
            label_id = box.get("label_id")
            if not isinstance(bbox, dict) or not isinstance(label_id, str):
                continue
            lines.append(
                self._bbox_to_yolo_line(
                    self._resolve_box_class_index(label_id, label_map),
                    bbox,
                    img_w,
                    img_h,
                )
            )
        return lines

    def _build_label_lines_from_annotations(
        self,
        *,
        image: Image,
        annotations: list[Annotation],
        label_map: dict[str, int],
    ) -> list[str]:
        img_w, img_h = self._resolve_image_size(image)
        if img_w <= 0 or img_h <= 0:
            return []

        lines: list[str] = []
        for annotation in annotations:
            payload = annotation.data or {}
            if not isinstance(payload, dict):
                continue
            class_idx = label_map.get(str(annotation.label_id))
            if class_idx is None:
                continue
            if not {"x", "y", "width", "height"}.issubset(payload):
                continue
            lines.append(self._bbox_to_yolo_line(class_idx, payload, img_w, img_h))
        return lines

    def _read_existing_label_lines(
        self,
        image: Image,
        source_label_index: dict[str, list[Path]],
    ) -> list[str]:
        image_path = self._resolve_image_path(image.file_path)
        if not image_path.exists():
            return []

        dataset_root = self._resolve_source_dataset_root_from_image(image)
        label_path = resolve_yolo_label_path(
            dataset_root,
            image_path,
            image_split=self._resolve_effective_split(image),
            label_index=source_label_index,
        )
        if label_path is None or not label_path.exists():
            return []

        return [
            line.strip()
            for line in label_path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]

    async def _materialize_export_items(
        self,
        *,
        export_items: list[dict[str, Any]],
        target_id: uuid.UUID,
        target_dir: Path,
    ) -> Counter[str]:
        split_counts: Counter[str] = Counter()
        for item in export_items:
            image = item["image"]
            source_path = Path(str(item["source_path"]))
            target_split = str(item["target_split"])
            label_lines = list(item["label_lines"])
            annotation_status = str(item["annotation_status"])

            if not source_path.exists():
                continue

            image_dir = target_dir / "images" / target_split
            label_dir = target_dir / "labels" / target_split
            image_dir.mkdir(parents=True, exist_ok=True)
            label_dir.mkdir(parents=True, exist_ok=True)

            dest_path = image_dir / image.filename
            await asyncio.to_thread(shutil.copy2, str(source_path), str(dest_path))

            label_path = label_dir / f"{Path(image.filename).stem}.txt"
            label_path.write_text("\n".join(label_lines), encoding="utf-8")

            split_counts[target_split] += 1
            await self.image_repo.create(
                Image(
                    dataset_id=target_id,
                    filename=image.filename,
                    file_path=str(dest_path),
                    split=target_split,
                    width=image.width,
                    height=image.height,
                    annotation_status=annotation_status,
                )
            )
        return split_counts

    async def _reset_target_dataset(self, dataset_id: uuid.UUID, target_dir: Path) -> None:
        existing_images = await self.image_repo.list_by_dataset(
            dataset_id,
            offset=0,
            limit=100000,
        )
        for image in existing_images:
            await self.image_repo.delete(image)

        for folder_name in ("images", "labels"):
            folder_path = target_dir / folder_name
            if folder_path.exists():
                await asyncio.to_thread(shutil.rmtree, folder_path, True)

        data_yaml_path = target_dir / "data.yaml"
        if data_yaml_path.exists():
            data_yaml_path.unlink()

        target_dir.mkdir(parents=True, exist_ok=True)

    async def _stage_export_items_for_overwrite(
        self,
        export_items: list[dict[str, Any]],
        target_dir: Path,
    ) -> Path | None:
        staging_dir = target_dir.parent / f".annotation_export_stage_{uuid.uuid4().hex}"
        staged_any = False
        resolved_target_dir = target_dir.resolve()
        for item in export_items:
            source_path = Path(str(item["source_path"]))
            if not source_path.exists():
                continue
            try:
                source_path.resolve().relative_to(resolved_target_dir)
            except ValueError:
                continue

            staging_dir.mkdir(parents=True, exist_ok=True)
            staged_path = staging_dir / source_path.name
            await asyncio.to_thread(shutil.copy2, str(source_path), str(staged_path))
            item["source_path"] = staged_path
            staged_any = True

        return staging_dir if staged_any else None

    def _validate_export_layout(self, target_dir: Path, split_counts: Counter[str]) -> None:
        for split, count in split_counts.items():
            if count <= 0:
                continue
            image_stems = {
                path.stem
                for path in (target_dir / "images" / split).glob("*")
                if path.is_file()
            }
            label_stems = {
                path.stem
                for path in (target_dir / "labels" / split).glob("*.txt")
                if path.is_file()
            }
            if image_stems != label_stems:
                missing_labels = sorted(image_stems - label_stems)
                orphan_labels = sorted(label_stems - image_stems)
                problems: list[str] = []
                if missing_labels:
                    problems.append(f"{split} 缺少标签: {', '.join(missing_labels[:5])}")
                if orphan_labels:
                    problems.append(f"{split} 存在孤立标签: {', '.join(orphan_labels[:5])}")
                raise ValueError("导出结果不一致，" + "；".join(problems))

    def _clear_label_caches(self, target_dir: Path) -> None:
        label_root = target_dir / "labels"
        if not label_root.exists():
            return
        for cache_path in label_root.rglob("*.cache"):
            cache_path.unlink(missing_ok=True)

    def _build_source_label_index(
        self,
        source: Dataset,
        images: list[Image],
    ) -> dict[str, list[Path]]:
        dataset_root = self._resolve_source_dataset_root(source, images)
        return build_yolo_label_file_index(dataset_root)

    def _resolve_source_dataset_root(self, source: Dataset, images: list[Image]) -> Path:
        if source.storage_path:
            return resolve_storage_path(source.storage_path).parent
        for image in images:
            image_path = self._resolve_image_path(image.file_path)
            if image_path.exists():
                return resolve_dataset_root_from_image_path(image_path)
        return StoragePaths.dataset_root(source.id)

    def _resolve_source_dataset_root_from_image(self, image: Image) -> Path:
        image_path = self._resolve_image_path(image.file_path)
        if image_path.exists():
            return resolve_dataset_root_from_image_path(image_path)
        return StoragePaths.dataset_root(image.dataset_id)

    @staticmethod
    def _normalize_annotation_payload(
        annotations: dict[str, list[dict[str, Any]]] | None,
    ) -> dict[str, list[dict[str, Any]]]:
        if not isinstance(annotations, dict):
            return {}
        normalized: dict[str, list[dict[str, Any]]] = {}
        for image_id, boxes in annotations.items():
            if not isinstance(image_id, str) or not isinstance(boxes, list):
                continue
            normalized[image_id] = [
                box for box in boxes
                if isinstance(box, dict)
            ]
        return normalized

    @staticmethod
    def _group_annotations_by_image(
        annotations: list[Annotation],
    ) -> dict[uuid.UUID, list[Annotation]]:
        grouped: dict[uuid.UUID, list[Annotation]] = {}
        for annotation in annotations:
            grouped.setdefault(annotation.image_id, []).append(annotation)
        return grouped

    def _resolve_effective_split(self, image: Image) -> str:
        image_path = self._resolve_image_path(image.file_path)
        if image_path.exists():
            return resolve_effective_split_from_image_path(image_path, image.split)
        return image.split

    @staticmethod
    def _resolve_box_class_index(label_id: str, label_map: dict[str, int]) -> int:
        if label_id in label_map:
            return label_map[label_id]
        if label_id.isdigit():
            return int(label_id)
        return 0

    @staticmethod
    def _bbox_to_yolo_line(
        class_idx: int, bbox: dict[str, float], img_w: int, img_h: int
    ) -> str:
        x_center = (bbox["x"] + bbox["width"] / 2) / img_w
        y_center = (bbox["y"] + bbox["height"] / 2) / img_h
        w = bbox["width"] / img_w
        h = bbox["height"] / img_h
        return f"{class_idx} {x_center:.6f} {y_center:.6f} {w:.6f} {h:.6f}"

    @staticmethod
    def _write_data_yaml(target_dir: Path, class_names: list[str]) -> Path:
        yaml_path = target_dir / "data.yaml"
        data: dict[str, Any] = {
            "path": str(target_dir),
            "names": dict(enumerate(class_names)),
            "nc": len(class_names),
            "train": "images/train",
            "val": "images/val",
        }
        test_dir = target_dir / "images" / "test"
        if test_dir.exists():
            data["test"] = "images/test"

        yaml_path.write_text(yaml.dump(data, allow_unicode=True))
        return yaml_path
