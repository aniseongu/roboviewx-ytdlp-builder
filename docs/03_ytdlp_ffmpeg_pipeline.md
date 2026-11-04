# 03. yt-dlp + ffmpeg pipeline

## Pipeline

```text
confirmed_segments.csv
→ validate technical fields
→ yt-dlp download
→ ffmpeg segment extraction
→ dataset_items.csv
```

## yt-dlp command template

```bash
yt-dlp \
  --ignore-config \
  --no-playlist \
  -f "bestaudio/best" \
  --write-info-json \
  -P "data/downloads/raw" \
  -o "%(id)s.%(ext)s" \
  "YOUTUBE_URL"
```

## Why these options?

```text
--ignore-config : 사용자 전역 설정 영향 방지
--no-playlist  : 실수로 playlist 전체 다운로드 방지
-f bestaudio/best : 오디오 우선 다운로드
--write-info-json : source metadata 저장
-o "%(id)s.%(ext)s" : YouTube ID 기반 파일명
```

## ffmpeg command template

```bash
ffmpeg -y \
  -ss START_SEC \
  -i "RAW_AUDIO_PATH" \
  -t DURATION_SEC \
  -ac 1 \
  -ar 16000 \
  "OUTPUT_WAV_PATH"
```

## Output path

```text
data/segments/{group}/{label_code}/{dataset_item_id}.wav
```

Example:

```text
data/segments/intrusion/INTRUSION_FOOTSTEP/ds_000001.wav
```

## Log file

```text
logs/download_log.csv
```

Columns:

```csv
timestamp,source_id,candidate_id,step,status,message,output_path
```
