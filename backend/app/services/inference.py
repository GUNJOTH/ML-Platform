import logging
import uuid
from pathlib import Path
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.dataset_files import resolve_storage_path
from app.core.storage.factory import get_storage
from app.exceptions import InferenceError, NotFoundError
from app.frameworks.registry import get_predictor
from app.repositories.model import MLModelRepository

logger = logging.getLogger(__name__)


class InferenceService:
    def __init__(self, session: AsyncSession) -> None:
        self.model_repo = MLModelRepository(session)
        self.storage = get_storage()

    async def run_inference(
        self,
        model_id: uuid.UUID,
        image_path: str,
        config: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        model = await self.model_repo.get_by_id(model_id)
        if not model or not model.weight_path:
            raise NotFoundError(f"Model {model_id} not found or has no weights")

        resolved_image = resolve_storage_path(image_path)
        resolved_weight = resolve_storage_path(model.weight_path)

        framework = model.framework or "ultralytics"
        try:
            predictor = get_predictor(framework)
            detections = await predictor.predict(
                str(resolved_weight),
                str(resolved_image),
            )
        except Exception as exc:
            logger.exception("Inference failed for model %s", model_id)
            raise InferenceError(str(exc)) from exc
        finally:
            await self._delete_uploaded_image(image_path)

        logger.info(
            "Inference on model %s: %d detections", model_id, len(detections)
        )
        return detections

    async def _delete_uploaded_image(self, image_path: str) -> None:
        relative_path = self._resolve_upload_image_relative_path(image_path)
        if not relative_path:
            return

        try:
            await self.storage.delete(relative_path)
        except OSError:
            logger.warning(
                "Failed to delete uploaded inference image: %s",
                relative_path,
            )

    @staticmethod
    def _resolve_upload_image_relative_path(image_path: str) -> str | None:
        path = Path(image_path)
        if not path.parts:
            return None

        normalized_parts = (
            path.parts[1:] if path.parts[0] == "storage" else path.parts
        )
        if len(normalized_parts) < 3:
            return None
        if normalized_parts[0] != "uploads" or normalized_parts[1] != "images":
            return None

        relative_path = Path(*normalized_parts)
        full_path = (settings.storage_path / relative_path).resolve()
        uploads_root = (settings.storage_path / "uploads" / "images").resolve()

        try:
            full_path.relative_to(uploads_root)
        except ValueError:
            return None

        return str(relative_path)
