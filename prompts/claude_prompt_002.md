# Claude prompt 002: yt-dlp downloader for confirmed list

Implement:

```bash
python -m youtube_segment_builder.cli download-audio \
  --input data/input/confirmed_segments.csv \
  --raw-dir data/downloads/raw \
  --log logs/download_log.csv
```

## Requirements

- Read confirmed_segments.csv.
- Use all rows that pass technical validation.
- Do not check permission_status.
- Do not require permission_evidence_path.
- Use yt-dlp through Python subprocess.
- Do not use shell=True.
- Always include:
  - --ignore-config
  - --no-playlist
  - -f bestaudio/best
  - --write-info-json
  - -o "%(id)s.%(ext)s"
- Skip download if a raw file for the same ytid already exists.
- Log success/failure to CSV.
- Continue if one video fails.

## Do not implement

- cookies
- login
- playlist download
- search crawling
- restriction bypass

## Stop after this task

Show changed files and sample command.
