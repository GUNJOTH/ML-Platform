from typing import Any

from app.frameworks.base import BaseEvaluator, BasePredictor, BaseTrainer

_REGISTRY: dict[str, dict[str, type[BaseTrainer] | type[BaseEvaluator] | type[BasePredictor]]] = {}


def register_framework(
    name: str,
    trainer_cls: type[BaseTrainer],
    evaluator_cls: type[BaseEvaluator],
    predictor_cls: type[BasePredictor],
) -> None:
    _REGISTRY[name] = {
        "trainer": trainer_cls,
        "evaluator": evaluator_cls,
        "predictor": predictor_cls,
    }


def get_trainer(framework: str, **kwargs: Any) -> BaseTrainer:
    entry = _REGISTRY.get(framework)
    if not entry:
        raise ValueError(f"Framework '{framework}' not registered")
    cls = entry["trainer"]
    return cls(**kwargs)  # type: ignore[call-arg]


def get_evaluator(framework: str, **kwargs: Any) -> BaseEvaluator:
    entry = _REGISTRY.get(framework)
    if not entry:
        raise ValueError(f"Framework '{framework}' not registered")
    cls = entry["evaluator"]
    return cls(**kwargs)  # type: ignore[call-arg]


def get_predictor(framework: str, **kwargs: Any) -> BasePredictor:
    entry = _REGISTRY.get(framework)
    if not entry:
        raise ValueError(f"Framework '{framework}' not registered")
    cls = entry["predictor"]
    return cls(**kwargs)  # type: ignore[call-arg]


def list_frameworks() -> list[str]:
    return list(_REGISTRY.keys())
