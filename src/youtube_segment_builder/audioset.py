from __future__ import annotations

import shutil
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path

import pandas as pd

# Official AudioSet metadata CSVs are static files hosted by Google.
# Downloading them is a plain file fetch — not YouTube search / scraping / playlist.
AUDIOSET_BASE_URL = "http://storage.googleapis.com/us_audioset/youtube_corpus/v1/csv/"

CLASS_LABELS_FILE = "class_labels_indices.csv"

SEGMENT_FILES = {
    "balanced": "balanced_train_segments.csv",
    "eval": "eval_segments.csv",
    "unbalanced": "unbalanced_train_segments.csv",
}

# Which segment files each --split value pulls. class_labels_indices.csv is always
# downloaded. unbalanced is only fetched when explicitly asked (unbalanced / all).
SPLIT_TO_SEGMENTS = {
    "default": ["balanced", "eval"],
    "balanced": ["balanced"],
    "eval": ["eval"],
    "unbalanced": ["unbalanced"],
    "all": ["balanced", "eval", "unbalanced"],
}

CANDIDATE_COLUMNS = [
    "candidate_id",
    "source_id",
    "ytid",
    "youtube_url",
    "preview_url",
    "target_label",
    "label_code",
    "is_intrusion",
    "group",
    "audioset_start_sec",
    "audioset_end_sec",
    "clip_start_sec",
    "clip_end_sec",
    "audioset_mids",
    "audioset_label_names",
    "selected",
    "creator_name",
    "video_title",
    "attribution_text",
    "notes",
]

# Columns a human may edit in audioset_candidates.csv; preserved across regeneration
# (matched by candidate_id) so manual work is never overwritten.
PRESERVE_COLUMNS = [
    "selected",
    "clip_start_sec",
    "clip_end_sec",
    "creator_name",
    "video_title",
    "attribution_text",
    "notes",
]

EXAMPLE_TARGETS = (
    "target_label,label_code,is_intrusion,group,audioset_mids,max_candidates\n"
    "footsteps,INTRUSION_FOOTSTEP,true,intrusion,/m/07pbtc8,200\n"
    "speech,NONINTR_SPEECH,false,non_intrusion,/m/09x0r,100\n"
)


# --------------------------------------------------------------------------- #
# download-audioset-csv
# --------------------------------------------------------------------------- #
@dataclass
class DownloadCsvResult:
    downloaded: list[str] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)
    failed: list[tuple[str, str]] = field(default_factory=list)


def _download_file(url: str, target: Path, timeout: int) -> None:
    """Stream a URL to target atomically via a .part temp file."""
    tmp = target.with_suffix(target.suffix + ".part")
    with urllib.request.urlopen(url, timeout=timeout) as resp:  # noqa: S310 (static https host)
        with open(tmp, "wb") as fh:
            shutil.copyfileobj(resp, fh)
    tmp.replace(target)


def download_audioset_csv(
    split: str,
    dest: str,
    overwrite: bool = False,
    timeout: int = 120,
) -> DownloadCsvResult:
    result = DownloadCsvResult()

    segments = SPLIT_TO_SEGMENTS.get(split)
    if segments is None:
        raise ValueError(
            f"Unknown split {split!r}. Choose from {sorted(SPLIT_TO_SEGMENTS)}"
        )

    dest_dir = Path(dest)
    dest_dir.mkdir(parents=True, exist_ok=True)

    files = [CLASS_LABELS_FILE] + [SEGMENT_FILES[s] for s in segments]

    for filename in files:
        target = dest_dir / filename
        if target.exists() and not overwrite:
            result.skipped.append(filename)
            print(f"  [SKIP] {filename} — already exists")
            continue

        print(f"  [GET]  {filename}")
        try:
            _download_file(AUDIOSET_BASE_URL + filename, target, timeout)
            result.downloaded.append(filename)
            print(f"         -> OK  {target}")
        except Exception as exc:  # keep going; one bad file must not abort the batch
            result.failed.append((filename, str(exc)))
            print(f"         -> FAILED: {exc}")

    return result


# --------------------------------------------------------------------------- #
# make-audioset-candidates
# --------------------------------------------------------------------------- #
@dataclass
class Target:
    target_label: str
    label_code: str
    is_intrusion: str
    group: str
    mids: set[str]
    max_candidates: int | None


@dataclass
class CandidatesResult:
    total_segments: int = 0
    matched: int = 0
    preserved: int = 0
    dropped: int = 0
    per_target: dict[str, int] = field(default_factory=dict)
    output_path: str = ""


def write_example_targets(path: str | Path) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(EXAMPLE_TARGETS, encoding="utf-8")


