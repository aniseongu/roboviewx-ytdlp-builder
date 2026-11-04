<div align="center">

# YouTube Segment Builder

사람이 확인한 YouTube 구간 목록으로 침입 탐지 학습용 오디오를 내려받는 Python CLI

![Python](https://img.shields.io/badge/Python-3.10+-124532?logo=python&logoColor=white)
![yt-dlp](https://img.shields.io/badge/yt--dlp-555555)
![status](https://img.shields.io/badge/status-구간%20추출%20미구현-555555)

</div>

## 소개

이 도구는 사람이 확인한 YouTube 구간을 오디오 데이터셋으로 준비하는 Python CLI입니다.

Google AudioSet에서 발소리, 말소리 같은 라벨이 붙은 YouTube 구간을 후보로 뽑고, 사람이 출처와 사용 가능 여부를 확인해 고른 행만 다운로드합니다. 검색 결과를 긁어 오거나 재생목록을 통째로 받지 않습니다.

## 흐름

```text
AudioSet 구간 CSV 다운로드
→ 대상 라벨별 후보 목록 생성 (audioset_candidates.csv)
→ 사람이 듣고 확인한 행에 selected=YES 표시
→ confirmed_segments.csv 생성
→ URL·시간·라벨 형식 검사
→ yt-dlp로 원본 오디오 다운로드, 결과는 download_log.csv에 기록
```

ffmpeg로 지정 구간을 잘라 16kHz 모노 WAV로 만드는 단계는 아직 구현하지 않았습니다. 설계는 `docs/03_ytdlp_ffmpeg_pipeline.md`에 있습니다.

## 명령

| 명령 | 하는 일 |
| --- | --- |
| `download-audioset-csv` | AudioSet 구간 CSV와 클래스 목록을 `data/audioset/`에 받습니다. 기본은 balanced와 eval이고, unbalanced는 따로 지정해야 받습니다. |
| `make-audioset-candidates` | `data/config/audioset_targets.csv`의 라벨별로 후보 구간을 뽑습니다. 다시 만들어도 사람이 고친 선택 표시와 구간은 유지합니다. |
| `build-confirmed-from-candidates` | `selected`가 YES인 행만 `confirmed_segments.csv`로 옮깁니다. 기존 파일은 `.bak`으로 백업합니다. |
| `validate-input` | 필수 열, URL 형식, 시작·끝 시간, 라벨 코드, 중복 ID를 검사합니다. 구간이 5~10초를 벗어나면 경고만 냅니다. |
| `download-audio` | yt-dlp로 원본 오디오를 받습니다. 이미 받은 영상과 같은 실행 안에서 겹치는 영상은 건너뛰고, 한 건이 실패해도 나머지는 계속 받습니다. |

yt-dlp는 항상 `--ignore-config --no-playlist`로 부르고, `shell=True`는 쓰지 않습니다. 한 건당 제한 시간은 300초입니다.

## 설치

Python 3.10 이상과 ffmpeg가 필요합니다.

```bash
git clone https://github.com/aniseongu/youtube-segment-builder.git
cd youtube-segment-builder
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
sudo apt install -y ffmpeg
```

## 사용법

```bash
python -m youtube_segment_builder.cli download-audioset-csv
python -m youtube_segment_builder.cli make-audioset-candidates

# data/candidates/audioset_candidates.csv를 열어 확인한 행의 selected를 YES로 바꾼다

python -m youtube_segment_builder.cli build-confirmed-from-candidates
python -m youtube_segment_builder.cli validate-input
python -m youtube_segment_builder.cli download-audio
```

대상 라벨은 `data/config/audioset_targets.csv`에서 바꿉니다. 지금은 침입 쪽 발소리(`INTRUSION_FOOTSTEP`)와 비침입 쪽 말소리(`NONINTR_SPEECH`) 두 개가 들어 있습니다.

## 주의

- 코드는 사용 허락 여부를 검사하지 않습니다. `confirmed_segments.csv`에 들어온 행은 팀이 이미 확인한 것으로 봅니다.
- 쿠키, 로그인, DRM, 비공개·연령·지역 제한을 우회하는 기능은 넣지 않았습니다.
- 내려받은 음원과 후보·확정 CSV는 `.gitignore`로 저장소에서 뺐습니다.

## 폴더 구조

```text
src/youtube_segment_builder/   CLI와 단계별 모듈
data/config/                    대상 라벨 설정
data/input/                     confirmed_segments 양식
docs/                           범위, 입력 형식, 파이프라인, CLI 설계 메모
```
