---
title: "Model Context Protocol (MCP)"
tags: [mcp, context-engineering, agentic-coding, orchestrator]
source: "raw/8. Model Context Protocol.pdf"
date: 2026-06-13
related: ["[[06-agent-pool-orchestrator]]", "[[07-harness-and-skills]]", "[[09-loop-and-hooks]]"]
version: 1
---

# Model Context Protocol (MCP)

> MCP(Model Context Protocol)는 Claude, Codex, Gemini 같은 AI 에이전트가 다양한 외부 시스템과 동일한 방식으로 연결될 수 있도록 Anthropic이 만들고 OpenAI·Google 등이 참여하여 표준화한 프로토콜이다.

---

## Overview

MCP는 AI 에이전트를 위한 **USB 인터페이스**에 가깝다. USB가 다양한 기기를 하나의 표준 커넥터로 연결하듯, MCP는 다양한 외부 시스템(DB, API, 파일 시스템 등)을 AI 에이전트에 표준 방식으로 연결한다.

이전에는 AI 에이전트가 새로운 시스템과 연동할 때마다 커넥터 코드를 직접 작성하거나, 긴 시간 동안 분석 작업을 반복해야 했다. MCP는 이 비용을 줄이고 성능을 개선한다.

---

## Key Concepts

### MCP 등장 배경 (Why MCP)

**이전 (~2025)**:
- AI 에이전트가 DB, System, API를 이해하려면:
  - 분석 가능한 코드를 직접 작성하여 긴 시간 동안 분석
  - 커넥터 코드를 직접 작성
  - 또는 사람이 도구를 직접 만들어야 했음
- 성능이 좋지 않아 매번 복잡한 분석 작업 반복
- 하나의 서비스와 연결된 LLM 에이전트 시스템 구축·검증은 꽤 어려운 작업

**MCP 이후**:
- 표준화된 프로토콜 하나로 모든 시스템 연동
- 각 시스템의 API를 에이전트와 연동하는 비용 감소
- 성능 개선

### OOM 원칙 (객체지향 관점)

```
캡슐화: MCP를 사용하면 Tool Calling으로 일어나는 내부의 일에 대해
        AI Agent가 신경 쓸 필요가 없음

추상화: 다양한 시스템이 동일한 MCP 인터페이스로 추상화됨

다형성: 동일한 Tool Call 형식으로 다른 백엔드 시스템에 접근 가능
```

### MCP 트레이드오프: Context Explosion

맥가이버 나이프(도구 모음)에서 특정 도구 하나를 찾으려면?
→ **각 도구에 대한 기능 추론** 필요 → **Context Explosion**

MCP에 도구가 너무 많으면:
- 에이전트가 어떤 도구를 사용할지 추론하는 데 많은 컨텍스트 소비
- 실제 작업에 사용 가능한 컨텍스트 윈도우 감소

**해결 전략**:
- 관련 도구만 선택적으로 로드 (Routing)
- 도구 그룹화 및 계층화
- 불필요한 도구는 Pool에서 제외

### MCP 아키텍처

```
AI Agent (Claude/Codex/Gemini)
    │
    │ MCP 표준 프로토콜
    ▼
MCP Server
    ├── Tool 1: memo.create
    ├── Tool 2: memo.get
    ├── Tool 3: memo.list
    ├── Tool 4: memo.update
    └── Tool 5: memo.append
    │
    ▼
Backend System (SQLite, API, File System, ...)
```

---

## Details

### Orchestrator-Worker 패턴에서 MCP

```
Orchestrator Agent
    │
    ├── MCP → memo.create  (작업 기록 생성)
    ├── MCP → memo.get     (기존 기록 조회)
    │
    ▼ Subprocess
Worker Agent 1
Worker Agent 2
    │
    ├── MCP → memo.append  (결과 기록 추가)
    └── MCP → memo.update  (상태 업데이트)
```

### AgentMEMO 실습 구조

```
AgentMEMO
├── agentmemo/
│   ├── server.py      # FastMCP 기반 MCP 서버
│   └── repository.py  # SQLite 기반 저장소
└── ...

MCP Tools:
- memo.create  → 새 메모 생성
- memo.get     → 메모 조회 (ID 기반)
- memo.list    → 메모 목록 조회
- memo.update  → 메모 내용 수정
- memo.append  → 메모에 내용 추가 (Journal 패턴에 적합)
```

검증 Task:
```
1. agentmemo-server가 127.0.0.1:8000에서 실행
2. /mcp POST 수신
3. tools/list에 대해 5개 tool 반환
4. tools/call로 memo.create 호출 검증
5. SQLite에 저장됐는지 확인
```

### MCP vs 직접 API 호출 비교

| 항목 | 직접 API 호출 | MCP |
|---|---|---|
| 연동 방식 | 시스템마다 다른 코드 | 표준 프로토콜 하나 |
| 에이전트 학습 비용 | API 문서 분석 필요 | Tool 목록만 확인 |
| 확장성 | 시스템마다 커넥터 추가 | MCP 서버 추가로 확장 |
| 내부 구현 노출 | 에이전트가 내부 알아야 함 | 캡슐화됨 |
| Context 사용 | 분석에 많은 Context 사용 | Tool Call만 사용 |

### FastMCP로 MCP 서버 구현 (Python)

```python
from fastmcp import FastMCP
from pydantic import BaseModel

mcp = FastMCP("agentmemo-server")

class MemoCreate(BaseModel):
    title: str
    content: str

class MemoAppend(BaseModel):
    memo_id: str
    content: str

@mcp.tool()
def memo_create(data: MemoCreate) -> dict:
    """새 메모를 생성한다."""
    memo_id = repository.create(data.title, data.content)
    return {"id": memo_id, "status": "created"}

@mcp.tool()
def memo_append(data: MemoAppend) -> dict:
    """기존 메모에 내용을 추가한다. Journal 패턴에 사용."""
    repository.append(data.memo_id, data.content)
    return {"id": data.memo_id, "status": "appended"}

@mcp.tool()
def memo_get(memo_id: str) -> dict:
    """메모를 조회한다."""
    memo = repository.get(memo_id)
    return memo

if __name__ == "__main__":
    mcp.run(host="127.0.0.1", port=8000)
```

---

## Examples / Code

### Claude에서 MCP 서버 연결

```json
// .claude/settings.json
{
  "mcpServers": {
    "agentmemo": {
      "command": "python",
      "args": ["-m", "agentmemo.server"],
      "env": {}
    }
  }
}
```

### MCP를 통한 Journal 관리 (Harness 연동)

```python
# 에이전트가 작업 완료 후 Journal에 기록
# MCP Tool Call 형식

{
  "tool": "memo_append",
  "arguments": {
    "memo_id": "project-journal",
    "content": "- [2026-06-13 15:00] Implemented timeout parameter — pytest passes\n"
  }
}
```

### AgentMEMO 클론 및 실행

```bash
git clone https://github.com/INHA-SELAB/AgentMEMO
cd AgentMEMO
# AI에게 프로젝트 목표 분석 지시
claude -p "이 프로젝트의 목표를 분석하고, FastMCP를 이용하여 tools를 구현하는 방법을 설명해줘"
```

---

## Related

- [[07-harness-and-skills]] — Journal을 MCP로 외부 저장하는 패턴
- [[06-agent-pool-orchestrator]] — Orchestrator-Worker 패턴에서 MCP 활용
- [[09-loop-and-hooks]] — Loop와 Hook에서 MCP Tool 호출
