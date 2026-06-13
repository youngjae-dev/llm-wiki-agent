---
title: "Agent Pool & Orchestrator"
tags: [orchestrator, agent-design, pipeline, agentic-coding]
source: "raw/6. Agent pool and Orchestrator.pdf"
date: 2026-06-13
related: ["[[05-agent-specifications]]", "[[07-harness-and-skills]]", "[[03-cli-subprocess]]"]
version: 1
---

# Agent Pool & Orchestrator

> Agent Pool은 재사용 가능한 에이전트 정의를 파일로 관리하는 구조이며, Orchestrator는 목표에 맞는 에이전트를 선택·실행하는 관리자 역할을 담당한다.

---

## Overview

단일 파이프라인(Sequential/Parallel Agent)은 특정 작업에 최적화되어 있지만, 파이프라인 자체를 Tool처럼 보관하지 않으면 재사용이 어렵다. Agent Pool은 에이전트 설정값을 JSON/TOML/XML 파일로 관리하여, Orchestrator가 목표에 따라 유동적으로 에이전트를 선택·조합할 수 있게 한다.

---

## Key Concepts

### 에이전트의 상태 모델

에이전틱 코딩 워크플로우/세션에서 각 에이전트는:

```
상태: Processing | Idle
상태 변화(전이): Idle → Processing → Idle (또는 Terminate)
입력과 출력
시간의 개념
```

**이전 파이프라인 다이어그램에서**:
- Planner가 Reviewer에게 자료를 전달 후 **대기(Idle)**
- Reviewer는 Planner의 요청에 따라 작업 후 Review 반환 → 이후 **Sleep(Idle) 또는 Terminate**

### Workflow (Pipeline) 의 한계

| 문제 | 설명 |
|---|---|
| Main Orchestrator 과부하 | Sub-Agent 방식을 그대로 재사용하면 Orchestrator에 과도한 부담 |
| 재사용 어려움 | 단일 작업에만 활용, 파이프라인 자체를 Tool로 저장하지 않으면 이후 재사용 불가 |

### Agent Pool

**정의**: 개별 에이전트의 설정값을 파일(JSON, TOML, XML 등)로 관리하여, Orchestrator가 필요한 에이전트를 유동적으로 활용할 수 있는 구조.

```
pool/
├── planner.json      # 계획 수립 에이전트
├── reviewer.json     # 검토 에이전트
├── coder.json        # 구현 에이전트
└── tester.json       # 테스트 에이전트
```

각 JSON 파일이 하나의 에이전트를 정의한다.

### Agent Pool JSON 스키마

```json
{
  "id": "에이전트 파일명과 동일",
  "role": "에이전트의 한 줄 역할 설명",
  "system_prompt": "에이전트에게 전달될 전체 시스템 프롬프트",
  "input": {
    "description": "이 에이전트가 받는 입력 설명",
    "format": "입력 형식 (text, csv, json, file_path 등)",
    "source": "입력이 어디서 오는지 (user, 이전 에이전트 ID, file 등)"
  },
  "output": {
    "description": "이 에이전트가 만드는 출력 설명",
    "format": "출력 형식",
    "files": ["생성하는 파일 경로 목록"]
  },
  "tools": ["이 에이전트가 사용할 수 있는 도구/명령 목록"],
  "constraints": {
    "max_attempts": 3,
    "timeout_seconds": 180,
    "sandbox": "이 에이전트의 권한 수준"
  }
}
```

### Orchestrator 역할

Orchestrator는:
1. `pool/*.json`의 에이전트 정의를 읽는다
2. 목표에 맞는 에이전트를 선택한다
3. 에이전트를 독립 subprocess로 실행한다
4. 결과를 수집하고 다음 에이전트에게 전달한다

**Orchestrator의 행동 제한**:
- `CLAUDE.md`, `AGENTS.md`, `GEMINI.md` 같은 컨텍스트 파일로 행동을 제한
- 에이전트 결과는 반드시 독립 subprocess를 통해 실행·생성

---

## Details

### 대시보드 설계 (Agent Pool 모니터링)

