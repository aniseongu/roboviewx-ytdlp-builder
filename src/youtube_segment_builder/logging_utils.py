from __future__ import annotations

import csv
from datetime import datetime, timezone
from pathlib import Path

_LOG_COLUMNS = [
    "timestamp",
    "source_id",
    "candidate_id",
    "step",
    "status",
    "message",
    "output_path",
]


def append_log(
    log_path: str,
    source_id: str,
    candidate_id: str,
    step: str,
    status: str,
    message: str,
    output_path: str = "",
) -> None:
    path = Path(log_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    write_header = not path.exists()
    with open(path, "a", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=_LOG_COLUMNS)
        if write_header:
            writer.writeheader()
        writer.writerow(
            {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "source_id": source_id,
                "candidate_id": candidate_id,
                "step": step,
                "status": status,
                "message": message,
                "output_path": output_path,
            }
        )
