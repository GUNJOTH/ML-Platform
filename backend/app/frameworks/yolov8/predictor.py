import logging
from typing import Any

from app.frameworks.base import BasePredictor

logger = logging.getLogger(__name__)


class YOLOv8Predictor(BasePredictor):
    async def predict(self, model_path: str, input_path: str) -> list[dict[str, Any]]:
        from ultralytics import YOLO

        model = YOLO(model_path)
        results = model.predict(
            source=input_path,
            conf=0.25,
            iou=0.45,
            imgsz=640,
            save=False,
        )

        detections: list[dict[str, Any]] = []
        for result in results:
            boxes = result.boxes
            if boxes is None:
                continue
            for i in range(len(boxes)):
                xyxy = boxes.xyxy[i].tolist()
                detections.append({
                    "bbox": xyxy,
                    "confidence": float(boxes.conf[i]),
                    "class_id": int(boxes.cls[i]),
                    "class_name": result.names[int(boxes.cls[i])],
                })

        logger.info("Inference: %d detections from %s", len(detections), input_path)
        return detections
