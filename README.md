# EditFlow

EditFlow는 한국 유튜브/라이브 방송 편집자가 긴 방송 원본에서
하이라이트 후보를 빠르게 찾고, Premiere Pro에서 바로 검수할 수 있는
마커 파일을 만들기 위해 개발한 편집 보조 도구입니다.

긴 생방송 편집은 채팅 반응, 다시보기 반복 시청 구간, 편집자의 수동 감각을
오가며 후보 구간을 찾는 시간이 많이 듭니다. EditFlow는 이 중 반복 가능한
부분을 자동화해 “어디부터 봐야 하는지”를 먼저 정리해 주는 것을 목표로 합니다.

현재 버전은 MVP입니다. 영상 자체를 분석하기보다, 채팅 로그와 히트맵 데이터를
입력받아 반응이 강한 구간을 찾고 Premiere Pro 마커 XML과 CSV 리포트로
내보내는 흐름에 집중합니다.

## 개발 목적

- 긴 라이브 방송에서 숏폼/하이라이트 후보 구간을 빠르게 추리는 것
- 채팅 반응과 반복 시청 데이터를 함께 보고 우선순위를 매기는 것
- 편집자가 Premiere Pro 타임라인에서 바로 확인할 수 있는 마커를 만드는 것
- CLI, API, 브라우저 UI가 같은 분석 파이프라인을 사용하게 만드는 것
- 이후 YouTube API 수집, 자막, 장면 분석, 편집툴 패널로 확장할 수 있는
  기반을 만드는 것

## 현재 제공 기능

- 채팅 CSV/JSON 입력
- 히트맵 CSV/JSON 입력
- 채팅량, 웃음 토큰, 히트맵 점수를 기준으로 피크 탐지
- 채팅 피크와 히트맵 피크가 겹치는 구간을 S/A/B 등급 마커로 분류
- 가까운 피크 병합, 최대 마커 수 제한, 최소 마커 간격 적용
- 프리롤과 마커 길이를 반영한 Premiere Pro XML 출력
- 사람이 읽기 쉬운 timecode가 포함된 CSV 리포트 출력
- CLI, FastAPI, 정적 Workbench UI 지원

## 전체 흐름

```mermaid
flowchart LR
    A["Video / Chat / Heatmap 입력"] --> B["CSV 또는 JSON 파싱"]
    B --> C["채팅 반응 피크 탐지"]
    B --> D["히트맵 피크 탐지"]
    C --> E["피크 병합 및 등급 분류"]
    D --> E
    E --> F["Premiere XML 생성"]
    E --> G["CSV 리포트 생성"]
    F --> H["편집자가 Premiere Pro에서 검수"]
    G --> H
```

분석 등급은 다음 기준으로 나뉩니다.

- `S`: 채팅 피크와 히트맵 피크가 겹친 핵심 후보
- `A`: 채팅 반응이 강한 후보
- `B`: 히트맵 점수가 높은 후보

## 입력 포맷

채팅 CSV:

```csv
second,message
10,ㅋㅋㅋ
10,미쳤다
11,좋다
```

히트맵 CSV:

```csv
second,score
10,0.7
11,0.9
```

JSON은 같은 키를 가진 객체 배열을 사용합니다.

```json
[
  { "second": 10, "message": "ㅋㅋㅋ" }
]
```

## 결과물

CLI 실행 시 기본 결과물은 다음과 같습니다.

- `editflow_markers.xml`: Premiere Pro로 가져올 마커 XML
- `editflow_markers.csv`: 편집자가 확인할 CSV 리포트
- `editflow_manifest.json`: 실행 설정, 입력 파일, 결과 요약

CSV 리포트에는 초 단위 시간, timecode, 등급, 근거, confidence가 포함됩니다.

## 실행 방법

### CLI

저장소 루트에서 실행합니다.

```bash
PYTHONPATH=src JJonyeok2/bin/python -m editflow.cli analyze \
  --chat examples/chat.csv \
  --heatmap examples/heatmap.csv \
  --out outputs \
  --max-markers 20 \
  --peak-merge-seconds 2 \
  --min-marker-gap-seconds 8 \
  --pre-roll-seconds 2 \
  --marker-duration-seconds 5
```

패키지 설치 후에는 `editflow` 엔트리포인트로도 실행할 수 있습니다.

### API

API 서버를 실행합니다.

