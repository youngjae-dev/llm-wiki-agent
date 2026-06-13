# 에이전트 의사결정 라운드 문서

## ArchWiki MCP Tool — 설계 의사결정 히스토리

---

## 과제 1 Journal 참고 (출발점)

> 과제 2의 의사결정은 과제 1에서 구축한 LLM Wiki 지식 베이스(`journal.md`)를 기반으로 시작되었다.  
> 아래는 과제 2 설계를 시작하기 전 `journal.md` 마지막 상태 (AGENTS.md 규칙: "매 세션 시작 시 journal.md 마지막 10줄 읽기"):

```
- [2026-06-13 14:10] Ingested raw/1. Vibe coding and Agent coding.pdf → wiki/01-vibe-coding-and-agentic-coding.md
- [2026-06-13 14:15] Ingested raw/2. SDLC pipeline in Vibe coding.pdf → wiki/02-sdlc-pipeline.md
- [2026-06-13 14:20] Ingested raw/3. Agents subprocess calling.pdf → wiki/03-cli-subprocess.md
- [2026-06-13 14:25] Ingested raw/4. Plan_mode Sequential and Parallel agents.pdf → wiki/04-plan-mode-sequential-agents.md
- [2026-06-13 14:30] Ingested raw/5. Agent Specifications.pdf → wiki/05-agent-specifications.md
- [2026-06-13 14:35] Ingested raw/6. Agent pool and Orchestrator.pdf → wiki/06-agent-pool-orchestrator.md
- [2026-06-13 14:40] Ingested raw/7. Harness and Skills.pdf → wiki/07-harness-and-skills.md
- [2026-06-13 14:45] Ingested raw/8. Model Context Protocol.pdf → wiki/08-model-context-protocol.md
- [2026-06-13 14:50] Ingested raw/9. Loop and Hooks.pdf → wiki/09-loop-and-hooks.md
- [2026-06-13 15:00] index.md 전체 갱신 — 9개 페이지 등록 완료
```

**Journal 분석 결과**:
- 과제 1에서 CSE3308 강의 9개 PDF → 9개 위키 페이지로 변환 완료
- raw/ → wiki/ 파이프라인(`pipeline/ingest.py`)이 정상 동작 확인됨
- index.md, journal.md, SCHEMA.md, AGENTS.md 등 핵심 인프라 완비
- → **과제 2는 이 인프라 위에 새 도메인 지식과 MCP Tool 레이어를 추가하는 방향으로 진행**

---

## Round 1: 지식 도메인 선택

**질문**: 어떤 도메인의 위키를 만들 것인가?

**검토한 옵션**:
| 옵션 | 이유 | 결정 |
|---|---|---|
| CSE3308 Agentic Coding 직접 재사용 | 기존 과제 1 내용과 동일 → 평가 차별성 없음 | ❌ 탈락 |
| 시스템 아키텍처 설계 도메인 | 실용성 높음, raw 파일로 구성 가능, 과제 1과 차별화 | ✅ 선택 |

**결정 근거**:
- 개인 프로젝트를 시작할 때 아키텍처 설계가 가장 어렵고 중요한 단계임
- 이 도메인은 패턴 선택, 데이터 흐름 설계, ADR 작성, 안티패턴 회피로 명확히 구조화됨
- 에이전트가 "프로젝트 특성을 파악 → 최적 아키텍처 도출"하는 시나리오를 자연스럽게 구현 가능

---

## Round 2: GUI 구현 방식 선택

**질문**: 어떤 프레임워크로 3-패널 GUI를 만들 것인가?

**검토한 옵션**:
| 옵션 | 장점 | 단점 | 결정 |
|---|---|---|---|
| Next.js + React | 풍부한 UI 표현력 | 빌드 복잡, TypeScript 설정, API 서버 별도 필요 | ❌ |
| Flask + Jinja2 | 경량 | HTML/CSS 직접 작성 부담, 상태 관리 어려움 | ❌ |
| **Streamlit** | Python 단일 파일, 빠른 프로토타이핑, 상태 관리 내장 | UI 커스터마이징 한계 | ✅ 선택 |

