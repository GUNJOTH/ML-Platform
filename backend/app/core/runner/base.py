from abc import ABC, abstractmethod
from typing import Any


class TaskRunner(ABC):
    @abstractmethod
    async def run(self, task_id: str, config: dict[str, Any]) -> dict[str, Any]:
        ...

    @abstractmethod
    async def cancel(self, task_id: str) -> None:
        ...

    @abstractmethod
    async def get_progress(self, task_id: str) -> int:
        ...
