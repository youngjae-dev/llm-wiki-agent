---
title: "Loop & Hooks — 자동화와 결정론적 제어"
tags: [loop, hooks, agentic-coding, harness]
source: "raw/9. Loop and Hooks.pdf"
date: 2026-06-13
related: ["[[07-harness-and-skills]]", "[[06-agent-pool-orchestrator]]", "[[08-model-context-protocol]]"]
version: 1
---

# Loop & Hooks — 자동화와 결정론적 제어

> Hook은 에이전트의 생애주기 특정 시점에 자동으로 실행되는 스크립트이며, Loop은 에이전트를 주기적으로 재실행하는 자동화 메커니즘이다. 이 둘은 에이전트의 확률적 오류를 **결정론적 결과물**로 보정하는 핵심 수단이다.

---

## Overview

AI 에이전트는 확률에 따른 잘못된 결정을 내릴 수 있다. Hook은 에이전트 생애주기의 특정 시점에 결정론적 스크립트를 주입하여, 에이전트가 무엇을 하든 반드시 통과해야 하는 체크포인트를 만든다.

> "AI Agent가 확률에 따른 잘못된 결정을 내릴 수 있는 부분들을 Hook을 이용하여 결정론적인 결과물을 낼 수 있도록 하는 것이 주 목적이다."

---

## Key Concepts

### Hook

**정의**: 에이전트의 생애주기 동안 특정 시점/조건 만족 시마다 자동으로 실행 가능한 스크립트.

### Hook Events (이벤트 유형)

| 이벤트 | 발생 시점 |
|---|---|
| `UserPromptSubmit` | 사용자가 프롬프트를 제출했을 때 |
| `PreToolUse` | 에이전트가 도구를 쓰기 직전 |
| `PostToolUse` | 도구 실행이 끝난 직후 |
| `PermissionRequest` | 권한 요청이 발생할 때 |
| `Stop` | 한 turn이 끝나려 할 때 |
| `SessionStart` | 세션 시작/재개 시점 |

### Loop

**정의**: 에이전트를 일정 주기 또는 조건 만족까지 반복 실행하는 자동화 메커니즘.

**지원 범위**:
- Claude: 거의 독점적 지원
- Codex/Gemini: OS에서 제공하는 Scheduler 기능 활용 필요 (cron 등)

---

## Details

### Hook 유의미한 사용 패턴

#### At `Stop` (작업 완료 시점)

```bash
# 작업 완료 보고 및 exit code 검증
# timeout 10s 정도로 정상 exit code 발행되는지 확인
# 특정 에이전트가 작업 완료 시 SDK/subprocess로 다른 에이전트 작동
```

**예시**:
```json
{
  "hooks": {
    "Stop": [{
      "matcher": "",
      "hooks": [{
        "type": "command",
        "command": "bash -c 'cd /project && npm test 2>&1 | tail -5'",
        "timeout": 10
      }]
    }]
  }
}
```

#### At `PostToolUse` (도구 사용 후 기록)

```bash
# 어떤 도구를 사용했는지 기록 남기기 (LOG)
```

**예시**:
```json
{
  "hooks": {
    "PostToolUse": [{
      "matcher": ".*",
      "hooks": [{
        "type": "command",
        "command": "echo \"[$(date)] Tool used: $TOOL_NAME\" >> tool_log.txt"
      }]
    }]
  }
}
```

#### At `UserPromptSubmit` (사용자 입력 시 전처리)

```bash
# 사용자의 지시에 대해 /docs와 같은 지식 베이스에 이미 존재하는지 체크
# 추가 프롬프트 강제 주입
```

**예시 (LLM Wiki 연동)**:
```bash
#!/bin/bash
# 사용자 질의가 wiki에 있는지 확인하여 컨텍스트 추가
QUERY="$USER_PROMPT"
WIKI_MATCH=$(grep -r "$QUERY" /path/to/wiki/ --include="*.md" -l 2>/dev/null | head -3)

if [ -n "$WIKI_MATCH" ]; then
  echo "📖 관련 위키 페이지:"
  echo "$WIKI_MATCH"
fi
```

### Loop 사용 시 주의사항

