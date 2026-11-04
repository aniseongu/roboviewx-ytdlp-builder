# Claude prompt 003: ffmpeg segment extraction

Implement:

```bash
python -m youtube_segment_builder.cli extract-segments \
  --input data/input/confirmed_segments.csv \
  --raw-dir data/downloads/raw \
  --out-dir data/segments \
  --dataset-items-out data/metadata/dataset_items.csv \
  --sample-rate 16000
```

## Requirements

- Read confirmed_segments.csv.
- Find downloaded raw audio by ytid in raw-dir.
- Compute duration_sec = end_sec - start_sec.
- Use ffmpeg to extract segment.
- Convert to WAV mono 16kHz by default.
- Output path:
  - data/segments/{group}/{label_code}/{dataset_item_id}.wav
- Write dataset_items.csv.
- human_verified defaults to false.
- quality_status defaults to NEEDS_REVIEW.
- download_status records SUCCESS or FAILED.
- Continue if one item fails.

## Stop after this task

Show changed files and sample command.
