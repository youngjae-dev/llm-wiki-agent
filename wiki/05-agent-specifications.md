---
title: "Agent Specifications — 에이전트 명세 설계"
tags: [agent-design, context-engineering, pipeline, sdlc]
source: "raw/5. Agent Specifications.pdf"
date: 2026-06-13
related: ["[[04-plan-mode-sequential-agents]]", "[[06-agent-pool-orchestrator]]", "[[07-harness-and-skills]]"]
version: 1
---

# Agent Specifications — 에이전트 명세 설계

> 에이전트 명세(Agent Specification)는 에이전트의 역할·입력·출력·시스템 프롬프트를 구조화하여 정의한 문서이며, 멀티-에이전트 파이프라인의 일관성과 재현성을 보장하는 핵심 요소다.

---

## Overview

에이전트는 단순히 프롬프트를 받아 응답하는 것이 아니라, **명세된 역할**에 따라 특정 입력을 받아 특정 출력을 생성하는 컴포넌트다. 명세가 명확할수록 파이프라인의 예측 가능성이 높아지고, 에이전트 간 핸드오프가 안정적으로 이뤄진다.

---

## Key Concepts

### Agent Specification 구성 요소

```
Agent Spec
├── Role         → 에이전트의 역할 (한 줄 설명)
├── System Prompt → 에이전트의 행동 방식 전체를 정의
├── Inputs
│   ├── description → 받는 입력의 설명
│   ├── format      → 입력 형식 (text, json, file_path 등)
│   └── source      → 입력 출처 (user, 이전 에이전트 ID, file 등)
└── Outputs
    ├── description → 만드는 출력의 설명
    ├── format      → 출력 형식
    └── files       → 생성하는 파일 경로 목록
```

**Context에 포함되어야 할 것**:
- Session ID
- Project Information
- Hand-Off (이전 에이전트의 출력)

### System Prompt

에이전트의 행동 방식 전체를 결정하는 텍스트.

```
[Input]  "Python으로 bubble sort 함수를 작성해줘."
[System] "너는 절대 답을 주지 않는 소크라테스식 교수다.
          모든 요청에 질문으로만 응답하라."
→ 에이전트는 코드 대신 질문으로 응답
```

**주입 방법**:
- **Claude**: `--system-prompt` 플래그로 간단하게 가능
- **Codex/Gemini**: 마크다운 파일을 활용하여 주입

### Planner-Reviewer 파이프라인

가장 기본적인 멀티-에이전트 구조:

```
User Prompt
    │
    ▼ AGENT 1 (Planner)
    Analysis → Decomposition → Planning
    출력: Plan.md
    │
    ▼ AGENT 2 (Reviewer)
    Validation → Review → Revise (1~10점 채점)
    출력: Review.md
    │
    ▼ AGENT 1 (Planner)
    Plan Rewrite (Review 반영)
    출력: Revised_Plan.md
    │
    ▼
    TODO → Final_TODO.md
```

---

## Details

### Planner 에이전트 System Prompt

| 단계 | 역할 |
|---|---|
| Step 1: Analysis | 요청을 읽고 목표(Goal)와 기술적 제약(Constraints)을 판단 |
| Step 2: Decomposition | 목표를 실현 가능한 단위로 쪼개고, 실행 순서와 의존성을 결정 |
| Step 3: Planning | 각 TODO에 입력, 출력, 구현 방법, 완료 기준(AC)을 구체화 |

### Reviewer 에이전트 System Prompt

| 단계 | 역할 |
|---|---|
| Step 1: Validation | 모든 TODO에 입력/출력/AC가 있는지, 빠진 항목이 있는지 확인 |
| Step 2: Review | 기술적으로 구현 가능한지, 의존성 순서가 맞는지, 모호한 부분 평가 |
| Step 3: Revise | 1~10점 점수를 매기고, 구체적 개선 사항을 항목별로 작성 |

### Ping-Pong 구조 (반복 검토)

