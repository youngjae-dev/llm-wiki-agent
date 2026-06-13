# AGENTS.md — LLM Wiki 유지보수 에이전트 행동 지침

> **매 세션 시작 시 이 파일과 `journal.md`의 마지막 10줄을 먼저 읽어라.**  
> 이 파일이 너의 작업 방식 전부다.

---

## 0. 이 위키가 무엇인가

**LLM Wiki**는 LLM 에이전트가 유지보수하는 Markdown 전용 지식 베이스다.

- **저장소**: Markdown 파일만 사용. DB 없음.
- **운영 주체**: LLM 에이전트 (Claude, Codex, Gemini 등)
- **사용자 인터페이스**: 파일 읽기 / CLI 질의
- **진입점**: `index.md` → `wiki/*.md`
- **구조 규칙**: `SCHEMA.md` 참고

```
raw/ → pipeline/ingest.py → wiki/*.md → index.md
                                       ↑
                              (사용자 질의 시 갱신)
```

---

## 1. 역할 정의

이 위키를 관리하는 에이전트는 세 가지 모드로 동작한다.

### 1-A. Ingestion Agent (원본 → 위키 변환)

**트리거**: `raw/`에 새 파일이 생겼을 때, 또는 사용자가 `pipeline/ingest.py`를 실행할 때.

**책임**:
1. 원본 파일(PDF, 텍스트)에서 핵심 내용 추출
2. `SCHEMA.md`의 템플릿에 맞는 위키 페이지 생성
3. `index.md`에 항목 추가
4. `journal.md`에 기록 append

**금지**:
- 원본 파일(`raw/`) 수정 또는 삭제
- `journal.md` 기존 내용 수정

### 1-B. Query Agent (사용자 질의 처리)

**트리거**: 사용자가 위키에서 개념을 검색하거나 질문할 때.

**책임**:
1. `index.md`에서 관련 페이지 탐색
2. 해당 `wiki/*.md` 파일 읽기
3. 답변 생성
4. 답변에 사용한 페이지가 없거나 불충분하면 → Maintenance Agent 호출

### 1-C. Maintenance Agent (위키 갱신)

**트리거**: 페이지 누락, 오류 발견, 사용자 요청.

**책임**:
1. 새 페이지 생성 또는 기존 페이지 보강
2. 깨진 내부 링크 수정
3. `index.md` 갱신
4. `journal.md` 기록

---

## 2. 작업 시작 전

1. `journal.md` 마지막 10줄 읽기 — 직전 상태 파악
2. `SCHEMA.md` 전체 읽기 — 구조 규칙 확인
3. `index.md` 읽기 — 현재 위키 전체 파악
4. 작업 대상 `wiki/*.md` 읽기

가정하지 말고 파일을 먼저 읽어라.

---

## 3. 페이지 생성 절차

```
1. SCHEMA.md 읽기
2. 원본 내용 분석 (핵심 개념 추출)
3. 슬러그 결정: NN-kebab-case (현재 최대 순번 + 1)
4. 프론트매터 작성 (전체 필드 필수)
5. 본문 작성 (Overview → Key Concepts → Details → Examples → Related)
6. 최소 1개 내부 링크 [[slug]] 포함
7. wiki/<slug>.md 저장
8. index.md에 항목 추가
9. journal.md에 한 줄 append
```

---

## 4. 페이지 갱신 절차

```
1. 기존 페이지 읽기
2. 변경 사항 최소화 (필요한 부분만 수정)
3. 프론트매터의 version +1, date 갱신
4. journal.md에 한 줄 append: "Updated wiki/XX-slug.md vN→vN+1 — <이유>"
```

---

## 5. User Query 처리 절차

사용자가 개념을 질의할 때:

```
1. index.md에서 관련 슬러그 탐색
2. 해당 wiki/*.md 읽기
3. 답변 생성
4. 답변 끝에 출처 명시: "Source: [[slug]]"
```

관련 페이지가 없으면:
```
1. "이 개념은 아직 위키에 없습니다. 생성하겠습니까?" 묻기
2. 사용자 승인 시 → Maintenance Agent로 페이지 생성
```

---

## 6. 절대 하지 마라

- `raw/` 파일 수정·삭제
- `journal.md` 기존 내용 수정 (오직 append)
- `SCHEMA.md` 구조 임의 변경 (사용자 승인 필요)
- 한 세션에서 3개 이상의 페이지 동시 생성 (quality 저하)
- 존재하지 않는 페이지로의 링크를 확인 없이 사용
- `index.md` 기존 항목 삭제 (비활성화만 허용)

---

## 7. 막히면

- 원본 내용이 모호하면 사용자에게 질문하라. 추측하지 마라.
- 같은 방법으로 3번 실패하면 멈추고 `journal.md`에 상황 기록 후 보고하라.
- 슬러그 충돌이 발생하면 순번을 조정하고 사용자에게 알려라.

---

## 8. 파이프라인 실행

새 raw 파일이 있을 때:

```bash
# 단일 파일
python pipeline/ingest.py "raw/파일명.pdf"

# 전체 raw/ 디렉토리 (미처리 파일만)
python pipeline/ingest.py --all
```

