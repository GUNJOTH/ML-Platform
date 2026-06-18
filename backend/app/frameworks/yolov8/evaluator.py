import logging
from typing import Any

from app.frameworks.base import BaseEvaluator

logger = logging.getLogger(__name__)


class YOLOv8Evaluator(BaseEvaluator):
    async def evaluate(self, config: dict[str, Any]) -> dict[str, Any]:
        from ultralytics import YOLO

        model_path = config["model_path"]
        data_yaml = config["data_yaml_path"]
        device = config.get("device", "cuda")
        split = config.get("split", "test")

        model = YOLO(model_path)
        results = model.val(
            data=data_yaml,
            split=split,
            device=device,
            imgsz=640,
        )

        metrics = {
            "map50": float(results.results_dict.get("metrics/mAP50(B)", 0)),
            "map50_95": float(results.results_dict.get("metrics/mAP50-95(B)", 0)),
            "precision": float(results.results_dict.get("metrics/precision(B)", 0)),
            "recall": float(results.results_dict.get("metrics/recall(B)", 0)),
        }

        logger.info("Evaluation completed: %s", metrics)
        return metrics
