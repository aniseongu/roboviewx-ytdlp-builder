# 01. Scope

## 이 도구가 하는 일

사람이 이미 확인한 YouTube 영상 목록을 입력으로 받아 다음을 자동화한다.

```text
다운로드
→ 오디오 추출
→ 지정 초 구간 자르기
→ WAV 변환
→ metadata 생성
```

## 이 도구가 하지 않는 일

```text
허락 여부 판단
GRANTED 상태 확인
permission evidence 파일 확인
YouTube 검색/크롤링
playlist 전체 다운로드
로그인/쿠키 기반 다운로드
제한 우회
```

## 전제

`data/input/confirmed_segments.csv`에는 사람이 확인한 영상만 들어온다.

따라서 코드는 법적/권한 판단을 하지 않고, 기술적인 자동화만 담당한다.
