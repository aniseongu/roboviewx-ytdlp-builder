# 06. WSL start

## 1. projects 폴더 이동

```bash
mkdir -p ~/projects
cd ~/projects
```

## 2. 프로젝트 폴더 생성

```bash
mkdir youtube-segment-builder
cd youtube-segment-builder
```

## 3. 가상환경 생성

```bash
python3 -m venv .venv
source .venv/bin/activate
```

## 4. 패키지 설치

```bash
pip install --upgrade pip
pip install pandas pydantic typer pytest yt-dlp
```

## 5. ffmpeg 설치

```bash
sudo apt update
sudo apt install -y ffmpeg
```

## 6. 확인

```bash
python --version
yt-dlp --version
ffmpeg -version
```

## 7. Claude Code 실행

```bash
claude
```

## 8. 첫 지시

```text
CLAUDE.md와 docs 폴더를 읽어줘.
prompts/claude_prompt_001.md에 따라 validate-input 명령부터 구현해줘.
권한/GRANTED 검사는 만들지 말고, CSV 형식과 시간값 검증만 해줘.
```
