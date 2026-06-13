---
title: "Plan Mode & Sequential Agents"
tags: [plan-mode, pipeline, agent-design, sdlc]
source: "raw/4. Plan_mode Sequential and Parallel agents.pdf"
date: 2026-06-13
related: ["[[02-sdlc-pipeline]]", "[[05-agent-specifications]]", "[[07-harness-and-skills]]"]
version: 1
---

# Plan Mode & Sequential Agents

> Plan Mode는 에이전트가 코드를 건드리지 않고 계획만 세우는 Read-Only 모드이며, Sequential Agent는 핸드오프 파일로 단계별 결과를 전달하는 파이프라인 설계 패턴이다.

---

## Overview

에이전틱 코딩에서 가장 흔한 실패는 "계획 없이 코딩"이다. Plan Mode는 이를 방지하기 위해 에이전트를 Read-Only 상태로 제한하여 계획만 세우게 하고, 사용자가 검토·승인한 뒤에 구현으로 전환하는 구조다.

Sequential Agent는 각 에이전트의 출력이 다음 에이전트의 입력이 되는 파이프라인 구조로, SDLC의 Analysis 단계에서 수행하는 작업 분해와 동일한 원리다.

---

## Key Concepts

### Plan Mode

**정의**: Agent CLI에서 계획만 세우고, 코드는 건드리지 않는 모드.

**특징**:
- 진입하면 **read-only 도구만 활성화**
- 파일 읽기, 검색, 웹 조회는 가능
- 파일 수정·생성·삭제·명령 실행은 **차단**
- 산출물은 **마크다운 파일**로 저장됨 (메모리 공간)
- 사용자가 계획을 검토하고 승인하면 그때 구현 모드로 전환

**Plan Mode의 흐름**:
```
Input Prompt
    │
    ▼
Analysis → Decomposition → Planning → TODO → Outputs
```

**Multi-Agent Plan Mode (개선된 형태)**:
```
Input Prompt
    │
    ▼ AGENT 1
Analysis → Decomposition → Planning → Plan.md
    │
    ▼ AGENT 2
Review → Review.md
    │
    ▼ AGENT 1
Plan Rewrite → Revised_Plan.md
    │
    ▼
TODO → Final_TODO.md
```

### Handoff File (핸드오프 파일)

각 라운드 또는 개별 에이전트마다 작업 내용을 기록하는 파일.

```
workspace/
├── 00_planning.md          # 초기 계획
├── 01_review.md            # 검토 결과
├── 02_revised_plan.md      # 수정된 계획
└── 03_final_plan_report.md # 최종 계획 보고서
```

핸드오프 파일의 목적:
- 에이전트 간 상태 공유 (컨텍스트 전달)
- 작업 이력 기록
- 파이프라인 재현 가능성 확보

### Sequential Agent 파이프라인

```
각 에이전트는 독립적으로 작동하되,
앞 단계가 완료되어야 다음 단계가 시작됨.

태스크의 순서와 의존관계를 사전에 정확히 설계
= SDLC Analysis 단계의 작업 분해
```

### Parallel Agent (비교)

```
하나의 입력을 여러 전문화된 서브 에이전트가 동시에 처리
→ 각각 독립된 결과 산출
→ 주로 Research (WebSearch)에서 강력한 접근
```

---

## Details

### 파이프라인 설계 목표

```
프롬프트를 입력하면 Plan, Todo를 생성하는 자동화 파이프라인 설계

산출물 예시:
1. Plan 문서 (구현 계획)
2. Plan에 대한 Review 문서 (구현 계획 평가)
3. Revised Plan 문서 (수정된 구현 계획)
4. TODO 문서 (구현을 위한 체크리스트)
```

### 실패 사례: Sequential Agent의 한계

Quick Sort 구현 사례 — 순차 에이전트만으로는:
- 각 에이전트가 앞 단계의 오류를 그대로 이어받음
- 검증 단계 없이 파이프라인이 진행되면 최종 산출물 품질 저하
- Reviewer 에이전트 추가로 해결 (Ping-Pong 구조)

### 이상적인 Plan Mode 산출물 구조

Claude Plan Mode의 특징:
```
- 계획을 보여주기 위해 토큰을 많이 사용 (비효율적일 수 있음)
- Python 기반 프로토타입 요청 시 Tkinter 우선 시도 특징
  (추가 라이브러리 불필요, Fault 확률 낮음, 단 성능 이슈 있음)
```

### Subprocess 기반 파이프라인 실행

```python
import subprocess
import json

def run_plan_agent(prompt: str) -> str:
    """Plan Agent: 계획 수립"""
    result = subprocess.run(
        ["claude", "-p", "--output-format", "json", "--no-session-persistence"],
        input=f"[PLANNER] {prompt}\n\n분석하고 구현 계획을 Plan.md 형식으로 작성하라.",
        capture_output=True, encoding="utf-8", timeout=180
    )
    response = json.loads(result.stdout)
    return response["result"]

def run_review_agent(plan_content: str) -> str:
    """Review Agent: 계획 검토"""
    result = subprocess.run(
        ["claude", "-p", "--output-format", "json", "--no-session-persistence"],
        input=f"[REVIEWER]\n\n다음 계획을 검토하고 Review.md 형식으로 평가하라.\n\n{plan_content}",
        capture_output=True, encoding="utf-8", timeout=180
    )
    response = json.loads(result.stdout)
    return response["result"]

# 파이프라인 실행
prompt = "subprocess 기반 AI 챗봇 구현"
plan = run_plan_agent(prompt)

with open("workspace/00_planning.md", "w") as f:
    f.write(plan)

review = run_review_agent(plan)
with open("workspace/01_review.md", "w") as f:
    f.write(review)
```

---

## Examples / Code

### 과제 예시 (실습)

```
주요 목표: subprocess 기반 AI 챗봇의 구현을 위한 설계 문서 생성

Task 1: AI와 논의하여 Plan Mode의 구조와 산출물 파악
         Excalidraw로 파이프라인 구조 러프하게 정의

Task 2: 파이프라인 구조 image와 API Document를 드래그앤드롭으로
         CLI에게 전달 → 실행 명령
         "파이프라인 스크립트의 명세를 재사용 가능하도록 구조화한 문서를 작성하고
          markdown 파일로 저장해주세요"

Task 3: 각 Round/Agent마다 핸드오프 파일을 저장하도록 파이프라인 개선
         예시: workspace/00_planning.md, 01_review.md, ..., 04_final_plan_report.md
```

### Subprocess Cheatsheet 참고

```
Claude  → Claude_CLI_Subprocess_API.md
Codex   → Codex_CLI_Subprocess_API.md
Gemini  → Gemini_CLI_Subprocess_API.md
Heavy User (Claude + Codex + Gemini) → Agent_CLI_Subprocess_API.md
```

---

## Related

- [[02-sdlc-pipeline]] — SDLC와 PRD 기반 Spec-Driven Development
- [[05-agent-specifications]] — System Prompt와 에이전트 명세 설계
- [[06-agent-pool-orchestrator]] — Agent Pool과 상태 관리
- [[07-harness-and-skills]] — Contract-Driven Iteration (TASK.md)
- [[03-cli-subprocess]] — subprocess.run() API 상세
