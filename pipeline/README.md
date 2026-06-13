# pipeline/ — LLM Wiki Ingestion Pipeline

raw/ 디렉토리의 원본 파일(PDF, 텍스트)을 받아 wiki/ 페이지로 변환하는 파이프라인.

---

## 아키텍처

```
raw/파일.pdf
    │
    ▼ [1] pdftotext 추출
    텍스트 내용
    │
    ▼ [2] Claude CLI subprocess 호출
    SCHEMA.md 템플릿 기반 위키 페이지 생성
    │
    ▼ [3] wiki/NN-slug.md 저장
    │
    ▼ [4] index.md 갱신 + journal.md 기록
```

**핸드오프 파일** (파이프라인 각 단계 추적용):
```
pipeline/workspace/
├── 00_raw_extract_TIMESTAMP.md   # 원본 추출 결과 미리보기
└── 01_wiki_draft_TIMESTAMP.md    # Claude가 생성한 초안
```

---

## 사전 요구사항

```bash
# pdftotext 설치 (PDF 지원용)
brew install poppler       # macOS
apt-get install poppler-utils  # Linux

# Claude CLI 설치 및 인증
# https://claude.ai/code
claude --version
```

Python 3.10 이상 필요. 추가 패키지 없음 (표준 라이브러리만 사용).

---

## 사용법

### 단일 파일 처리

```bash
# PDF 파일
python pipeline/ingest.py "raw/7. Harness and Skills.pdf"

# 텍스트 파일
python pipeline/ingest.py "raw/notes.txt"
```

### 전체 raw/ 처리 (미처리 파일만)

```bash
python pipeline/ingest.py --all
```

journal.md에 이미 기록된 파일은 자동으로 건너뜀.

### 인라인 텍스트 입력

```bash
python pipeline/ingest.py --text "MCP는 AI용 USB 인터페이스다..." --title "MCP 빠른 참조"
```

### 미리보기 (실제 저장 없이)

```bash
python pipeline/ingest.py --dry-run "raw/파일.pdf"
```

---

## 출력 예시

```
[ingest] 처리 중: 7. Harness and Skills.pdf

  [1/4] 원본 텍스트 추출...
  [workspace] 00_raw_extract_20260613_144000.md
  → 12453 문자 추출됨

  [2/4] Claude로 위키 페이지 생성 중...
  [workspace] 01_wiki_draft_20260613_144015.md

  [3/4] wiki/ 에 저장 중...

  [4/4] index.md / journal.md 갱신 중...

  완료: /Users/.../wiki/07-harness-and-skills.md

생성됨: /Users/.../wiki/07-harness-and-skills.md
```

---

## 생성 파일 명명 규칙

```
NN-kebab-case.md

NN: 현재 최대 순번 + 1 (자동 계산)
kebab-case: 파일명에서 앞의 숫자·점 제거 후 소문자 하이픈 변환

예:
  "7. Harness and Skills.pdf" → "07-harness-and-skills.md"
  "My New Topic.pdf"          → "10-my-new-topic.md"
```

---

## 에러 처리

| 에러 | 원인 | 해결 |
|---|---|---|
| `pdftotext 실패` | poppler 미설치 | `brew install poppler` |
| `Claude CLI 실패` | 인증 만료 또는 미설치 | `claude` 재실행 후 인증 |
| `FileNotFoundError` | 파일 경로 오류 | 경로 확인 (raw/ 기준) |
| `returncode != 0` | Claude API 오류 | stderr 메시지 확인 |

---

## 멀티-에이전트 파이프라인 (고급)

기본 파이프라인은 단일 Claude 호출로 위키 페이지를 생성한다.
품질이 중요한 경우 Planner-Reviewer 구조로 확장 가능:

```python
# 1단계: Claude로 초안 생성
draft = generate_wiki_page(raw_content, source_name, schema, slug)

# 2단계: 두 번째 Claude 호출로 검토
review_prompt = f"다음 위키 페이지 초안을 검토하고 개선하라:\n\n{draft}"
reviewed = call_claude(review_prompt)

# 3단계: 최종 저장
output_path.write_text(reviewed)
```

---

## 관련 파일

- `../SCHEMA.md` — 위키 페이지 구조·형식 규칙
- `../AGENTS.md` — LLM 에이전트 행동 지침
- `../index.md` — 위키 전체 색인 (자동 갱신)
- `../journal.md` — 유지보수 로그 (자동 append)
