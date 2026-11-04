from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from youtube_segment_builder.logging_utils import append_log


@dataclass
class DownloadResult:
    total: int = 0
    downloaded: int = 0
    skipped: int = 0
    failed: int = 0


def _find_raw_file(raw_dir: Path, ytid: str) -> Path | None:
    """Return the downloaded audio file for ytid if it exists (not .json)."""
    for f in raw_dir.glob(f"{ytid}.*"):
        if f.suffix != ".json":
            return f
    return None


def _last_line(text: str) -> str:
    lines = [l for l in text.splitlines() if l.strip()]
    return lines[-1] if lines else ""


def download_audio(
    df: pd.DataFrame,
    raw_dir: str,
    log_path: str,
) -> DownloadResult:
    result = DownloadResult()
    raw = Path(raw_dir)
    raw.mkdir(parents=True, exist_ok=True)

    seen_ytids: set[str] = set()

    for _, row in df.iterrows():
        source_id = str(row["source_id"])
        candidate_id = str(row["candidate_id"])
        ytid = str(row["ytid"]).strip()
        url = str(row["youtube_url"]).strip()

        result.total += 1

        # Same ytid already queued in this batch (multiple segments, one video)
        if ytid in seen_ytids:
            result.skipped += 1
            append_log(
                log_path, source_id, candidate_id,
                "download", "SKIPPED",
                f"ytid {ytid} already processed in this run", "",
            )
            continue

        seen_ytids.add(ytid)

        existing = _find_raw_file(raw, ytid)
        if existing:
            result.skipped += 1
            append_log(
                log_path, source_id, candidate_id,
                "download", "SKIPPED",
                f"raw file already exists: {existing.name}", str(existing),
            )
            print(f"  [SKIP] {ytid} — {existing.name}")
            continue

        print(f"  [DL]   {ytid} — {url}")

        cmd = [
            "yt-dlp",
            "--ignore-config",
            "--no-playlist",
            "-f", "bestaudio/best",
            "--write-info-json",
            "-P", str(raw),
            "-o", "%(id)s.%(ext)s",
            url,
        ]

        try:
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,
            )
            if proc.returncode == 0:
                out_file = _find_raw_file(raw, ytid)
                out_path = str(out_file) if out_file else ""
                result.downloaded += 1
                append_log(
                    log_path, source_id, candidate_id,
                    "download", "SUCCESS", "yt-dlp completed", out_path,
                )
                print(f"         -> OK  {out_path}")
            else:
                stderr = (proc.stderr or proc.stdout or "").strip()
                msg = _last_line(stderr) or "yt-dlp returned non-zero exit"
                result.failed += 1
                append_log(
                    log_path, source_id, candidate_id,
                    "download", "FAILED", msg, "",
                )
                print(f"         -> FAILED: {msg}")

        except subprocess.TimeoutExpired:
            result.failed += 1
            append_log(
                log_path, source_id, candidate_id,
                "download", "FAILED", "timeout after 300s", "",
            )
            print(f"         -> FAILED: timeout after 300s")

        except Exception as exc:
            result.failed += 1
            append_log(
                log_path, source_id, candidate_id,
                "download", "FAILED", str(exc), "",
            )
            print(f"         -> FAILED: {exc}")

    return result
