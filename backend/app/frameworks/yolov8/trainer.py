import json
import logging
from pathlib import Path
from typing import Any, Callable

from app.frameworks.base import BaseTrainer
from app.core.storage.paths import StoragePaths

logger = logging.getLogger(__name__)


class YOLOv8Trainer(BaseTrainer):
    async def train(self, config: dict[str, Any]) -> dict[str, Any]:
        from ultralytics import YOLO

        weight_path = config.get("weight_path")
        if not weight_path:
            raise ValueError("缺少 weight_path：训练任务必须指定本地预训练模型")
        data_yaml = config["data_yaml_path"]
        epochs = config.get("epochs", 50)
        batch_size = config.get("batch_size", 16)
        img_size = config.get("img_size", 640)
        patience = config.get("patience", 10)
        optimizer = config.get("optimizer", "AdamW")
        lr0 = config.get("lr0", 0.01)
        warmup_epochs = config.get("warmup_epochs", 3)
        cos_lr = config.get("cos_lr", False)
        close_mosaic = config.get("close_mosaic", 10)
        pretrained = config.get("pretrained", True)
        task_id = config.get("task_id", "standalone")
        import torch
        device = config.get("device") or ("cuda" if torch.cuda.is_available() else "cpu")
        run_name = config.get("run_name", "train")
        project_dir = config.get("project_dir", str(StoragePaths.run_root(task_id)))
        progress_file = config.get("progress_file")

        model = YOLO(weight_path)

        history_file = str(Path(progress_file).parent / "history.json") if progress_file else None

        def _on_train_epoch_end(trainer_obj: Any) -> None:
            if not progress_file:
                return
            current = trainer_obj.epoch + 1
            total = trainer_obj.epochs
            progress = int((current / total) * 100)
            Path(progress_file).write_text(
                json.dumps({"progress": progress, "epoch": current, "total": total})
            )

            if history_file:
                epoch_data: dict[str, Any] = {"epoch": current}
                if trainer_obj.loss is not None:
                    epoch_data["train_loss"] = round(float(trainer_obj.loss.mean()), 4)
                if hasattr(trainer_obj, "metrics") and trainer_obj.metrics:
                    epoch_data["map50"] = round(float(trainer_obj.metrics.get("metrics/mAP50(B)", 0)), 4)
                    epoch_data["map50_95"] = round(float(trainer_obj.metrics.get("metrics/mAP50-95(B)", 0)), 4)
                hp = Path(history_file)
                history = json.loads(hp.read_text()) if hp.exists() else []
                history.append(epoch_data)
                hp.write_text(json.dumps(history))

        model.add_callback("on_train_epoch_end", _on_train_epoch_end)

        results = model.train(
            data=data_yaml,
            epochs=epochs,
            batch=batch_size,
            imgsz=img_size,
            patience=patience,
            optimizer=optimizer,
            lr0=lr0,
            warmup_epochs=warmup_epochs,
            cos_lr=cos_lr,
            close_mosaic=close_mosaic,
            pretrained=pretrained,
            device=device,
            project=project_dir,
            name=run_name,
            exist_ok=True,
        )

        best_weight = Path(project_dir) / run_name / "weights" / "best.pt"
        metrics = self._extract_metrics(results)
        metrics["weight_path"] = str(best_weight)

        logger.info("Training completed: %s", metrics)
        return metrics

    def _extract_metrics(self, results: Any) -> dict[str, Any]:
        try:
            return {
                "map50": float(results.results_dict.get("metrics/mAP50(B)", 0)),
                "map50_95": float(results.results_dict.get("metrics/mAP50-95(B)", 0)),
                "precision": float(results.results_dict.get("metrics/precision(B)", 0)),
                "recall": float(results.results_dict.get("metrics/recall(B)", 0)),
            }
        except (AttributeError, TypeError):
            return {"map50": 0, "map50_95": 0, "precision": 0, "recall": 0}