파이프라인은 자동으로:
- pdftotext로 텍스트 추출
- Claude CLI로 위키 페이지 생성
- index.md 갱신
- journal.md 기록

---

## 9. 에이전트 간 핸드오프

멀티-에이전트 환경에서는 핸드오프 파일을 사용한다.

```
pipeline/workspace/
├── 00_raw_extract.md      # 원본 추출 결과
├── 01_wiki_draft.md       # 위키 초안
├── 02_review.md           # 검토 결과
└── 03_final.md            # 최종 페이지
```

각 에이전트는 자신의 단계 파일만 수정한다.

---

## 10. 위키 품질 체크리스트

페이지 저장 전:

- [ ] 프론트매터 전체 필드 있음
- [ ] Overview가 독립적으로 이해 가능
- [ ] 최소 1개 내부 링크 `[[...]]`
- [ ] Related 섹션 최소 1항목
- [ ] 코드 블록에 언어 명시
- [ ] journal.md에 기록 추가됨
- [ ] index.md에 항목 추가됨

---

## 11. MCP Tool 에이전트 SPEC (과제 2 — ArchWiki)

> 이 섹션은 MCP 서버(`mcp_server.py`)를 통해 동작하는 에이전트 및 Streamlit GUI 에이전트에 대한 명세다.

### 11-A. MCP Wiki Agent

MCP 클라이언트(Claude Desktop, Claude CLI 등)가 `mcp_server.py`를 통해 위키를 도구로 활용할 때의 에이전트.

**역할**: 사용자의 아키텍처 설계 질문에 위키 지식을 근거로 답변

**허용된 MCP Tool 목록**:

| Tool | 권한 | 설명 |
|---|---|---|
| `wiki_list_pages` | 읽기 | 전체 페이지 목록 조회 |
| `wiki_get_page` | 읽기 | 단일 페이지 내용 조회 |
| `wiki_search` | 읽기 | 키워드 기반 검색 |
| `wiki_get_related` | 읽기 | 연관 페이지 탐색 |
| `wiki_get_index` | 읽기 | 전체 목차 조회 |
| `wiki_get_journal` | 읽기 | 감사 로그 조회 |
| `wiki_create_page` | 쓰기 | 새 페이지 생성 (사용자 승인 시) |
| `wiki_update_page` | 쓰기 | 기존 페이지 수정 (사용자 승인 시) |
| `wiki_append_journal` | 쓰기 | 감사 로그 추가 (자동) |

**금지 행동**:
- 사용자 승인 없이 `wiki_create_page` / `wiki_update_page` 실행
- `raw/` 디렉토리 접근 (MCP Tool 미노출)
- journal.md 기존 내용 덮어쓰기 (`append_journal`만 허용)

**응답 규칙**:
- 답변에 근거로 사용한 위키 페이지를 반드시 명시 (`출처: wiki/slug.md`)
- 관련 페이지가 없을 경우 "해당 내용이 아직 위키에 없습니다"로 안내
- 한국어로 질문 시 한국어로 답변

---

### 11-B. GUI Chat Agent (Streamlit 위키 에이전트)

`app.py`의 우측 채팅 패널에서 동작하는 에이전트.

**역할**: 현재 위키 페이지 컨텍스트 기반 아키텍처 설계 자문

**동작 방식**:
```
사용자 질문
    ↓
wiki_core.search(질문) → 관련 페이지 3개 추출
    ↓
현재 페이지 본문 + 검색 결과 → 컨텍스트 구성
    ↓
subprocess.run(["claude", "-p", ...]) → Claude CLI 호출
    ↓
JSON 응답 파싱 → 채팅 패널에 표시
```

**컨텍스트 구성 규칙**:
- 현재 열람 중인 위키 페이지 본문 (최대 1,500자)
- 검색 기반 관련 페이지 스니펫 (상위 3개)
- 시스템 프롬프트: ArchWiki Agent 역할 명시, 한국어 응답 지시

**권한**:
- 위키 파일 읽기: 허용 (`wiki_core` 직접 호출)
- 위키 파일 쓰기: 허용하지 않음 (읽기 전용 채팅 에이전트)
- journal.md 수정: 금지

**오류 처리**:
- Claude CLI 미설치: "[오류] Claude CLI를 찾을 수 없습니다" 메시지 표시
- 응답 시간 초과(60초): "[오류] 에이전트 응답 시간 초과" 메시지 표시

---

### 11-C. 에이전트 권한 요약표

| 에이전트 | 위키 읽기 | 위키 쓰기 | journal append | raw 접근 |
|---|---|---|---|---|
| Ingestion Agent (1-A) | ✅ | ✅ | ✅ | ✅ (읽기만) |
| Query Agent (1-B) | ✅ | ❌ | ❌ | ❌ |
| Maintenance Agent (1-C) | ✅ | ✅ | ✅ | ❌ |
| MCP Wiki Agent (11-A) | ✅ | ✅ (승인 시) | ✅ | ❌ |
| GUI Chat Agent (11-B) | ✅ | ❌ | ❌ | ❌ |
