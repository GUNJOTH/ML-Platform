from __future__ import annotations

from pathlib import Path
from typing import Any

from PIL import Image as PILImage
import yaml

from app.config import settings
from app.exceptions import ValidationError

_YAML_ENCODINGS = ("utf-8", "utf-8-sig", "gbk")


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
