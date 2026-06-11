import logging
import uuid
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


class InferenceService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def run_inference(
        self, model_id: uuid.UUID, image_paths: list[str], config: dict[str, Any]
    ) -> dict[str, Any]:
        logger.info("Inference requested for model %s on %d images", model_id, len(image_paths))
        # Placeholder: actual inference logic will be implemented via frameworks/
        return {"status": "pending", "message": "inference not yet implemented"}
