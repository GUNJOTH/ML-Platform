import logging
from pathlib import Path

from app.config import settings
from app.core.storage.factory import get_storage

logger = logging.getLogger(__name__)

ALLOWED_IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".webp"}
ALLOWED_MODEL_EXTS = {".pt", ".pth", ".onnx", ".torchscript"}
ALLOWED_ARCHIVE_EXTS = {".zip", ".tar", ".tar.gz", ".tgz"}


class UploadService:
    def __init__(self) -> None:
        self.storage = get_storage()
        self.max_size = settings.max_upload_size_mb * 1024 * 1024

    async def save_dataset_archive(self, filename: str, source) -> str:
        ext = Path(filename).suffix.lower()
        if ext not in ALLOWED_ARCHIVE_EXTS:
            raise ValueError(f"Unsupported archive format: {ext}")

        save_path = f"uploads/datasets/{filename}"
        await self.storage.save_stream(save_path, source, max_size=self.max_size)
        logger.info("Dataset archive saved: %s", save_path)
        return save_path

    async def save_model_weight(self, filename: str, source) -> str:
        ext = Path(filename).suffix.lower()
        if ext not in ALLOWED_MODEL_EXTS:
            raise ValueError(f"Unsupported model format: {ext}")

        save_path = f"uploads/models/{filename}"
        await self.storage.save_stream(save_path, source, max_size=self.max_size)
        logger.info("Model weight saved: %s", save_path)
        return save_path

    async def save_image(self, filename: str, source) -> str:
        ext = Path(filename).suffix.lower()
        if ext not in ALLOWED_IMAGE_EXTS:
            raise ValueError(f"Unsupported image format: {ext}")

        save_path = f"uploads/images/{filename}"
        await self.storage.save_stream(save_path, source, max_size=self.max_size)
        return save_path
