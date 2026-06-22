"""Evaluation worker — runs in a separate process.

Usage: python -m app.runners.eval_worker <task_id>

Reads config from storage/tasks/{task_id}/config.json
Writes result to storage/tasks/{task_id}/result.json

See .claude/skills/task-rules.md for the full contract.
"""

import asyncio
import json
import logging
import os
import sys
import traceback

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def main() -> None:
    if len(sys.argv) < 2:
        logger.error("Usage: python -m app.runners.eval_worker <task_id>")
        sys.exit(1)

    task_id = sys.argv[1]

    from app.core.storage.paths import StoragePaths

    config_file = StoragePaths.task_config(task_id)
    if not config_file.exists():
        logger.error("Config file not found: %s", config_file)
        sys.exit(1)

    config = json.loads(config_file.read_text())
    StoragePaths.task_pid(task_id).write_text(str(os.getpid()))

    framework = config.get("framework", "ultralytics")

    import app.frameworks  # noqa: F401
    from app.frameworks.registry import get_evaluator

    evaluator = get_evaluator(framework)
    result_file = StoragePaths.task_result(task_id)

    try:
        result = asyncio.run(evaluator.evaluate(config))
        result_file.write_text(json.dumps({"status": "completed", **result}))
        logger.info("Evaluation completed: %s", result)
    except Exception as exc:
        result_file.write_text(json.dumps({
            "status": "failed",
            "error": str(exc),
            "traceback": traceback.format_exc(),
        }))
        logger.exception("Evaluation failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
