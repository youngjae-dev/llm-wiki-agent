---
title: "Harness Engineering & Skills"
tags: [harness, skills, agent-design, agentic-coding, context-engineering]
source: "raw/7. Harness and Skills.pdf"
date: 2026-06-13
related: ["[[05-agent-specifications]]", "[[06-agent-pool-orchestrator]]", "[[09-loop-and-hooks]]"]
version: 1
---

# Harness Engineering & Skills

> Harness Engineering은 에이전트가 복잡한 작업을 안전하고 효율적으로 완수하도록 프롬프트나 모델을 넘어선 **외부 실행 환경**을 구조적으로 설계하고 통제하는 기술이다.

---

## Overview

단순히 프롬프트를 잘 작성하는 것만으로는 에이전트가 일관되게 동작하지 않는다. Harness Engineering은 작업의 **목표·절차·기록·선호**를 분리해 관리하여 에이전트가 안정적으로 작업을 수행하게 만드는 실행 구조다.

> "Contract가 없는 Procedure는 무한 루프이고, Procedure가 없는 Contract는 죽은 문서다."

---

## Key Concepts

### 하네스의 4대 구성 요소

| 책임 | 핵심 질문 | 파일 예시 |
|---|---|---|
| Contract | 무엇이 끝났는가? | `TASK.md` |
| Procedure | 어떻게 진행하는가? | Skill 파일 |
| Journal | 지금까지 무엇을 했는가? | `journal.md` 또는 MCP |
| Preference | 어떤 방식으로 일하는가? | `PROFILE.md`, `AGENTS.md`, `CLAUDE.md` |

### Contract (TASK.md)

에이전트가 작업의 완료 조건을 알 수 있게 해주는 계약 문서.

```markdown
Status: open
Goal: Add timeout parameter to fetch_user() with 5s default.
Done when:
- `pytest tests/test_fetch_user.py -q` passes
- New parameter has docstring entry
- Existing callers still work
Log:
-
```

**좋은 Contract 조건**:

| 조건 | 설명 |
|---|---|
| Goal은 한 문장 | 두 문장이면 작업이 두 개인 경우가 많다 |
| Done when은 측정 가능 | "works well"은 금지 |
| 검증 명령은 구체적 | `pytest` 보다 `pytest tests/test_foo.py -q` |
| Done when은 1~4개 | 많으면 작업을 쪼갠다 |
| 부정 가드 포함 | 새 의존성 금지, 기존 기능 유지 등 |

### Contract-Driven Iteration

에이전트가 Contract를 읽고, Done when을 만족할 때까지 반복하는 방식.

```
1. TASK.md를 읽는다
2. Status가 done이면 멈춘다
3. 아직 open이면 가장 가까운 Done when을 향해 최소 변경을 한다
4. 테스트, 린트, 타입 체크 등으로 검증한다
5. 결과를 Journal에 한 줄 기록한다
6. 모든 Done when이 만족되면 Status를 done으로 바꾼다
7. 아니면 다시 반복한다
```

### Skill (스킬)

**정의**: 에이전트가 특정 작업을 어떻게 수행할지 정의한 마크다운 파일.

- AI Agent는 작업 맥락에 맞는 Skill을 자동으로 찾아 적용할 수 있음
- 구조: `SKILL.md` 파일 + 필요 시 보조 파일들이 한 폴더에 묶인 형태

```
.claude/commands/
├── code-review.md     # 코드 리뷰 방법 정의
├── deploy.md          # 배포 절차 정의
└── wiki-ingest.md     # 위키 페이지 생성 방법 정의
```

### Journal

반복마다 무엇을 했는지 남기는 기록. 누적되고, 수정하지 않는 것이 원칙.

| 항목 | 예시 |
|---|---|
| 무엇을 했는가 | Added timeout=5 default |
| 왜 했는가 | Needed to satisfy Done when |
| 결과는 무엇인가 | pytest passes / failed / reverted |

**위치 선택**:

| 방식 | 위치 | 적합한 경우 |
|---|---|---|
| In-file | TASK.md의 Log: | 단일 세션 작업 |
| External | MCP append/read | 세션을 넘어 이어지는 작업 |

---

## Details

### Ralph's Loop (랄프 루프의 단계)

```
Phase 1: Jobs To Be Done
  AI Agent와 사람이 대화하며 /spec 폴더에 명세서를 만든다

Phase 2: Compare & Plan
  AI 에이전트가 기존 코드 구현체와 명세서를 비교한 뒤 Plan을 세운다

while (작업 미완료):
  Phase 3: Execute One Task
    AI 에이전트가 1개의 Plan 체크리스트에 대해:
    작업 → 검증 → 계획 업데이트 → 커밋 → 종료
    한 작업이 끝나면 새 에이전트가 다음 체크리스트 작업 진행
```

**생각해볼 것**:
- 명시적인 달성 조건이 있어야 함
- 최대 작업 상한이 있어야 함

### AGENTS.md 템플릿 (실제 사용 예시)