```python
def ping_pong_pipeline(prompt: str, pass_threshold: int = 8) -> dict:
    """
    Planner-Reviewer 핑퐁 파이프라인.
    Reviewer가 pass_threshold 이상 점수를 줄 때까지 반복.
    """
    plan = run_planner(prompt)
    
    round_num = 0
    while True:
        review = run_reviewer(plan)
        score = extract_score(review)  # 1~10 점수 파싱
        
        # 첫 평가는 무조건 7점 이하로 제한 (재검토 강제)
        if round_num == 0:
            score = min(score, 7)
        
        if score >= pass_threshold:
            break
        
        plan = run_planner_revise(plan, review)
        round_num += 1
    
    return {"plan": plan, "review": review, "score": score, "rounds": round_num}
```

**핑퐁 규칙 예시**:
- Reviewer 에이전트에게 보고서 점수를 10점 기준으로 잡고, 8점 이상일 때만 통과
- 첫 평가는 무조건 7점 이하로 제한 (최소 1회 개선 강제)

### 확장 파이프라인: Planner → Reviewer → Coder → Tester

```
User Prompt
    │
    ▼ Planner Agent     → Plan.md
    │
    ▼ Reviewer Agent    → Review.md
    │
    ▼ Planner Revise    → Revised_Plan.md
    │
    ▼ Coder Agent       → 구현 코드
    │
    ▼ Tester Agent      → 테스트 결과
```

**Coder System Prompt 요소**:
- 역할: Revised_Plan.md를 읽고 코드 구현
- 제약: 승인된 플랜 범위 내에서만 구현, 새 의존성 추가 금지

**Tester System Prompt 요소**:
- 역할: 구현된 코드에 대한 테스트 작성 및 실행
- 제약: 실패한 테스트를 skip 처리하지 마라

---

## Examples / Code

### Agent Specification JSON 예시

```json
{
  "id": "planner",
  "role": "사용자 요청을 분석하여 구현 계획을 수립하는 에이전트",
  "system_prompt": "너는 시니어 소프트웨어 아키텍트다. 요청을 분석하여 실현 가능한 TODO 목록과 Plan을 작성하라. 각 TODO에는 입력, 출력, 완료 기준(AC)을 포함하라.",
  "input": {
    "description": "사용자 요청 프롬프트",
    "format": "text",
    "source": "user"
  },
  "output": {
    "description": "구현 계획 마크다운",
    "format": "markdown",
    "files": ["workspace/00_planning.md"]
  },
  "tools": ["read_file", "web_search"],
  "constraints": {
    "max_attempts": 3,
    "timeout_seconds": 180,
    "sandbox": "read-only"
  }
}
```

```json
{
  "id": "reviewer",
  "role": "계획의 완성도와 기술적 실현 가능성을 평가하는 에이전트",
  "system_prompt": "너는 엄격한 시니어 리뷰어다. 제출된 Plan을 검토하여 1~10점을 매기고, 구체적인 개선 사항을 작성하라. 첫 평가는 7점을 초과하지 마라.",
  "input": {
    "description": "Planner가 생성한 Plan.md",
    "format": "markdown",
    "source": "planner"
  },
  "output": {
    "description": "검토 결과 및 점수",
    "format": "markdown",
    "files": ["workspace/01_review.md"]
  },
  "tools": ["read_file"],
  "constraints": {
    "max_attempts": 1,
    "timeout_seconds": 120,
    "sandbox": "read-only"
  }
}
```

### System Prompt 주입 (Claude)

```bash
# Claude: --system-prompt 플래그
claude -p --system-prompt "너는 절대 답을 주지 않는 소크라테스식 교수다." \
  --output-format json

# 또는 마크다운 파일로
claude -p --system-prompt "$(cat pool/planner.md)" --output-format json
```

---

## Related

- [[04-plan-mode-sequential-agents]] — Plan Mode와 핸드오프 파일 구조
- [[06-agent-pool-orchestrator]] — Agent Pool에서 명세 파일 관리
- [[07-harness-and-skills]] — AGENTS.md를 통한 Preference 정의
- [[03-cli-subprocess]] — subprocess로 에이전트 실행하기
