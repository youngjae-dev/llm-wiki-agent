# PRD: ArchWiki — 개인 프로젝트 아키텍처 설계 보조 위키 툴

**버전**: 1.0  
**작성일**: 2026-06-13  
**작성**: ArchWiki Agent (에이전트 작성)

---

## 1. 제품 개요

### 1.1 한 줄 요약

개발자가 개인 프로젝트를 시작할 때 가장 적합한 시스템 아키텍처를 설계할 수 있도록 돕는 **MCP 기반 위키 에이전트**.

### 1.2 문제 정의

개인 프로젝트를 시작하는 개발자는 다음 문제를 반복적으로 경험한다:

1. **아키텍처 결정 지식 부족**: 어떤 패턴이 이 프로젝트에 적합한지 판단 기준이 없다
2. **설계 실수 반복**: 마이크로서비스 과적용, God Object 등 동일한 안티패턴 반복
3. **결정 맥락 소실**: 왜 이 설계를 선택했는지 나중에 기억하지 못함 (ADR 미작성)
4. **단편적 지식**: 캐싱, DB 스케일링, 통신 방식 등을 개별로 찾아야 하며 종합적 관점이 없음

### 1.3 해결 방안

- 아키텍처 설계 지식을 **위키 페이지**로 구조화
- **MCP 서버**로 AI 에이전트가 위키를 도구로 활용하게 함
- **Streamlit GUI**로 위키 탐색 + 에이전트 채팅을 하나의 인터페이스에서 제공

---

## 2. 사용자 페르소나

| 구분 | 설명 |
|---|---|
| **주요 사용자** | 사이드 프로젝트를 진행하는 주니어~미드레벨 백엔드 개발자 |
| **기술 수준** | REST API 개발 경험 있음, 아키텍처 패턴 학습 중 |
| **고통 포인트** | "어떻게 설계해야 하는지 모르겠다", "나중에 다 고쳐야 했다" |
| **원하는 것** | 프로젝트 특성을 말하면 최적 설계를 추천받고 싶다 |

---

## 3. 기능 요구사항

### 3.1 Must Have (MVP)

| ID | 기능 | 구현 방법 |
|---|---|---|
| F-01 | 위키 페이지 목록 조회 | `wiki_list_pages` MCP Tool |
| F-02 | 위키 페이지 내용 조회 | `wiki_get_page` MCP Tool |
| F-03 | 키워드 검색 | `wiki_search` MCP Tool |
| F-04 | 관련 페이지 탐색 | `wiki_get_related` MCP Tool |
| F-05 | 전체 목차 조회 | `wiki_get_index` MCP Tool |
| F-06 | AI 에이전트 채팅 | Claude CLI subprocess |
| F-07 | 3-패널 GUI | Streamlit |

### 3.2 Should Have

| ID | 기능 | 구현 방법 |
|---|---|---|
| F-08 | 새 페이지 생성 | `wiki_create_page` MCP Tool |
| F-09 | 페이지 수정 | `wiki_update_page` MCP Tool |
| F-10 | 감사 로그 기록 | `wiki_append_journal` MCP Tool |
| F-11 | 태그 기반 필터링 | GUI 사이드바 |

### 3.3 Could Have (향후)

- 에이전트가 직접 위키 페이지를 생성/수정
- PDF 업로드 → 위키 페이지 자동 생성 (pipeline/ingest.py 연동)
- 다크/라이트 테마 전환

---

## 4. 비기능 요구사항

| 항목 | 요구사항 |
|---|---|
| 응답 시간 | 위키 조회: < 100ms, 에이전트 응답: < 60s |
| 의존성 | Python 3.10+, streamlit, fastmcp, Claude CLI |
| 데이터 저장 | 파일 시스템 (Markdown + YAML 프론트매터) |
| 확장성 | 새 위키 페이지 추가 시 코드 변경 없이 자동 반영 |
| 이식성 | 로컬 실행 (외부 서버·API Key 불필요, Claude CLI 필요) |

---

## 5. 시스템 아키텍처

```
[Streamlit GUI (app.py)]
    │
    ├─ 직접 호출 → [wiki_core.py]
    │                   │
    │                   └─ R/W → [wiki/*.md, journal.md, index.md]
    │
    └─ subprocess → [Claude CLI]
                        └─ 응답 → GUI 채팅 패널

[MCP 서버 (mcp_server.py)]
    │
    └─ 임포트 → [wiki_core.py]  ← MCP 클라이언트가 호출 시 사용
```

---

## 6. MCP Tool 명세

| Tool 이름 | 입력 | 출력 | 설명 |
|---|---|---|---|
| `wiki_list_pages` | 없음 | JSON 배열 | 모든 페이지 메타데이터 |
| `wiki_get_page` | `slug: str` | JSON 객체 | 페이지 전체 내용 |
| `wiki_search` | `query: str` | JSON 배열 | 관련도 순 검색 결과 |
| `wiki_get_related` | `slug: str` | JSON 배열 | 연관 페이지 목록 |
| `wiki_get_index` | 없음 | Markdown 문자열 | index.md 전체 |
| `wiki_create_page` | `slug, content` | `{ok, slug}` | 새 페이지 생성 |
| `wiki_update_page` | `slug, content` | `{ok, slug}` | 페이지 수정 (version +1) |
| `wiki_append_journal` | `message: str` | `{ok, message}` | 감사 로그 추가 |
| `wiki_get_journal` | `last_n: int` | Markdown 문자열 | 최근 N개 로그 |

---

## 7. 성공 지표 (Success Metrics)

| 지표 | 목표 |
|---|---|
| 위키 페이지 수 | 최소 7개 (아키텍처 도메인) |
| MCP Tool 수 | 8개 이상 |
| 에이전트 응답 성공률 | Claude CLI 연결 성공 시 > 95% |
| 검색 결과 정확도 | 직접 평가: 쿼리와 관련 없는 결과 < 20% |

---

## 8. 제약 조건 및 가정

- Claude CLI (`claude` 명령)가 PATH에 설치되어 있어야 에이전트 채팅 기능 사용 가능
- Claude CLI 미설치 시 위키 탐색 기능은 정상 동작 (에이전트 채팅만 오류 표시)
- Markdown 파일은 SCHEMA.md에 정의된 YAML 프론트매터 형식을 따라야 함
- 동시 사용자 1명 가정 (로컬 전용 도구)