**비용 고려**:
```
Loop가 Read/Write를 수반하는 경우:
→ 일정 시간마다 작업 비용 발생
→ 고가 요금제가 아니라면 단순 Status Checking 위주로 활용 권장
```

**비용 최적화 아이디어**:
```
개인 GPU로 Qwen3.5 27b 같은 로컬 모델을 vllm/Ollama로 호출 가능한 경우:
- fire (트리거) → 상용 LLM 에이전트
- action (실행) → 로컬 에이전트를 API로 호출
→ 비용 절감
```

### Claude Loop 예시

```bash
# Claude Code에서 Loop 시작
/loop 5m "현재 디렉토리의 git status를 확인하고 변경사항이 있으면 요약하라"

# 자율 루프 (모델이 간격 결정)
/loop "빌드 상태를 모니터링하고 실패 시 알려라"
```

**Loop 간격 선택**:
```
캐시 TTL = 5분

캐시 유지: 60s~270s (외부 상태 빠르게 변할 때)
캐시 만료: 300s+ (긴 작업 대기, 비용 아낄 때)

일반 idle 체크: 1200s~1800s (20~30분)
```

### Hook Configuration 예시 (Claude settings.json)

```json
{
  "hooks": {
    "UserPromptSubmit": [{
      "matcher": "",
      "hooks": [{
        "type": "command",
        "command": "python /path/to/wiki_lookup.py",
        "timeout": 5
      }]
    }],
    "PostToolUse": [{
      "matcher": "Bash|Edit|Write",
      "hooks": [{
        "type": "command",
        "command": "echo \"[$(date '+%H:%M:%S')] $TOOL_NAME\" >> ~/.claude/tool_usage.log"
      }]
    }],
    "Stop": [{
      "matcher": "",
      "hooks": [{
        "type": "command",
        "command": "bash -c 'cd $PROJECT_DIR && python -m pytest -q --tb=no 2>&1 | tail -3'",
        "timeout": 10
      }]
    }]
  }
}
```

### LLM Wiki에서 Hook 활용 패턴

```
At UserPromptSubmit:
  1. 사용자 질의 키워드 추출
  2. wiki/*.md에서 관련 페이지 검색
  3. 발견 시 컨텍스트에 추가 주입
  → 에이전트가 위키를 먼저 참조하도록 강제

At Stop (에이전트 작업 완료 시):
  1. journal.md에 현재 세션 요약 자동 append
  2. index.md 갱신 여부 확인
  → 위키 유지보수 자동화
```

---

## Examples / Code

### 위키 질의 Hook 스크립트 (wiki_lookup.py)

```python
#!/usr/bin/env python3
"""
UserPromptSubmit Hook: 사용자 질의를 위키에서 검색하여
관련 페이지를 stderr로 출력 (에이전트 컨텍스트에 주입됨)
"""
import os
import sys
import re
from pathlib import Path

WIKI_DIR = Path(__file__).parent.parent / "wiki"
USER_PROMPT = os.environ.get("USER_PROMPT", sys.stdin.read()).strip()

keywords = set(re.findall(r'\w{3,}', USER_PROMPT.lower()))
results = []

for md_file in WIKI_DIR.glob("*.md"):
    content = md_file.read_text(encoding="utf-8").lower()
    score = sum(1 for kw in keywords if kw in content)
    if score >= 2:
        results.append((score, md_file.name))

results.sort(reverse=True)

if results:
    print("\n📖 관련 위키 페이지 (우선 참조 권장):")
    for score, name in results[:3]:
        print(f"  - wiki/{name}")
```

### OS Cron 기반 Loop (Codex/Gemini 대안)

```bash
# crontab -e
# 매 30분마다 GitHub 트렌드 체크
*/30 * * * * cd /project && gemini -p "GitHub 트렌드를 확인하고 새로운 항목을 wiki/trends.md에 추가하라" >> /var/log/wiki_update.log 2>&1
```

---

## Related

- [[07-harness-and-skills]] — Harness Engineering: Hook이 결정론적 제어를 보장하는 방법
- [[06-agent-pool-orchestrator]] — Stop Hook에서 다음 에이전트 작동
- [[08-model-context-protocol]] — Hook에서 MCP Tool 호출
- [[03-cli-subprocess]] — Loop/Hook에서 subprocess로 에이전트 실행
