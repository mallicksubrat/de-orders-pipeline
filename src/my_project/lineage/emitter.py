from __future__ import annotations

import json
from pathlib import Path

from my_project.utils.logger import get_logger


def emit_lineage(event: dict, output_path: Path | None = None) -> None:
    logger = get_logger("my_project.lineage")
    payload = json.dumps(event, sort_keys=True)

    if output_path is not None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with output_path.open("a", encoding="utf-8") as handle:
            handle.write(payload + "\n")

    logger.info("lineage_event=%s", payload)