```
.pool/ 디렉토리의 에이전트들을 테이블 형태로 시각화

요구사항:
- 에이전트가 추가/삭제되면 테이블에 동적으로 반영
- 각 에이전트 행에 현재 상태(idle/running/completed/failed) 실시간 표시
- 에이전트가 실행될 때마다 라운드 번호와 해당 출력을 이력으로 누적
- 파이프라인 순서는 고정하지 말고, 어떤 에이전트든 풀에 등록되면 테이블에 나타나도록

Agent Pool Dashboard
┌──────────┬─────────────────────────┬───────────┬─────────┬───────────┐
│ ID       │ Role                    │ Status    │ Rounds  │ Last Run  │
├──────────┼─────────────────────────┼───────────┼─────────┼───────────┤
│ planner  │ 계획 수립               │ idle      │ 3       │ 14:32     │
│ reviewer │ 계획 검토               │ running   │ 2       │ 14:33     │
│ coder    │ 구현                    │ idle      │ 0       │ -         │
│ tester   │ 테스트                  │ idle      │ 0       │ -         │
└──────────┴─────────────────────────┴───────────┴─────────┴───────────┘
```

### Orchestrator 컨텍스트 파일 설계

```markdown
# AGENTS.md (프로젝트 루트)

당신은 Orchestrator입니다.

## 역할
pool/*.json의 에이전트 정의를 읽고, 목표에 맞는 에이전트를 선택하여 실행하라.
에이전트 결과는 반드시 독립 subprocess를 통해 실행되고 생성되어야 한다.

## 에이전트 선택 규칙
- 계획 수립 → planner
- 계획 검토 → reviewer
- 코드 구현 → coder
- 테스트 실행 → tester

## 제약
- 에이전트 파일 직접 수정 금지
- 에이전트 실행 결과를 직접 수정하지 마라
```

### Subprocess를 통한 Agent Team 구축

```python
import json
import subprocess
from pathlib import Path

class AgentPool:
    def __init__(self, pool_dir: str = ".pool"):
        self.pool_dir = Path(pool_dir)
        self.agents = self._load_agents()
    
    def _load_agents(self) -> dict:
        agents = {}
        for json_file in self.pool_dir.glob("*.json"):
            with open(json_file) as f:
                agent = json.load(f)
                agents[agent["id"]] = agent
        return agents
    
    def run_agent(self, agent_id: str, input_text: str) -> str:
        agent = self.agents[agent_id]
        system_prompt = agent["system_prompt"]
        timeout = agent["constraints"]["timeout_seconds"]
        
        result = subprocess.run(
            ["claude", "-p", "--system-prompt", system_prompt,
             "--output-format", "json", "--no-session-persistence"],
            input=input_text,
            capture_output=True, encoding="utf-8",
            timeout=timeout
        )
        
        if result.returncode != 0:
            raise RuntimeError(f"Agent {agent_id} failed: {result.stderr}")
        
        response = json.loads(result.stdout)
        return response["result"]

class Orchestrator:
    def __init__(self, pool: AgentPool):
        self.pool = pool
    
    def run_pipeline(self, goal: str) -> dict:
        """planner → reviewer → coder → tester 파이프라인 실행"""
        results = {}
        
        # Step 1: Plan
        plan = self.pool.run_agent("planner", goal)
        results["plan"] = plan
        Path("workspace/00_planning.md").write_text(plan)
        
        # Step 2: Review
        review = self.pool.run_agent("reviewer", plan)
        results["review"] = review
        Path("workspace/01_review.md").write_text(review)
        
        # Step 3: Code
        code = self.pool.run_agent("coder", plan)
        results["code"] = code
        
        # Step 4: Test
        test_result = self.pool.run_agent("tester", code)
        results["test"] = test_result
        
        return results
```

### 실습 Task 예시

```
CLI 에이전트에게 웹을 통해 GitHub 트렌드를 조사하고 리포트를 작성하는
자동화 Task를 수행하려면 어떤 에이전트가 필요할지 논의하고 구현한다.

필요 에이전트:
- researcher: GitHub 트렌드 웹 조사 (WebSearch 권한 필요)
- summarizer: 조사 결과 요약
- reporter: 최종 리포트 작성

각 에이전트를 pool/*.json에 등록하고 대시보드에서 진행 추적
```

---

## Related

- [[05-agent-specifications]] — Agent Spec JSON 스키마 설계
- [[07-harness-and-skills]] — Harness Engineering과 AGENTS.md
- [[03-cli-subprocess]] — subprocess로 에이전트 실행하기
- [[04-plan-mode-sequential-agents]] — 순차 에이전트 파이프라인