**결정 근거**:
- MVP 검증이 우선 → 빠른 구현 가능한 Streamlit 선택
- `st.columns()`으로 3-패널 레이아웃 구현 가능
- CSS 인젝션으로 다크 테마·태그 뱃지 등 커스터마이징 가능

---

## Round 3: MCP 서버 구현체 선택

**질문**: MCP 서버를 어떤 방식으로 구현할 것인가?

**검토한 옵션**:
| 옵션 | 특징 | 결정 |
|---|---|---|
| mcp (공식 Python SDK) | 저수준, 보일러플레이트 많음 | ❌ |
| **FastMCP** | 데코레이터 기반, 간결한 API, 공식 SDK와 호환 | ✅ 선택 |
| 직접 구현 (JSON-RPC) | 학습 비용 높고 유지보수 어려움 | ❌ |

**결정 근거**:
- `@mcp.tool()` 데코레이터로 함수 → MCP Tool 변환이 즉시 가능
- Python 독스트링이 자동으로 Tool Description이 됨
- `mcp.run()`으로 stdio/SSE 모두 지원

---

## Round 4: AI 에이전트 연결 방식

**질문**: Streamlit GUI에서 AI 에이전트를 어떻게 연결할 것인가?

**검토한 옵션**:
| 옵션 | 장점 | 단점 | 결정 |
|---|---|---|---|
| Anthropic Python SDK | 안정적, 스트리밍 지원 | API 키 필요, 과금 발생 | 보조 옵션 |
| **Claude CLI subprocess** | 로컬 환경에서 인증 재사용, 설정 불필요 | 응답 속도 다소 느림 | ✅ 선택 (기본) |
| OpenAI SDK | 풍부한 문서 | API 키 필요, 비용 | ❌ |

**결정 근거**:
- `subprocess.run(["claude", "-p", ...])`로 로컬 Claude CLI 활용
- 별도 API 키 설정 없이 Claude Code 환경에서 즉시 동작
- 응답은 JSON 포맷(`--output-format json`)으로 파싱 가능

---

## Round 5: 위키 파일 구조 설계

**질문**: wiki_core.py의 핵심 기능은 무엇이어야 하는가?

**결정된 API 목록**:

| 함수 | 역할 | 선택 이유 |
|---|---|---|
| `parse_frontmatter()` | YAML 파싱 | 외부 라이브러리 없이 경량 구현 |
| `get_all_pages()` | 전체 목록 | 사이드바 네비게이션용 |
| `get_page(slug)` | 단일 조회 | 부분 일치로 사용성 향상 |
| `search(query)` | 키워드 검색 | TF-IDF 없이 term frequency로 경량 구현 |
| `create_page()` / `update_page()` | 쓰기 | AGENTS.md에 정의된 Maintenance Agent 기능 |
| `append_journal()` | 감사 로그 | 모든 쓰기 작업 자동 기록 |

**결정 근거**:
- 외부 데이터베이스 없이 Markdown 파일만으로 모든 기능 구현
- SCHEMA.md의 프론트매터 규약을 Python으로 그대로 구현
- 검색은 단순 term frequency로 구현 → 추가 의존성 없음

---

## Round 6: 위키 페이지 구성 결정

**질문**: raw 파일 26개를 몇 개 페이지로 합성할 것인가?

**결정**: 7개 페이지 (wiki/10~16)

| 결정 기준 | 내용 |
|---|---|
| 페이지당 적절한 크기 | 한 페이지가 하나의 개념 영역을 담도록 |
| 관련 파일 그룹핑 | raw/ 하위 폴더 단위로 합성 (1~2 폴더 → 1 페이지) |
| 내부 링크 네트워크 | 모든 페이지가 최소 2~3개 related 링크를 가지도록 |

**결과**: 26개 raw 파일 → 7개 위키 페이지, 평균 linked 페이지 수: 3.0