```bash
JJonyeok2/bin/python -m uvicorn editflow.api:api \
  --app-dir src \
  --host 127.0.0.1 \
  --port 8000
```

분석 요청 예시:

```bash
curl -X POST http://127.0.0.1:8000/analyze \
  -H 'Content-Type: application/json' \
  -d '{
    "chat_text": "second,message\n10,ㅋㅋ\n10,ㅋㅋㅋ\n10,미쳤다\n",
    "chat_filename": "chat.csv",
    "heatmap_text": "second,score\n11,0.9\n",
    "heatmap_filename": "heatmap.csv",
    "fps": 30,
    "min_messages": 3,
    "min_laughs": 2,
    "min_heatmap_score": 0.75,
    "overlap_seconds": 5,
    "max_markers": 20,
    "peak_merge_seconds": 2,
    "min_marker_gap_seconds": 8,
    "pre_roll_seconds": 2,
    "marker_duration_seconds": 5
  }'
```

### Workbench UI

정적 UI는 설치 없이 로컬 서버로 열 수 있습니다.

```bash
python3 -m http.server 8766 --bind 127.0.0.1 --directory web
```

브라우저에서 엽니다.

```text
http://127.0.0.1:8766/index.html
```

UI의 기본 화면은 업로드와 분석 실행만 노출합니다. 세부 튜닝 값은
`Advanced` 패널 안에 숨겨져 있으며, 필요할 때만 열어 조정합니다.

## 프로젝트 구조

```text
src/editflow/
  ingest/        CSV/JSON 입력 파서
  analysis/      피크 탐지, 마커 분류, 후처리
  exporters/     Premiere XML, CSV, manifest 출력
  pipeline.py    CLI/API가 공유하고 UI가 API를 통해 호출하는 분석 오케스트레이션
  cli.py         명령줄 인터페이스
  api.py         FastAPI 백엔드

web/
  index.html     정적 Workbench UI
  styles.css     실무형 편집 UI 스타일
  src/           UI 모듈, API 호출, 로컬 fallback 분석, 렌더링

examples/        샘플 채팅/히트맵 데이터
tests/           파서, 분석, 출력, CLI/API/UI 테스트
```

## YouTube API 연동 방향

현재 자동 수집은 아직 제품 기능으로 고정하지 않았습니다. YouTube는 임의
페이지 크롤링보다 공식 YouTube Data API와 Live Streaming API를 우선해야 합니다.

현실적인 다음 단계는 다음 흐름입니다.

```text
YouTube URL 입력
→ videoId 추출
→ videos.list로 liveStreamingDetails 조회
→ activeLiveChatId 확인
→ liveChatMessages.list 또는 streamList로 라이브 채팅 수집
→ publishedAt - actualStartTime으로 second 계산
→ second,message 형식으로 변환
→ 기존 EditFlow 분석 파이프라인에 전달
```

주의할 점:

- `activeLiveChatId`는 현재 라이브 중인 방송에서만 안정적으로 사용할 수 있습니다.
- 방송이 끝난 다시보기 채팅 리플레이는 공식 API로 안정적인 수집 범위가 아닙니다.
- 유튜브 히트맵도 현재 공식 Data API에서 일반적으로 가져올 수 있는 데이터가
  아니므로, MVP에서는 파일 업로드 흐름을 유지합니다.
- API key는 프론트엔드에 넣지 않고 백엔드 환경변수로 보관해야 합니다.
  예: `YOUTUBE_API_KEY=...`

## 현재 범위와 제한

현재 EditFlow는 “하이라이트 후보를 추천하는 도구”입니다. 최종 편집 판단,
저작권 판단, 맥락 판단은 편집자가 해야 합니다.

아직 포함하지 않은 범위:

- 영상 프레임/오디오 직접 분석
- Whisper 기반 자막 분석
- OCR, 표정, 장면 전환 탐지
- YouTube 다시보기 채팅 리플레이 자동 수집
- Adobe UXP 패널
- 사용자 계정, DB, 작업 이력 관리

## 검증

전체 테스트:

```bash
JJonyeok2/bin/python -m pytest
```

린트:

```bash
JJonyeok2/bin/ruff check .
```

프론트엔드 모듈 문법 확인:

```bash
node --check web/src/main.js
node --check web/src/api.js
node --check web/src/analysis.js
node --check web/src/data.js
node --check web/src/exporters.js
node --check web/src/render.js
node --check web/src/config.js
node --check web/src/state.js
```
