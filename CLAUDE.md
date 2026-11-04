# CLAUDE.md

## Project

YouTube Segment Builder

## Goal

Build a Python CLI tool that downloads audio from a human-confirmed YouTube segment list and extracts WAV clips for the audio dataset.

## Important project rule

Do not implement a permission-status gate.

The human team will verify permissions before adding rows to:

```text
data/input/confirmed_segments.csv
```

The code should validate technical fields only:

- required columns
- URL format
- start/end seconds
- label_code
- output path safety
- duplicate IDs

## Do not implement

Do not check:

```text
permission_status == GRANTED
permission_evidence_path exists
```

Do not require a permission manifest.

## Still forbidden

Do not implement:

- YouTube search crawling
- HTML scraping
- playlist bulk downloading
- cookies
- login-based downloads
- DRM bypass
- private video bypass
- age restriction bypass
- geo restriction bypass
- paywall bypass

## Tools

- Python 3.10+
- yt-dlp
- ffmpeg
- pandas
- pydantic
- typer
- pytest

## Pipeline

```text
1. Read data/input/confirmed_segments.csv
2. Validate technical fields
3. Download audio using yt-dlp
4. Extract segment with ffmpeg
5. Save WAV mono 16kHz clip
6. Write data/metadata/dataset_items.csv
7. Write logs/download_log.csv
```

## CLI commands

```bash
python -m youtube_segment_builder.cli validate-input
python -m youtube_segment_builder.cli download-audio
python -m youtube_segment_builder.cli extract-segments
python -m youtube_segment_builder.cli run-all
```

## Implementation style

- Implement one command at a time.
- Use small files.
- Use subprocess safely.
- Always use yt-dlp with `--ignore-config` and `--no-playlist`.
- Do not use shell=True.
- Print clear summaries.
- Log failures instead of crashing the entire batch when one video fails.
