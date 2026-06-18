import logging
from typing import Any

from app.core.runner.base import TaskRunner

logger = logging.getLogger(__name__)


class SyncRunner(TaskRunner):
    async def run(self, task_id: str, config: dict[str, Any]) -> dict[str, Any]:
        logger.info("SyncRunner.run called for task %s (placeholder)", task_id)
        return {"status": "completed", "message": "placeholder"}

    async def cancel(self, task_id: str) -> None:
        logger.info("SyncRunner.cancel called for task %s (placeholder)", task_id)

    async def get_progress(self, task_id: str) -> int:
        return 0

    async def get_result(self, task_id: str) -> dict[str, Any] | None:
        return None