def _load_targets(path: Path) -> list[Target]:
    df = pd.read_csv(path, dtype=str).fillna("")
    required = {"target_label", "label_code", "is_intrusion", "group", "audioset_mids"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"targets CSV missing columns: {sorted(missing)}")

    targets: list[Target] = []
    for _, row in df.iterrows():
        mids = {m.strip() for m in str(row["audioset_mids"]).split(";") if m.strip()}
        if not mids:
            continue
        raw_max = str(row.get("max_candidates", "")).strip()
        max_candidates = int(float(raw_max)) if raw_max else None
        targets.append(
            Target(
                target_label=str(row["target_label"]).strip(),
                label_code=str(row["label_code"]).strip(),
                is_intrusion=str(row["is_intrusion"]).strip(),
                group=str(row["group"]).strip(),
                mids=mids,
                max_candidates=max_candidates,
            )
        )
    return targets


def _load_class_labels(path: Path) -> dict[str, str]:
    df = pd.read_csv(path)
    return dict(zip(df["mid"].astype(str), df["display_name"].astype(str)))


def _read_segments(path: Path) -> pd.DataFrame:
    # AudioSet segment CSVs begin with '#'-prefixed comment lines, use ", " separators,
    # and quote the positive_labels field (which itself contains commas).
    return pd.read_csv(
        path,
        comment="#",
        header=None,
        names=["ytid", "start_sec", "end_sec", "positive_labels"],
        skipinitialspace=True,
        quotechar='"',
        dtype={"ytid": str, "positive_labels": str},
    )


def _load_existing(output: Path) -> dict[str, dict]:
    if not output.exists():
        return {}
    old = pd.read_csv(output, dtype=str).fillna("")
    if "candidate_id" not in old.columns:
        return {}
    return {str(r["candidate_id"]): dict(r) for _, r in old.iterrows()}


def make_candidates(
    audioset_dir: str,
    targets_path: str,
    output_path: str,
) -> CandidatesResult:
    result = CandidatesResult(output_path=output_path)

    audio_dir = Path(audioset_dir)
    targets = _load_targets(Path(targets_path))
    labels = _load_class_labels(audio_dir / CLASS_LABELS_FILE)
    result.per_target = {t.target_label: 0 for t in targets}

    output = Path(output_path)
    existing = _load_existing(output)

    rows: list[dict] = []
    seen_ids: set[str] = set()

    for split, filename in SEGMENT_FILES.items():
        seg_path = audio_dir / filename
        if not seg_path.exists():
            continue

        seg = _read_segments(seg_path)
        result.total_segments += len(seg)

        for _, srow in seg.iterrows():
            ytid = str(srow["ytid"]).strip()
            try:
                start = float(srow["start_sec"])
                end = float(srow["end_sec"])
            except (ValueError, TypeError):
                continue

            mid_list = [
                m.strip()
                for m in str(srow["positive_labels"]).split(",")
                if m.strip()
            ]
            mid_set = set(mid_list)

            for t in targets:
                if not (t.mids & mid_set):
                    continue
                if (
                    t.max_candidates is not None
                    and result.per_target[t.target_label] >= t.max_candidates
                ):
                    continue

                candidate_id = f"cand_{t.target_label}_{ytid}"
                if candidate_id in seen_ids:
                    continue
                seen_ids.add(candidate_id)

                row = {
                    "candidate_id": candidate_id,
                    "source_id": f"audioset_{split}_{ytid}",
                    "ytid": ytid,
                    "youtube_url": f"https://www.youtube.com/watch?v={ytid}",
                    "preview_url": (
                        f"https://www.youtube.com/watch?v={ytid}&t={int(start)}s"
                    ),
                    "target_label": t.target_label,
                    "label_code": t.label_code,
                    "is_intrusion": t.is_intrusion,
                    "group": t.group,
                    "audioset_start_sec": start,
                    "audioset_end_sec": end,
                    "clip_start_sec": start,
                    "clip_end_sec": end,
                    "audioset_mids": ";".join(mid_list),
                    "audioset_label_names": ";".join(
                        labels.get(m, m) for m in mid_list
                    ),
                    "selected": "NO",
                    "creator_name": "",
                    "video_title": "",
                    "attribution_text": "",
                    "notes": "",
                }

                # Preserve human edits (selected=YES, clip trims, notes, ...)
                if candidate_id in existing:
                    old = existing[candidate_id]
                    for col in PRESERVE_COLUMNS:
                        val = str(old.get(col, "")).strip()
                        if val != "":
                            row[col] = val
                    result.preserved += 1

                rows.append(row)
                result.per_target[t.target_label] += 1
                result.matched += 1

    # Existing candidate_ids that current targets no longer reproduce would lose
    # any selected=YES — report the count so the caller can warn.
    result.dropped = len(set(existing) - seen_ids)

    output.parent.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame(rows, columns=CANDIDATE_COLUMNS)
    df.to_csv(output, index=False)

    return result
