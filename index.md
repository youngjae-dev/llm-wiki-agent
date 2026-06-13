# LLM Wiki — Index

> **Agentic Coding Basics** 강의(CSE3308) 기반 지식 베이스.  
> LLM 에이전트가 유지보수하는 Markdown-only 위키.

---

## 빠른 시작

- 위키 구조·규칙 → [SCHEMA.md](SCHEMA.md)
- 에이전트 행동 지침 → [AGENTS.md](AGENTS.md)
- 유지보수 로그 → [journal.md](journal.md)
- 파이프라인 사용법 → [pipeline/README.md](pipeline/README.md)

---

## 위키 페이지 목록

| 페이지 | 태그 | 요약 |
|---|---|---|
| [[01-vibe-coding-and-agentic-coding\|01. Vibe Coding & Agentic Coding]] | `vibe-coding` `agentic-coding` `sdlc` | 소프트웨어 엔지니어링의 진화와 바이브·에이전틱 코딩의 개념 차이 |
| [[02-sdlc-pipeline\|02. SDLC Pipeline]] | `sdlc` `agentic-coding` `pipeline` | AI-Assisted 개발에서 SDLC의 역할과 PRD 기반 Spec-Driven Development |
| [[03-cli-subprocess\|03. CLI & Subprocess]] | `subprocess` `agentic-coding` | Python subprocess를 통한 Claude/Codex/Gemini CLI 호출 방법 |
| [[04-plan-mode-sequential-agents\|04. Plan Mode & Sequential Agents]] | `plan-mode` `pipeline` `agent-design` | Plan Mode의 구조와 순차 에이전트 파이프라인·핸드오프 파일 설계 |
| [[05-agent-specifications\|05. Agent Specifications]] | `agent-design` `context-engineering` | 에이전트 명세(Role, Input, Output, System Prompt) 설계 방법 |
| [[06-agent-pool-orchestrator\|06. Agent Pool & Orchestrator]] | `orchestrator` `agent-design` `pipeline` | Agent Pool과 Orchestrator 패턴, 에이전트 상태 관리 |
| [[07-harness-and-skills\|07. Harness Engineering & Skills]] | `harness` `skills` `agent-design` | Harness Engineering의 개념과 Contract-Driven Iteration, Skill 설계 |
| [[08-model-context-protocol\|08. Model Context Protocol (MCP)]] | `mcp` `context-engineering` | MCP의 배경, 구조, 트레이드오프, Tool Calling 원칙 |
| [[09-loop-and-hooks\|09. Loop & Hooks]] | `loop` `hooks` `agentic-coding` | 에이전트 생애주기 Hook 이벤트와 자동화 Loop 활용 패턴 |

---

## 개념 빠른 참조

### 에이전트 설계

- **단일 에이전트** → [[01-vibe-coding-and-agentic-coding]]
- **순차 에이전트 (Sequential)** → [[04-plan-mode-sequential-agents]]
- **병렬 에이전트 (Parallel)** → [[02-sdlc-pipeline]]
- **Planner–Reviewer 핑퐁** → [[05-agent-specifications]]
- **Agent Pool** → [[06-agent-pool-orchestrator]]
- **Orchestrator 패턴** → [[06-agent-pool-orchestrator]]

### 실행 환경

- **CLI 호출 (subprocess)** → [[03-cli-subprocess]]
- **Plan Mode** → [[04-plan-mode-sequential-agents]]
- **Harness Engineering** → [[07-harness-and-skills]]
- **MCP** → [[08-model-context-protocol]]
- **Loop & Hooks** → [[09-loop-and-hooks]]

### 문서·명세

- **PRD / SRS** → [[02-sdlc-pipeline]]
- **AGENTS.md 작성법** → [[07-harness-and-skills]]
- **핸드오프 파일** → [[04-plan-mode-sequential-agents]]
- **Contract (TASK.md)** → [[07-harness-and-skills]]
- **Skill** → [[07-harness-and-skills]]

---

## 원본 소스

| 파일 | 대응 위키 페이지 |
|---|---|
| `raw/1. Vibe coding and Agent coding.pdf` | [[01-vibe-coding-and-agentic-coding]] |
| `raw/2. SDLC pipeline in Vibe coding.pdf` | [[02-sdlc-pipeline]] |
| `raw/3. Agents subprocess calling.pdf` | [[03-cli-subprocess]] |
| `raw/4. Plan_mode Sequential and Parallel agents.pdf` | [[04-plan-mode-sequential-agents]] |
| `raw/5. Agent Specifications.pdf` | [[05-agent-specifications]] |
| `raw/6. Agent pool and Orchestrator.pdf` | [[06-agent-pool-orchestrator]] |
| `raw/7. Harness and Skills.pdf` | [[07-harness-and-skills]] |
| `raw/8. Model Context Protocol.pdf` | [[08-model-context-protocol]] |
| `raw/9. Loop and Hooks.pdf` | [[09-loop-and-hooks]] |

---

*Last updated: 2026-06-13 | Maintained by LLM agents per [AGENTS.md](AGENTS.md)*
