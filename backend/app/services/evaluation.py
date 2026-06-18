import logging
import uuid
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import NotFoundError
from app.repositories.model import MLModelRepository
from app.schemas.task import TaskCreate

logger = logging.getLogger(__name__)


class EvaluationService:
    """Builds evaluation TaskCreate payloads. Routers call this then pass the
    payload to TaskService — services do not new other services.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.model_repo = MLModelRepository(session)

    async def build_task(
        self,
        model_id: uuid.UUID,
        dataset_id: uuid.UUID,
        config: dict[str, Any] | None = None,
    ) -> TaskCreate:
        model = await self.model_repo.get_by_id(model_id)
        if not model or not model.weight_path:
            raise NotFoundError(f"Model {model_id} not found or has no weights")

        task_config = {
            "model_path": model.weight_path,
            "model_id": str(model_id),
            "dataset_id": str(dataset_id),
            "framework": model.framework or "ultralytics",
            **(config or {}),
        }

        return TaskCreate(
            name=f"Evaluate {model.name}",
            task_type="evaluation",
            model_id=model_id,
            dataset_id=dataset_id,
            config=task_config,
        )
