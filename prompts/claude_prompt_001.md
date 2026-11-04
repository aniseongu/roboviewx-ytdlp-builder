# Claude prompt 001: Technical input validator

Read:

- CLAUDE.md
- docs/01_scope.md
- docs/02_input_schema.md
- docs/05_cli_design.md

Then implement:

```bash
python -m youtube_segment_builder.cli validate-input \
  --input data/input/confirmed_segments.csv
```

## Requirements

- Read CSV with pandas.
- Validate required columns.
- Validate youtube_url exists.
- Validate ytid exists.
- Validate start_sec and end_sec.
- Validate duration_sec = end_sec - start_sec.
- Warn if duration is outside 5~10 seconds, but do not fail.
- Validate group if present:
  - intrusion
  - non_intrusion
  - robot_noise
- Check duplicate source_id/candidate_id.
- Print clear summary.

## Explicit non-requirements

Do not check permission_status.
Do not require permission_evidence_path.
Do not create permission manifest logic.
Do not download anything yet.

## Stop after this task

Show changed files and sample command.
