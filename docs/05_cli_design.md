# 05. CLI design

## validate-input

```bash
python -m youtube_segment_builder.cli validate-input \
  --input data/input/confirmed_segments.csv
```

역할:

```text
필수 컬럼 확인
URL/ytid 확인
start_sec/end_sec 확인
group/label_code 확인
중복 source_id/candidate_id 확인
```

권한 여부는 검사하지 않는다.

## download-audio

```bash
python -m youtube_segment_builder.cli download-audio \
  --input data/input/confirmed_segments.csv \
  --raw-dir data/downloads/raw \
  --log logs/download_log.csv
```

역할:

```text
CSV의 모든 valid row에 대해 yt-dlp 다운로드
이미 받은 ytid는 재사용
다운로드 성공/실패 로그 기록
```

## extract-segments

```bash
python -m youtube_segment_builder.cli extract-segments \
  --input data/input/confirmed_segments.csv \
  --raw-dir data/downloads/raw \
  --out-dir data/segments \
  --dataset-items-out data/metadata/dataset_items.csv \
  --sample-rate 16000
```

역할:

```text
다운로드된 raw audio에서 start_sec~end_sec 추출
mono 16kHz WAV 생성
dataset_items.csv 생성
```

## run-all

```bash
python -m youtube_segment_builder.cli run-all \
  --input data/input/confirmed_segments.csv
```

흐름:

```text
validate-input
→ download-audio
→ extract-segments
→ summary 출력
```
