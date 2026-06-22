import logging
import zipfile
from pathlib import Path
from typing import Any

import yaml

from app.core.storage.paths import StoragePaths

logger = logging.getLogger(__name__)

_IMAGE_EXTS = (".jpg", ".jpeg", ".png")


class DatasetImporter:
    """Infrastructure helper: extracts uploaded zip files and detects YOLO-style
    dataset structure on disk. Not a Service — does not touch the database.
    """

    async def upload_and_extract(self, dataset_id: str, content: bytes) -> dict[str, Any]:
        upload_path = StoragePaths.upload_path(f"{dataset_id}.zip")
        upload_path.parent.mkdir(parents=True, exist_ok=True)
        upload_path.write_bytes(content)
        try:
            self._extract_zip(dataset_id, upload_path)
        finally:
            upload_path.unlink(missing_ok=True)
        return {"status": "extracted", "size_bytes": len(content)}

    def _extract_zip(self, dataset_id: str, zip_path: Path) -> Path:
        target = StoragePaths.dataset_root(dataset_id)
        target.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(target)
        logger.info("Extracted dataset %s to %s", dataset_id, target)
        return target

    def detect_structure(self, dataset_id: str) -> dict[str, Any]:
        root = StoragePaths.dataset_root(dataset_id)
        result: dict[str, Any] = {"root": str(root), "splits": {}, "classes": []}

        data_yaml = self._find_data_yaml(root)
        if data_yaml:
            result["classes"] = self._parse_classes(data_yaml)
            result["data_yaml_path"] = str(data_yaml)

        for split in ("train", "valid", "val", "test"):
            images_dir = self._find_split_dir(root, split)
            if images_dir:
                result["splits"][split] = {
                    "images_dir": str(images_dir),
                    "count": self._count_images(images_dir),
                }

        if not result["splits"]:
            all_images = list(root.rglob("*"))
            all_images = [f for f in all_images if f.suffix.lower() in _IMAGE_EXTS]
            if all_images:
                result["splits"]["train"] = {
                    "images_dir": str(root),
                    "count": len(all_images),
                }
            if not result["classes"]:
                class_dirs = [
                    d.name for d in root.iterdir()
                    if d.is_dir() and any(f.suffix.lower() in _IMAGE_EXTS for f in d.iterdir() if f.is_file())
                ]
                if class_dirs:
                    result["classes"] = sorted(class_dirs)

        return result

    def generate_data_yaml(self, dataset_id: str, classes: list[str]) -> str:
        root = StoragePaths.dataset_root(dataset_id)
        yaml_path = StoragePaths.dataset_yaml(dataset_id)

        if not classes:
            classes = self._scan_classes_from_labels(root)

        data: dict[str, Any] = {
            "names": dict(enumerate(classes)),
            "nc": len(classes),
        }

        for split, dirname in (("train", "train"), ("val", "valid"), ("test", "test")):
            images_dir = self._find_split_dir(root, dirname) or self._find_split_dir(root, "val")
            if images_dir:
                data[split] = str(images_dir)

        yaml_path.write_text(yaml.dump(data, allow_unicode=True))
        logger.info("Generated data.yaml at %s", yaml_path)
        return str(yaml_path)

    def list_images(self, dataset_id: str, split: str) -> list[dict[str, str]]:
        root = StoragePaths.dataset_root(dataset_id)
        images_dir = self._find_split_dir(root, split)
        if images_dir:
            return [
                {"filename": f.name, "path": str(f)}
                for f in sorted(images_dir.iterdir())
                if f.suffix.lower() in _IMAGE_EXTS
            ]
        return [
            {"filename": f.name, "path": str(f)}
            for f in sorted(root.rglob("*"))
            if f.suffix.lower() in _IMAGE_EXTS
        ]

    @staticmethod
    def _count_images(images_dir: Path) -> int:
        return sum(1 for f in images_dir.iterdir() if f.suffix.lower() in _IMAGE_EXTS)

    @staticmethod
    def _find_data_yaml(root: Path) -> Path | None:
        for candidate in root.rglob("data.yaml"):
            return candidate
        for candidate in root.rglob("*.yaml"):
            if "names" in candidate.read_text(errors="ignore"):
                return candidate
        return None

    @staticmethod
    def _parse_classes(yaml_path: Path) -> list[str]:
        data = yaml.safe_load(yaml_path.read_text())
        names = data.get("names", {})
        if isinstance(names, dict):
            return [names[k] for k in sorted(names.keys())]
        if isinstance(names, list):
            return names
        return []

    @staticmethod
    def _find_split_dir(root: Path, split: str) -> Path | None:
        for candidate in root.rglob(f"{split}/images"):
            return candidate
        for candidate in root.rglob(split):
            if candidate.is_dir():
                return candidate
        return None

    @staticmethod
    def _scan_classes_from_labels(root: Path) -> list[str]:
        class_ids: set[int] = set()
        for labels_dir in root.rglob("labels"):
            if not labels_dir.is_dir():
                continue
            for txt in labels_dir.rglob("*.txt"):
                for line in txt.read_text(errors="ignore").strip().splitlines():
                    parts = line.strip().split()
                    if parts:
                        try:
                            class_ids.add(int(parts[0]))
                        except ValueError:
                            continue
        if not class_ids:
            return []
        return [f"class_{i}" for i in range(max(class_ids) + 1)]
