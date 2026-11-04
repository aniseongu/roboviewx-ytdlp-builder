from __future__ import annotations

import shutil
from dataclasses import dataclass, field
from pathlib import Path

import pandas as pd

# Target schema of data/input/confirmed_segments.csv (technical fields only —
# no permission_status / permission_evidence_path columns, by project rule).
CONFIRMED_COLUMNS = [
    "source_id",
    "candidate_id",
    "youtube_url",
    "ytid",
    "creator_name",
    "video_title",
    "label_code",
    "is_intrusion",
    "group",
    "start_sec",
    "end_sec",
    "attribution_text",
    "notes",
]

# Columns copied straight across from the candidate row (same name on both sides).
# start_sec / end_sec are handled separately (clip_start_sec / clip_end_sec).
_PASSTHROUGH_COLUMNS = [
    "source_id",
    "candidate_id",
    "youtube_url",
    "ytid",
    "creator_name",
    "video_title",
    "label_code",
    "is_intrusion",
    "group",
    "attribution_text",
    "notes",
]

# selected values that mean "include this row" — compared case-insensitively.
_SELECTED_TRUE = {"yes", "y", "true"}


@dataclass
class BuildResult:
    total_candidates: int = 0
    selected_rows: int = 0
    output_path: str = ""
    backup_path: str | None = None
    warnings: list[str] = field(default_factory=list)


def _is_selected(value: object) -> bool:
    return str(value).strip().lower() in _SELECTED_TRUE


def build_confirmed_from_candidates(
    candidates_path: str,
    output_path: str,
    backup: bool = True,
) -> BuildResult:
    """Turn selected=YES candidate rows into a confirmed_segments.csv.

    Only technical fields are mapped. No permission gate is applied — the human
    team confirms permissions before selecting rows.
    """
    result = BuildResult(output_path=output_path)

    cand = pd.read_csv(candidates_path, dtype=str).fillna("")
    result.total_candidates = len(cand)

    if "selected" not in cand.columns:
        raise ValueError(
            f"{candidates_path} has no 'selected' column — is this an "
            "audioset_candidates.csv?"
        )

    missing = [
        c
        for c in _PASSTHROUGH_COLUMNS + ["clip_start_sec", "clip_end_sec"]
        if c not in cand.columns
    ]
    if missing:
        raise ValueError(f"candidates CSV missing expected columns: {missing}")

    selected = cand[cand["selected"].map(_is_selected)]
    result.selected_rows = len(selected)

    rows: list[dict] = []
    for _, c in selected.iterrows():
        row = {col: str(c.get(col, "")).strip() for col in _PASSTHROUGH_COLUMNS}
        row["start_sec"] = str(c.get("clip_start_sec", "")).strip()
        row["end_sec"] = str(c.get("clip_end_sec", "")).strip()
        rows.append(row)

    # Back up an existing confirmed_segments.csv before overwriting it.
    output = Path(output_path)
    if output.exists() and backup:
        bak = output.with_suffix(output.suffix + ".bak")
        shutil.copy2(output, bak)
        result.backup_path = str(bak)

    output.parent.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame(rows, columns=CONFIRMED_COLUMNS)
    df.to_csv(output, index=False)

    return result
