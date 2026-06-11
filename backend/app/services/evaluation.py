import logging
import uuid
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


class EvaluationService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def run_evaluation(
        self, model_id: uuid.UUID, dataset_id: uuid.UUID, config: dict[str, Any]
    ) -> dict[str, Any]:
        logger.info("Evaluation requested: model=%s dataset=%s", model_id, dataset_id)
        # Placeholder: actual evaluation logic via frameworks/
        return {"status": "pending", "message": "evaluation not yet implemented"}
