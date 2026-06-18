from app.frameworks.registry import register_framework
from app.frameworks.yolov8.evaluator import YOLOv8Evaluator
from app.frameworks.yolov8.predictor import YOLOv8Predictor
from app.frameworks.yolov8.trainer import YOLOv8Trainer

register_framework("ultralytics", YOLOv8Trainer, YOLOv8Evaluator, YOLOv8Predictor)
