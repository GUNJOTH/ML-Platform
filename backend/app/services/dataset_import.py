import logging
import os
import zipfile
from pathlib import Path
from typing import Any

import yaml

from app.core.dataset_files import extract_class_names, read_image_size, read_yaml_payload
from app.core.storage.paths import StoragePaths

logger = logging.getLogger(__name__)

_IMAGE_EXTS = (".jpg", ".jpeg", ".png")


class DatasetImporter:
    """Infrastructure helper: extracts uploaded zip files and detects YOLO-style
    dataset structure on disk. Not a Service — does not touch the database.
    """

    async def upload_and_extract(self, dataset_id: str, source) -> dict[str, Any]:
        upload_path = StoragePaths.upload_path(f"{dataset_id}.zip")
        upload_path.parent.mkdir(parents=True, exist_ok=True)
        total = 0
        with upload_path.open("wb") as f:
            while True:
                chunk = source.read(1024 * 1024)
                if not chunk:
                    break
                f.write(chunk)
                total += len(chunk)
        try:
            self._extract_zip(dataset_id, upload_path)
        finally:
            upload_path.unlink(missing_ok=True)
        return {"status": "extracted", "size_bytes": total}

    def _extract_zip(self, dataset_id: str, zip_path: Path) -> Path:
        target = StoragePaths.dataset_root(dataset_id)
        target.mkdir(parents=True, exist_ok=True)
        resolved_target = target.resolve()

        with zipfile.ZipFile(zip_path, "r") as zf:
            archive_root = self._detect_archive_root(zf.infolist())
            for member in zf.infolist():
                relative_name = self._normalize_archive_member_name(
                    member.filename,
                    archive_root=archive_root,
                )
                if not relative_name:
                    continue

                member_path = target / relative_name
                resolved = member_path.resolve()
                # Prevent zip-slip: member must stay inside target directory
                if not str(resolved).startswith(str(resolved_target) + os.sep):
                    logger.warning("Skipping suspicious zip entry: %s", member.filename)
                    continue
                if member.is_dir():
                    resolved.mkdir(parents=True, exist_ok=True)
                else:
                    resolved.parent.mkdir(parents=True, exist_ok=True)
                    with zf.open(member) as src, open(resolved, "wb") as dst:
                        dst.write(src.read())

        logger.info("Extracted dataset %s to %s", dataset_id, target)
        return target

    @staticmethod
    def _detect_archive_root(members: list[zipfile.ZipInfo]) -> str | None:
        root_names: set[str] = set()
        for member in members:
            normalized = member.filename.replace("\\", "/").lstrip("./")
            if not normalized:
                continue
            parts = [part for part in normalized.split("/") if part]
            if not parts:
                continue
            root_names.add(parts[0])
            if len(root_names) > 1:
                return None

        if len(root_names) != 1:
            return None

        root_name = next(iter(root_names))
        if not root_name.lower().endswith((".zip", ".yaml", ".yml")):
            return root_name
        return None

    @staticmethod
    def _normalize_archive_member_name(
        filename: str,
        *,
        archive_root: str | None,
    ) -> str:
        normalized = filename.replace("\\", "/").lstrip("./")
        if not normalized:
            return ""

        if archive_root:
            prefix = f"{archive_root}/"
            if normalized == archive_root:
                return ""
            if normalized.startswith(prefix):
                normalized = normalized[len(prefix):]

        return normalized

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

        split_aliases = {
            "train": ("train",),
            "val": ("val", "valid"),
            "test": ("test",),
        }

        for split, candidates in split_aliases.items():
            images_dir = next(
                (
                    resolved
                    for candidate in candidates
                    if (resolved := self._find_split_dir(root, candidate)) is not None
                ),
                None,
            )
            if images_dir:
                data[split] = str(images_dir)

        yaml_path.write_text(yaml.dump(data, allow_unicode=True))
        logger.info("Generated data.yaml at %s", yaml_path)
        return str(yaml_path)

    def list_images(self, dataset_id: str, split: str) -> list[dict[str, Any]]:
        root = StoragePaths.dataset_root(dataset_id)
        images_dir = self._find_split_dir(root, split)
        if images_dir:
            return [
                self._build_image_entry(f)
                for f in sorted(images_dir.iterdir())
                if f.suffix.lower() in _IMAGE_EXTS
            ]
        return [
            self._build_image_entry(f)
            for f in sorted(root.rglob("*"))
            if f.suffix.lower() in _IMAGE_EXTS
        ]

    @classmethod
    def _build_image_entry(cls, path: Path) -> dict[str, Any]:
        width, height = cls._read_image_size(path)
        return {
            "filename": path.name,
            "path": str(path),
            "width": width,
            "height": height,
        }

    @staticmethod
    def _read_image_size(path: Path) -> tuple[int, int]:
        return read_image_size(path)

    @staticmethod
    def _count_images(images_dir: Path) -> int:
        return sum(1 for f in images_dir.iterdir() if f.suffix.lower() in _IMAGE_EXTS)

    @staticmethod
    def _find_data_yaml(root: Path) -> Path | None:
        preferred: list[Path] = []
        fallback: list[Path] = []

        for candidate in root.rglob("data.yaml"):
            preferred.append(candidate)
        for candidate in root.rglob("*.yaml"):
            if candidate not in preferred:
                fallback.append(candidate)

        for candidate in [*preferred, *fallback]:
            try:
                payload = read_yaml_payload(candidate)
            except Exception:
                continue
            class_names = extract_class_names(payload)
            has_split = any(
                isinstance(payload.get(key), str) and payload.get(key)
                for key in ("train", "val", "valid", "test")
            )
            if class_names and has_split:
                return candidate

        for candidate in [*preferred, *fallback]:
            if "names" in candidate.read_text(errors="ignore"):
                return candidate
        return None

    @staticmethod
    def _parse_classes(yaml_path: Path) -> list[str]:
        return extract_class_names(read_yaml_payload(yaml_path))

    @staticmethod
    def _find_split_dir(root: Path, split: str) -> Path | None:
        direct_candidate = root / "images" / split
        if direct_candidate.is_dir():
            return direct_candidate

        for images_dir in root.rglob("images"):
            if not images_dir.is_dir():
                continue
            candidate = images_dir / split
            if candidate.is_dir():
                return candidate

        for candidate in root.rglob(split):
            if candidate.is_dir() and candidate.parent.name == "images":
                return candidate

        for candidate in root.rglob(split):
            if not candidate.is_dir():
                continue
            images_dir = candidate / "images"
            if images_dir.is_dir():
                return images_dir
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
