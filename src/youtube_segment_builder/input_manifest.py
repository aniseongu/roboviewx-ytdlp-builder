from __future__ import annotations

import re
from dataclasses import dataclass, field

import pandas as pd

_EMPTY_DF = pd.DataFrame()

REQUIRED_COLUMNS = [
    "source_id",
    "candidate_id",
    "youtube_url",
    "ytid",
    "label_code",
    "start_sec",
    "end_sec",
]

VALID_GROUPS = {"intrusion", "non_intrusion", "robot_noise"}

_YOUTUBE_URL_RE = re.compile(
    r"https?://(www\.)?(youtube\.com/watch\?.*v=|youtu\.be/)[\w-]+"
)


@dataclass
class ValidationResult:
    total_rows: int = 0
    valid_rows: int = 0
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    valid_df: pd.DataFrame = field(default_factory=pd.DataFrame)

    @property
    def has_errors(self) -> bool:
        return bool(self.errors)


def validate_csv(input_path: str) -> ValidationResult:
    result = ValidationResult()

    try:
        df = pd.read_csv(input_path)
    except Exception as exc:
        result.errors.append(f"Cannot read CSV: {exc}")
        return result

    result.total_rows = len(df)

    missing_cols = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing_cols:
        result.errors.append(f"Missing required columns: {missing_cols}")
        return result

    invalid_rows: set[int] = set()

    for i, row in df.iterrows():
        label = f"row {i + 2}"  # +2: header row + 0-based index

        # youtube_url
        url = str(row.get("youtube_url", "")).strip()
        if not _YOUTUBE_URL_RE.match(url):
            result.errors.append(f"{label}: invalid youtube_url: {url!r}")
            invalid_rows.add(i)

        # ytid
        ytid = str(row.get("ytid", "")).strip()
        if not ytid or ytid == "nan":
            result.errors.append(f"{label}: ytid is empty")
            invalid_rows.add(i)

        # label_code
        label_code = str(row.get("label_code", "")).strip()
        if not label_code or label_code == "nan":
            result.errors.append(f"{label}: label_code is empty")
            invalid_rows.add(i)

        # start_sec / end_sec
        try:
            start = float(row["start_sec"])
            end = float(row["end_sec"])
        except (ValueError, TypeError):
            result.errors.append(f"{label}: start_sec/end_sec must be numeric")
            invalid_rows.add(i)
            continue

        if start < 0:
            result.errors.append(f"{label}: start_sec must be >= 0 (got {start})")
            invalid_rows.add(i)

        if end <= start:
            result.errors.append(
                f"{label}: end_sec must be > start_sec (got {start} -> {end})"
            )
            invalid_rows.add(i)
        else:
            duration = end - start
            if not (5.0 <= duration <= 10.0):
                result.warnings.append(
                    f"{label}: duration {duration:.1f}s is outside recommended 5~10s"
                )

        # group (optional column, warn if value is unexpected)
        if "group" in df.columns:
            group_val = str(row.get("group", "")).strip()
            if group_val and group_val != "nan" and group_val not in VALID_GROUPS:
                result.warnings.append(
                    f"{label}: group {group_val!r} is not one of "
                    f"{sorted(VALID_GROUPS)}"
                )

    # Duplicate IDs
    for col in ("source_id", "candidate_id"):
        dupes = df[col][df[col].duplicated()].tolist()
        if dupes:
            result.errors.append(f"Duplicate {col} values: {dupes}")

    valid_indices = [i for i in df.index if i not in invalid_rows]
    result.valid_rows = len(valid_indices)
    result.valid_df = df.loc[valid_indices].reset_index(drop=True)
    return result
