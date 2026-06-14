# journal.md — LLM Wiki 유지보수 로그

> **append-only. 절대 수정 금지.**  
> 형식: `- [YYYY-MM-DD HH:MM] <동작> <대상> — <결과>`

---

- [2026-06-13 14:00] Init wiki repository structure — SCHEMA.md, AGENTS.md, index.md, journal.md 생성
- [2026-06-13 14:10] Ingested `raw/1. Vibe coding and Agent coding.pdf` → `wiki/01-vibe-coding-and-agentic-coding.md`
- [2026-06-13 14:15] Ingested `raw/2. SDLC pipeline in Vibe coding.pdf` → `wiki/02-sdlc-pipeline.md`
- [2026-06-13 14:20] Ingested `raw/3. Agents subprocess calling.pdf` → `wiki/03-cli-subprocess.md`
- [2026-06-13 14:25] Ingested `raw/4. Plan_mode Sequential and Parallel agents.pdf` → `wiki/04-plan-mode-sequential-agents.md`
- [2026-06-13 14:30] Ingested `raw/5. Agent Specifications.pdf` → `wiki/05-agent-specifications.md`
- [2026-06-13 14:35] Ingested `raw/6. Agent pool and Orchestrator.pdf` → `wiki/06-agent-pool-orchestrator.md`
- [2026-06-13 14:40] Ingested `raw/7. Harness and Skills.pdf` → `wiki/07-harness-and-skills.md`
- [2026-06-13 14:45] Ingested `raw/8. Model Context Protocol.pdf` → `wiki/08-model-context-protocol.md`
- [2026-06-13 14:50] Ingested `raw/9. Loop and Hooks.pdf` → `wiki/09-loop-and-hooks.md`
- [2026-06-13 14:55] Created pipeline/ingest.py — raw→wiki 변환 파이프라인 초기 구현
- [2026-06-13 15:00] index.md 전체 갱신 — 9개 페이지 등록 완료
- [2026-06-13 15:30] [Round 1 결정] 과제 2 지식 도메인 선택 — CSE3308 재사용 대신 "개인 프로젝트 시스템 아키텍처 설계"로 결정
- [2026-06-13 15:35] raw/00_decision_framework/ 분석 완료 — 6축 분류 체계, 아키텍처 결정 가이드 확인
- [2026-06-13 15:40] raw/02_architecture_patterns/ 분석 완료 — 5가지 핵심 아키텍처 패턴 확인
- [2026-06-13 15:45] raw/03_microservices_patterns/ 분석 완료 — 6가지 보조 패턴 확인
- [2026-06-13 15:50] Ingested `raw/00_decision_framework/` → `wiki/10-project-classification.md`
- [2026-06-13 15:55] Ingested `raw/00_decision_framework/` → `wiki/11-architecture-decision-guide.md`
- [2026-06-13 16:00] Ingested `raw/02_architecture_patterns/` → `wiki/12-architecture-patterns.md`
- [2026-06-13 16:05] Ingested `raw/03_microservices_patterns/` → `wiki/13-microservices-patterns.md`
- [2026-06-13 16:10] Ingested `raw/01_system_design_basics/` → `wiki/14-system-design-basics.md`
- [2026-06-13 16:15] Ingested `raw/04_adr_templates/ + raw/05_c4_model/` → `wiki/15-adr-and-c4-model.md`
- [2026-06-13 16:20] Ingested `raw/06_antipatterns/` → `wiki/16-architecture-antipatterns.md`
- [2026-06-13 16:25] index.md 갱신 — 16개 페이지 등록 완료 (아키텍처 도메인 7페이지 추가)
- [2026-06-13 16:30] [Round 2 결정] GUI 프레임워크 선택 — Next.js/Flask 검토 후 Streamlit 결정 (Python 단일 파일, 빠른 MVP)
- [2026-06-13 16:35] [Round 3 결정] MCP 서버 구현체 선택 — FastMCP 결정 (데코레이터 기반 Tool 정의, 공식 SDK 호환)
- [2026-06-13 16:40] [Round 4 결정] AI 에이전트 연결 방식 — Claude CLI subprocess 결정 (API Key 불필요, 로컬 인증 재사용)
- [2026-06-13 16:45] [Round 5 결정] wiki_core.py API 설계 — parse_frontmatter, search, create/update_page 등 6개 핵심 함수 확정
- [2026-06-13 16:50] Created `wiki_core.py` — 공유 위키 I/O 라이브러리 (파싱·검색·쓰기)
- [2026-06-13 16:55] Created `mcp_server.py` — FastMCP 기반 MCP 서버, 9개 Tool 정의
- [2026-06-13 17:00] Created `app.py` — Streamlit 3-패널 GUI (사이드바+콘텐츠+채팅)
- [2026-06-13 17:05] Created `docs/01-domain-definition.md` — 지식 도메인 정의 문서
- [2026-06-13 17:10] Created `docs/02-decision-journal.md` — 6라운드 의사결정 히스토리
- [2026-06-13 17:15] Created `docs/03-prd.md` — PRD (기능 요구사항, MCP Tool 명세, 성공 지표)
- [2026-06-13 17:20] Created `README.md` — 프로젝트 설명, MCP Tool 9개 명세, 실행 방법
- [2026-06-13 17:25] MVP GUI 실행 확인 — Streamlit localhost:8501, 3-패널 정상 렌더링
- [2026-06-13 17:30] MVP 스크린샷 캡처 — docs/mvp-screenshot.png 저장
- [2026-06-13 17:35] AGENTS.md 갱신 — MCP Tool 에이전트 SPEC 섹션 추가 (과제 2 반영)
- [2026-06-14 16:09] [Hook] Auto-logged write: wiki/test-hook-dummy.md
