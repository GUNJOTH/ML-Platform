import json
import logging
import os
import signal
import subprocess
import sys
from typing import Any

from app.core.runner.base import TaskRunner
from app.core.storage.paths import StoragePaths

logger = logging.getLogger(__name__)


class ProcessRunner(TaskRunner):
    """Spawns a worker subprocess per task. Worker communicates via files in
    storage/tasks/{task_id}/. See .claude/skills/task-rules.md for the contract.
    """

    async def run(self, task_id: str, config: dict[str, Any]) -> dict[str, Any]:
        task_dir = StoragePaths.task_root(task_id)
        task_dir.mkdir(parents=True, exist_ok=True)

        StoragePaths.task_config(task_id).write_text(json.dumps(config))

        worker_module = config.get("worker_module", "app.runners.train_worker")
        stdout_path = StoragePaths.task_stdout(task_id)
        stderr_path = StoragePaths.task_stderr(task_id)

        with stdout_path.open("w") as out_fp, stderr_path.open("w") as err_fp:
            proc = subprocess.Popen(
                [sys.executable, "-m", worker_module, task_id],
                stdout=out_fp,
                stderr=err_fp,
            )

        logger.info("Started worker PID=%d for task %s", proc.pid, task_id)
        return {"pid": proc.pid}

    async def cancel(self, task_id: str) -> None:
        pid_file = StoragePaths.task_pid(task_id)
        if not pid_file.exists():
            return
        try:
            pid = int(pid_file.read_text().strip())
            if not pid or pid < 0:
                return
            if sys.platform == "win32":
                subprocess.run(
                    ["taskkill", "/PID", str(pid), "/F", "/T"],
                    capture_output=True,
                )
            else:
                os.kill(pid, signal.SIGTERM)
            logger.info("Terminated PID %d for task %s", pid, task_id)
        except (ProcessLookupError, ValueError, OSError):
            logger.warning("Process for task %s not running", task_id)

    async def get_progress(self, task_id: str) -> int:
        progress_file = StoragePaths.task_progress(task_id)
        if not progress_file.exists():
            return 0
        try:
            data = json.loads(progress_file.read_text())
            return int(data.get("progress", 0))
        except (json.JSONDecodeError, ValueError):
            return 0

    async def get_result(self, task_id: str) -> dict[str, Any] | None:
        result_file = StoragePaths.task_result(task_id)
        if not result_file.exists():
            return None
        try:
            return json.loads(result_file.read_text())
        except (json.JSONDecodeError, ValueError):
            return None

    async def is_running(self, task_id: str) -> bool:
        pid_file = StoragePaths.task_pid(task_id)
        if not pid_file.exists():
            return False

        try:
            pid = int(pid_file.read_text().strip())
        except (ValueError, OSError):
            return False

        if pid <= 0:
            return False

        try:
            if sys.platform == "win32":
                result = subprocess.run(
                    ["tasklist", "/FI", f"PID eq {pid}"],
                    capture_output=True,
                    text=True,
                    check=False,
                )
                return str(pid) in result.stdout

            os.kill(pid, 0)
            return True
        except OSError:
            return False
