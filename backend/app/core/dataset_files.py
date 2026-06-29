from __future__ import annotations

from pathlib import Path
from typing import Any

from PIL import Image as PILImage
import yaml

from app.config import settings
from app.exceptions import ValidationError

_YAML_ENCODINGS = ("utf-8", "utf-8-sig", "gbk")
_DATASET_SPLITS = {"train", "val", "test"}


def resolve_storage_path(path_str: str) -> Path:
    path = Path(path_str)
    if path.is_absolute():
        return path
    if path.parts and path.parts[0] == "storage":
        return settings.storage_path.parent / path
    return settings.storage_path / path


def read_yaml_payload(yaml_path: Path) -> dict[str, Any]:
    for encoding in _YAML_ENCODINGS:
        try:
            content = yaml_path.read_text(encoding=encoding)
            payload = yaml.safe_load(content) or {}
            if isinstance(payload, dict):
                return payload
            raise ValidationError(f"数据集配置文件 {yaml_path.name} 内容格式无效，应为 YAML 对象")
        except UnicodeDecodeError:
            continue
        except yaml.YAMLError as exc:
            raise ValidationError(
                f"数据集配置文件 {yaml_path.name} 解析失败，请检查 YAML 格式是否正确"
            ) from exc
        except OSError as exc:
            raise ValidationError(
                f"读取数据集配置文件 {yaml_path.name} 失败，请检查文件是否可访问"
            ) from exc

    raise ValidationError(
        f"数据集配置文件 {yaml_path.name} 编码无法识别，请转换为 UTF-8 或 UTF-8 with BOM 后重试"
    )


def extract_class_names(payload: dict[str, Any]) -> list[str]:
    names = payload.get("names")
    if isinstance(names, list):
        return [str(item) for item in names]
    if isinstance(names, dict):
        return [str(name) for _, name in sorted(names.items(), key=lambda item: int(item[0]))]
    nc = payload.get("nc")
    if isinstance(nc, int) and nc > 0:
        return [f"class_{index}" for index in range(nc)]
    return []


def read_image_size(image_path: Path) -> tuple[int, int]:
    try:
        with PILImage.open(image_path) as image_file:
            return int(image_file.width), int(image_file.height)
    except OSError:
        return 0, 0


def resolve_dataset_root_from_image_path(image_path: Path) -> Path:
    datasets_root = (settings.storage_path / "datasets").resolve()
    resolved_image_path = image_path.resolve()

    try:
        relative_path = resolved_image_path.relative_to(datasets_root)
    except ValueError:
        return _resolve_dataset_root_from_structure(resolved_image_path)

    if relative_path.parts:
        return datasets_root / relative_path.parts[0]
    return _resolve_dataset_root_from_structure(resolved_image_path)


def _resolve_dataset_root_from_structure(image_path: Path) -> Path:
    for parent in image_path.parents:
        if (parent / "data.yaml").exists():
            return parent
        if (parent / "images").exists() or (parent / "labels").exists():
            return parent

    return image_path.parent


def resolve_effective_split_from_image_path(image_path: Path, fallback_split: str) -> str:
    dataset_root = resolve_dataset_root_from_image_path(image_path)
    inferred_split = infer_split_from_image_path(image_path, dataset_root)
    if inferred_split:
        return inferred_split
    return fallback_split


def infer_split_from_image_path(image_path: Path, dataset_root: Path) -> str | None:
    try:
        relative_path = image_path.relative_to(dataset_root)
    except ValueError:
        return None

    parts = relative_path.parts
    for index, part in enumerate(parts[:-1]):
        if part != "images" or index + 1 >= len(parts):
            continue
        split = parts[index + 1]
        if split in _DATASET_SPLITS:
            return split
    return None


def build_yolo_label_file_index(dataset_root: Path) -> dict[str, list[Path]]:
    label_index: dict[str, list[Path]] = {}
    label_root = dataset_root / "labels"
    if not label_root.exists():
        return label_index

    for label_path in label_root.rglob("*.txt"):
        label_index.setdefault(label_path.stem, []).append(label_path)

    for matches in label_index.values():
        matches.sort()
    return label_index


def resolve_yolo_label_path(
    dataset_root: Path,
    image_path: Path,
    *,
    image_split: str | None = None,
    label_index: dict[str, list[Path]] | None = None,
) -> Path | None:
    candidates: list[Path] = []

    inferred_split = infer_split_from_image_path(image_path, dataset_root)
    if inferred_split:
        candidates.append(dataset_root / "labels" / inferred_split / f"{image_path.stem}.txt")
    if image_split and image_split != inferred_split:
        candidates.append(dataset_root / "labels" / image_split / f"{image_path.stem}.txt")

    for candidate in candidates:
        if candidate.exists():
            return candidate

    matches = label_index.get(image_path.stem, []) if label_index is not None else []
    if not matches:
        label_root = dataset_root / "labels"
        if label_root.exists():
            matches = sorted(label_root.rglob(f"{image_path.stem}.txt"))

    if not matches:
        return candidates[0] if candidates else None

    if image_split:
        matched = next((path for path in matches if path.parent.name == image_split), None)
        if matched is not None:
            return matched
    if inferred_split:
        matched = next((path for path in matches if path.parent.name == inferred_split), None)
        if matched is not None:
            return matched
    return matches[0]
