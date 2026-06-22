import asyncio
import json
import logging
from pathlib import Path

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.core.storage.paths import StoragePaths

logger = logging.getLogger(__name__)

router = APIRouter(tags=["实时通信"])

POLL_INTERVAL_SECONDS = 2


@router.websocket("/ws/tasks/{task_id}")
async def task_progress_ws(websocket: WebSocket, task_id: str) -> None:
    await websocket.accept()
    progress_file = StoragePaths.task_progress(task_id)
    result_file = StoragePaths.task_result(task_id)

    try:
        while True:
            if result_file.exists():
                await websocket.send_json({
                    "type": "complete",
                    **json.loads(result_file.read_text()),
                })
                break

            await websocket.send_json({
                "type": "progress",
                **_read_progress(progress_file),
            })
            await asyncio.sleep(POLL_INTERVAL_SECONDS)

    except WebSocketDisconnect:
        logger.debug("WebSocket disconnected for task %s", task_id)
    except Exception:
        logger.exception("WebSocket error for task %s", task_id)


def _read_progress(path: Path) -> dict[str, int]:
    if not path.exists():
        return {"progress": 0, "epoch": 0, "total": 0}
    try:
        return json.loads(path.read_text())
    except (json.JSONDecodeError, ValueError):
        return {"progress": 0, "epoch": 0, "total": 0}
