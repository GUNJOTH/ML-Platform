import logging
import shutil
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.storage.paths import StoragePaths
from app.exceptions import NotFoundError
from app.models.dataset import Dataset, Image, Label
from app.repositories.dataset import DatasetRepository, ImageRepository
from app.repositories.label import LabelRepository
from app.config import settings

logger = logging.getLogger(__name__)


class AnnotationExportService:
    def __init__(self, session: AsyncSession) -> None:
        self.dataset_repo = DatasetRepository(session)
        self.image_repo = ImageRepository(session)
        self.label_repo = LabelRepository(session)

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
        class_names = self._resolve_class_names(source, labels)
        label_map = self._build_label_map(labels, class_names)
        images = await self.image_repo.list_by_dataset(
            source_dataset_id, offset=0, limit=10000
        )
        image_lookup = {str(img.id): img for img in images}

        if mode == "overwrite":
            target_dataset = source
            target_dir = self._resolve_target_dir(source, source_dataset_id)
        else:
            target_dataset = await self._create_new_dataset(source, class_names)
            target_dir = StoragePaths.dataset_root(target_dataset.id)
            target_dir.mkdir(parents=True, exist_ok=True)
            await self._copy_images(images, target_dataset.id)

        self._write_yolo_labels(target_dir, annotations, label_map, image_lookup)
        yaml_path = self._write_data_yaml(target_dir, class_names)

        target_dataset.storage_path = str(yaml_path)
        target_dataset.status = "annotated"
        target_dataset.num_classes = len(class_names)

        return await self.dataset_repo.update(target_dataset)

    @staticmethod
    def _resolve_target_dir(source: Dataset, dataset_id: uuid.UUID) -> Path:
        if source.storage_path:
            return Path(source.storage_path).parent
        return StoragePaths.dataset_root(dataset_id)

    def _resolve_class_names(self, source: Dataset, labels: list[Label]) -> list[str]:
        if labels:
            return [lb.name for lb in labels]

        yaml_path = self._resolve_source_yaml(source)
        if yaml_path and yaml_path.exists():
            try:
                payload = yaml.safe_load(yaml_path.read_text(encoding="utf-8")) or {}
            except (OSError, yaml.YAMLError):
                payload = {}
            names = payload.get("names")
            if isinstance(names, dict):
                return [str(name) for _, name in sorted(names.items(), key=lambda item: int(item[0]))]
            if isinstance(names, list):
                return [str(name) for name in names]

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
        path = Path(source.storage_path)
        if path.is_absolute():
            return path
        if path.parts and path.parts[0] == "storage":
            return settings.storage_path.parent / path
        return settings.storage_path / path

    async def _create_new_dataset(
        self, source: Dataset, class_names: list[str]
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

        for idx, name in enumerate(class_names):
            await self.label_repo.create(
                Label(dataset_id=created.id, name=name, sort_order=idx)
            )

        return created

    async def _copy_images(
        self, images: list[Image], target_id: uuid.UUID
    ) -> None:
        for img in images:
            src_path = self._resolve_image_path(img.file_path)
            dest_dir = StoragePaths.dataset_images_dir(target_id, img.split)
            dest_dir.mkdir(parents=True, exist_ok=True)
            dest_path = dest_dir / img.filename
            if src_path.exists():
                shutil.copy2(str(src_path), str(dest_path))

            await self.image_repo.create(
                Image(
                    dataset_id=target_id,
                    filename=img.filename,
                    file_path=str(dest_path),
                    split=img.split,
                    width=img.width,
                    height=img.height,
                    annotation_status="annotated",
                )
            )

    @staticmethod
    def _resolve_image_path(path_str: str) -> Path:
        path = Path(path_str)
        if path.is_absolute():
            return path
        if path.parts and path.parts[0] == "storage":
            return settings.storage_path.parent / path
        return settings.storage_path / path

    def _write_yolo_labels(
        self,
        target_dir: Path,
        annotations: dict[str, list[dict[str, Any]]],
        label_map: dict[str, int],
        image_lookup: dict[str, Image],
    ) -> None:
        for image_id, boxes in annotations.items():
            img = image_lookup.get(image_id)
            if not img:
                continue

            label_dir = target_dir / "labels" / img.split
            label_dir.mkdir(parents=True, exist_ok=True)
            label_file = label_dir / (Path(img.filename).stem + ".txt")

            img_w = img.width if img.width > 0 else 640
            img_h = img.height if img.height > 0 else 640

            lines = [
                self._bbox_to_yolo_line(
                    self._resolve_box_class_index(box["label_id"], label_map),
                    box["bbox"],
                    img_w,
                    img_h,
                )
                for box in boxes
            ]
            label_file.write_text("\n".join(lines))

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
