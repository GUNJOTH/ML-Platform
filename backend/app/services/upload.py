import logging
from pathlib import Path

from app.config import settings
from app.core.storage.factory import get_storage

logger = logging.getLogger(__name__)

ALLOWED_IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".webp"}
ALLOWED_MODEL_EXTS = {".pt", ".pth", ".onnx", ".torchscript"}
ALLOWED_ARCHIVE_EXTS = {".zip", ".tar", ".tar.gz", ".tgz"}
MAX_FILE_SIZE = 500 * 1024 * 1024  # 500MB


class UploadService:
    def __init__(self) -> None:
        self.storage = get_storage()

    async def save_dataset_archive(self, filename: str, content: bytes) -> str:
        ext = Path(filename).suffix.lower()
        if ext not in ALLOWED_ARCHIVE_EXTS:
            raise ValueError(f"Unsupported archive format: {ext}")
        if len(content) > MAX_FILE_SIZE:
            raise ValueError("File too large")

        save_path = f"uploads/datasets/{filename}"
        await self.storage.save(save_path, content)
        logger.info("Dataset archive saved: %s", save_path)
        return save_path

    async def save_model_weight(self, filename: str, content: bytes) -> str:
        ext = Path(filename).suffix.lower()
        if ext not in ALLOWED_MODEL_EXTS:
            raise ValueError(f"Unsupported model format: {ext}")
        if len(content) > MAX_FILE_SIZE:
            raise ValueError("File too large")

        save_path = f"uploads/models/{filename}"
        await self.storage.save(save_path, content)
        logger.info("Model weight saved: %s", save_path)
        return save_path

    async def save_image(self, filename: str, content: bytes) -> str:
        ext = Path(filename).suffix.lower()
        if ext not in ALLOWED_IMAGE_EXTS:
            raise ValueError(f"Unsupported image format: {ext}")

        save_path = f"uploads/images/{filename}"
        await self.storage.save(save_path, content)
        return save_path
