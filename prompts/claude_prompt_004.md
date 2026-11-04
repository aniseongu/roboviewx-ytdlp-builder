# Claude prompt 004: run-all command

Implement:

```bash
python -m youtube_segment_builder.cli run-all \
  --input data/input/confirmed_segments.csv
```

## Flow

```text
validate-input
→ download-audio
→ extract-segments
→ print summary
```

## Requirements

- Print total rows.
- Print valid rows.
- Print downloaded count.
- Print extracted count.
- Print failed count.
- Do not add permission checking logic.