```markdown
# AGENTS.md
> 매 세션 시작 시 이 파일과 `journal.md`를 먼저 읽어라.
> 이 파일이 너의 작업 방식 전부다.

## 0. 파일 구조
- `specs/` — 사용자와 합의한 요구사항 명세 (= 무엇을 만들 것인가)
- `TASK.md` — 지금 해야 할 작업 체크리스트
- `journal.md` — 지금까지 한 일의 기록 (append only, 절대 수정 금지)
- `AGENTS.md` — 이 파일

## 1. 작업 시작 전 (계획 단계)
- 프로젝트가 git으로 관리되고 있지 않으면 `git init`을 먼저 실행하라.
- `specs/` 폴더에서 사용자와 함께 계획을 세워라.
- 소크라테스적 질문으로 요구사항을 명확히 하라. **가정하지 말고 물어라.**
- 사용자가 "이정도면 충분하다"라고 명시적으로 마감을 선언하기 전까지,
  TASK.md의 체크리스트를 계속 다듬어라.
- 마감 선언 전에는 단 한 줄의 production 코드도 쓰지 마라.

## 2. 매 작업 (구현 단계)
매 반복은 다음 순서를 정확히 따라라:
1. journal.md의 마지막 5줄을 읽어 직전 상태를 확인하라.
2. TASK.md에서 가장 위의 미완료 항목 단 한 개만 골라라.
3. 관련 코드를 먼저 읽어라. 추측보다 탐색이 우선이다.
4. 구현하라.
5. 검증을 실행하라: `npm test && npm run lint && npm run build`
6. git commit. 메시지에 "무엇을"이 아니라 "왜"를 적어라.
7. TASK.md의 해당 항목을 체크하라.
8. journal.md에 한 줄 추가하라.
9. 종료하라. 다음 작업은 다음 반복에서.

## 3. 절대 하지 마라
❌ 한 반복에서 두 개 이상의 작업을 처리하기
❌ 실패한 테스트를 주석 처리하거나 skip 처리하기
❌ specs/ 없이 코드를 작성하기
❌ journal.md를 수정하거나 삭제하기 (오직 append)
❌ 사용자의 명시적 승인 없이 새 의존성 추가하기
❌ 같은 접근을 3번 실패한 뒤에도 시도 계속하기

## 4. 막히면
- 명세가 모호하면 추측하지 말고 사용자에게 질문하라.
- 같은 시도가 3번 실패하면 멈추고 journal.md에 상황을 적은 뒤 보고하라.
```

### 에이전틱 코딩 패턴 5가지

| 패턴 | 의미 | 예시 |
|---|---|---|
| Prompt Chaining | 앞 단계 결과를 다음 단계 입력으로 사용 | 스펙 작성 → 테스트 작성 → 구현 |
| Routing | 입력 종류에 따라 다른 경로 선택 | 문서 수정은 가벼운 모델, 보안 이슈는 강한 모델 |
| Parallelization | 독립 작업을 동시에 실행 | 여러 파일을 나누어 수정 |
| Orchestrator-Workers | 관리자가 작업을 쪼개 워커에게 배분 | 영향받는 파일을 찾고 각 워커에게 할당 |
| Evaluator-Optimizer | 만들고 평가하고 다시 고침 | 테스트 통과할 때까지 구현 반복 |

### 코딩에서 자주 쓰는 패턴

| 이름 | 흐름 | 핵심 |
|---|---|---|
| EPCC | Explore → Plan → Code → Commit | 바로 코딩하지 않고 먼저 읽고 계획한다 |
| TDD | Red → Green → Refactor | 실패 테스트를 먼저 만들고 통과시킨다 |
| Visual Iteration | 생성 → 화면 확인 → 수정 | UI는 실제 화면으로 검증한다 |
| Three-Agent Harness | Planner → Generator → Evaluator | 계획, 구현, 평가를 분리한다 |

### 패턴 선택 가이드

| 상황 | 선택 |
|---|---|
| 단계 간 의존성이 있다 | Prompt Chaining |
| 독립 작업이 여러 개다 | Parallelization |
| 작업 수를 미리 모른다 | Orchestrator-Workers |
| 결과를 자동 검증할 수 있다 | Evaluator-Optimizer |
| 입력 유형별 처리가 다르다 | Routing |
| 단일 에이전트로 충분하다 | 단일 에이전트 |

### 가장 흔한 실패와 해결

| 실패 | 문제 | 해결 |
|---|---|---|
| Done when이 모호함 | 모델이 자기 판단으로 완료 처리 | 명령어로 검증 가능하게 작성 |
| 자기 결과를 자기가 평가 | 항상 후하게 평가 | 테스트, 린트, 별도 evaluator 사용 |
| Contract가 너무 큼 | 중간에 길을 잃음 | 작은 Contract 여러 개로 분리 |
| Plan 없이 Code | 엉뚱한 파일 수정 | Explore와 Plan 먼저 수행 |
| MCP에 execute 도구 추가 | 외부 wrapper가 됨 | MCP는 append/read만 사용 |
| Done when을 수정함 | 기준을 낮춰 완료한 척함 | Done when 수정 금지 |

### OpenAI Goal (Codex)

```toml
# .codex/config.toml
[experimental]
goal = true
```

```
/goal <목표>     → 새 목표 생성 및 루프 시작
/goal pause      → 현재 목표를 paused 상태로 전환
/goal resume     → paused 상태를 다시 재개
/goal clear      → 현재 목표 제거
```

---

## Related

- [[05-agent-specifications]] — 에이전트 명세 (System Prompt, Role)
- [[06-agent-pool-orchestrator]] — Orchestrator 패턴과 Agent Pool
- [[09-loop-and-hooks]] — Loop와 Hook으로 하네스 자동화
- [[08-model-context-protocol]] — MCP를 통한 Journal 외부 저장
