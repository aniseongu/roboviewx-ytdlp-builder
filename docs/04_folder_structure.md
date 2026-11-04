# 04. Folder structure

```text
youtube-segment-builder/
├─ CLAUDE.md
├─ README.md
├─ data/
│  ├─ input/
│  │  └─ confirmed_segments.csv
│  ├─ downloads/
│  │  ├─ raw/
│  │  └─ infojson/
│  ├─ segments/
│  │  ├─ intrusion/
│  │  ├─ non_intrusion/
│  │  └─ robot_noise/
│  └─ metadata/
│     └─ dataset_items.csv
├─ docs/
├─ prompts/
├─ logs/
│  └─ download_log.csv
├─ src/
│  └─ youtube_segment_builder/
│     ├─ __init__.py
│     ├─ cli.py
│     ├─ input_manifest.py
│     ├─ downloader.py
│     ├─ segmenter.py
│     ├─ metadata.py
│     └─ logging_utils.py
└─ tests/
```
