import logging
import uuid
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dataset_files import resolve_storage_path
from app.exceptions import InferenceError, NotFoundError
from app.frameworks.registry import get_predictor
from app.repositories.model import MLModelRepository

logger = logging.getLogger(__name__)


class InferenceService:
    def __init__(self, session: AsyncSession) -> None:
        self.model_repo = MLModelRepository(session)

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
            detections = await predictor.predict(str(resolved_weight), str(resolved_image))
        except Exception as exc:
            logger.exception("Inference failed for model %s", model_id)
            raise InferenceError(str(exc)) from exc

        logger.info(
            "Inference on model %s: %d detections", model_id, len(detections)
        )
        return detections
