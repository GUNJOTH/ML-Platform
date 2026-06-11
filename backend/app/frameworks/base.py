from abc import ABC, abstractmethod
from typing import Any


class BaseTrainer(ABC):
    @abstractmethod
    async def train(self, config: dict[str, Any]) -> dict[str, Any]:
        ...


class BaseEvaluator(ABC):
    @abstractmethod
    async def evaluate(self, model_path: str, data_path: str) -> dict[str, Any]:
        ...


class BasePredictor(ABC):
    @abstractmethod
    async def predict(self, model_path: str, input_path: str) -> list[dict[str, Any]]:
        ...
