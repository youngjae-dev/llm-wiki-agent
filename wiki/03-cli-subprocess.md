---
title: "CLI & Subprocess — AI 에이전트 호출"
tags: [subprocess, agentic-coding, pipeline, agent-design]
source: "raw/3. Agents subprocess calling.pdf"
date: 2026-06-13
related: ["[[04-plan-mode-sequential-agents]]", "[[05-agent-specifications]]", "[[06-agent-pool-orchestrator]]"]
version: 1
---

# CLI & Subprocess — AI 에이전트 호출

> Python `subprocess.run()`을 통해 Claude/Codex/Gemini CLI를 프로그래밍 방식으로 호출하는 방법과, 멀티-에이전트 파이프라인에서의 응용을 다룬다.

---

## Overview

Coding(구현/개발)은 SDLC 단계 중 특정 단계의 극히 일부 활동에 불과하다. AI는 코드를 빠르고 정확하게 생성하지만, 그것만으로 좋은 시스템이 나오지는 않는다.

Subprocess는 단일 CLI 도구에서 **하나의 시스템(파이프라인)**으로 전환하는 핵심 메커니즘이다. Python에서 AI CLI를 subprocess로 호출하면 에이전트를 자동화된 파이프라인의 컴포넌트로 사용할 수 있다.

---

## Key Concepts

### CLI 호출의 두 가지 방식

**방식 1: 명령줄 인자 (터미널에서 직접 실행)**
```bash
claude -p "1+1의 답을 숫자만 말해줘"
```
프롬프트가 명령어의 일부로 전달됨.

**방식 2: stdin 파이프 (Python에서 실행)**
```python
import subprocess

# Claude
subprocess.run(
    ["claude", "-p"],
    input="1+1의 답을 숫자만 말해줘",
    capture_output=True,
    text=True
)

# Codex (darwin에서는 .cmd 제거)
subprocess.run(
    ["codex.cmd", "exec"],
    input="1+1의 답을 숫자만 말해줘",
    capture_output=True,
    text=True
)

# Gemini (darwin에서는 .cmd 제거)
subprocess.run(
    ["gemini.cmd", "-p", "1+1의 답을 숫자만 말해줘"],
    capture_output=True,
    text=True
)
```
프롬프트가 stdin(표준 입력)으로 전달됨.

### subprocess.run() 핵심 파라미터

```python
subprocess.run(
    cmd,              # 실행할 명령 리스트 (예: ["claude", "-p"])
    input=prompt,     # stdin으로 보낼 문자열 (프롬프트)
    capture_output=True,  # stdout/stderr를 캡처 (= stdout=PIPE, stderr=PIPE)
    encoding="utf-8", # 바이트 대신 문자열로 반환
    timeout=120,      # 최대 대기 시간 (초)
)
```

| 파라미터 | 역할 |
|---|---|
| `input` | 프로세스의 stdin에 문자열을 보내고 자동으로 닫는다 |
| `capture_output` | `stdout=PIPE, stderr=PIPE`의 축약형 |
| `text` | 입출력을 bytes 대신 str로 처리 → `encoding="utf-8"`로 오버라이딩 |
| `timeout` | 지정 시간 초과 시 `TimeoutExpired` 예외 발생 |

### CompletedProcess 반환값

`subprocess.run()`은 `CompletedProcess` 객체를 반환한다.

| 속성 | 타입 | 의미 | 예시 |
|---|---|---|---|
| `.returncode` | int | 프로세스 종료 코드 | `0` (성공) |
| `.stdout` | str | CLI가 출력한 내용 | `"2"` |
| `.stderr` | str | 에러/경고 메시지 | `""` (정상 시 비어 있음) |
| `.args` | list | 실행된 명령어 | `["claude", "-p"]` |

`returncode == 0`이면 성공 (Unix/Windows 공통 규칙).

---

## Details

### 에이전트별 CLI 명령 빌더

```python
import subprocess
import os

def pick_binary(agent: str) -> str:
    if agent == "codex":
        return "codex.cmd" if os.name == "nt" else "codex"
    if agent == "gemini":
        return "gemini.cmd" if os.name == "nt" else "gemini"
    if agent == "claude":
        return "claude"
    raise ValueError(f"Unknown agent: {agent}")

def build_cli_command(agent: str, prompt: str | None = None) -> list[str]:
    """
    에이전트 이름을 받아 oneshot CLI 명령 리스트를 반환한다.
    Gemini는 -p에 프롬프트가 필수이므로 prompt를 명령에 포함한다.
    Claude/Codex는 stdin으로 전달하므로 prompt를 명령에 포함하지 않는다.
    """
    exe = pick_binary(agent)
    if agent == "codex":
        # --skip-git-repo-check: Git 저장소 밖에서도 실행 가능
        return [exe, "exec", "--ephemeral", "--json", "--skip-git-repo-check"]
    if agent == "gemini":
        return [exe, "-p", prompt or "", "--output-format", "json"]
    if agent == "claude":
        return [exe, "-p", "--no-session-persistence", "--output-format", "json"]
    raise ValueError(f"Unknown agent: {agent}")

def run_agent(agent: str, prompt: str, timeout: int = 120) -> subprocess.CompletedProcess:
    cmd = build_cli_command(agent, prompt)
    use_stdin = prompt if agent != "gemini" else None
    return subprocess.run(
        cmd,
        input=use_stdin,
        capture_output=True,
        encoding="utf-8",
        timeout=timeout,
    )
```

### Claude JSON 응답 형식

```json
{
  "type": "result",
  "subtype": "success",
  "is_error": false,
  "duration_ms": 3063,
  "result": "\n\n2",
  "stop_reason": "end_turn",
  "session_id": "3a54ec45-3a23-400f-b60b-93debebc51c4",
  "total_cost_usd": 0.045919,
  "usage": {
    "input_tokens": 3,
    "cache_creation_input_tokens": 6624,
    "cache_read_input_tokens": 8758,
    "output_tokens": 5
  }
}
```

### 응답 파싱

```python
import json

# Claude, Gemini
response = json.loads(result.stdout)
text = response["result"]

# Codex (NDJSON — 줄마다 JSON 오브젝트)
lines = [json.loads(line) for line in result.stdout.strip().splitlines()]
```

### 세션 제어 (Session Control)

```python
SESSION_ID = "841f676a-cb80-4590-b885-351656184c57"

# Claude — 세션 이어가기
subprocess.run(
    ["claude", "-p", "--resume", SESSION_ID, "--output-format", "json"],
    input="이전 질문을 확인해주세요.",
    capture_output=True, encoding="utf-8"
)

# Codex
subprocess.run(
    ["codex", "exec", "resume", SESSION_ID, "--skip-git-repo-check", "이전 질문을 확인해주세요."],
    capture_output=True, encoding="utf-8"
)

# Gemini
subprocess.run(
    ["gemini", "--resume", SESSION_ID, "-p", "이전 질문을 확인해주세요."],
    capture_output=True, encoding="utf-8"
)
```

세션 영속성 제거 플래그:
- Claude: `--no-session-persistence`
- Codex: `--ephemeral`

### 에이전트 권한 수준

```bash
# 최고 권한 (YOLO Mode) — 주의 필요
claude --dangerously-skip-permissions
gemini --yolo
codex --dangerously-bypass-approvals-and-sandbox
```

**권한 수준이 높을 때의 단점**: 사용자가 완전한 제어권을 잃음. 에이전트가 멈춰야 할 순간에 멈추지 않을 수 있음.

---

## Examples / Code

### 환경 초기화

```python
import subprocess
import sys
import os
import time
import threading
import json

print(f"Python: {sys.version}")
print(f"OS: {os.name} ({sys.platform})")
print(f"CWD: {os.getcwd()}")

# CLI 설치 확인
def check_cli(agent: str) -> bool:
    binary = pick_binary(agent)
    try:
        result = subprocess.run([binary, "--version"], capture_output=True, text=True, timeout=10)
        version = result.stdout.strip() or result.stderr.strip()
        print(f"  {agent}: {version}")
        return True
    except FileNotFoundError:
        print(f"  {agent}: 설치되지 않음")
        return False

check_cli("claude")
```

### 실제 실행 예시

```python
MY_AGENT = "claude"

result = run_agent(MY_AGENT, "1+1의 답을 숫자만 말해줘")

if result.returncode == 0:
    response = json.loads(result.stdout)
    print(response["result"])  # "\n\n2"
else:
    print(f"Error: {result.stderr}")
```

### 팁: Claude + Codex 협업

```
Claude의 Skill에 Codex를 Implementation 담당으로 등록
Codex의 Skill에 Claude를 Review 담당으로 등록
→ CLI 레벨에서 간단한 에이전틱 코딩 체계 확보 가능
```

---

## Related

- [[04-plan-mode-sequential-agents]] — 순차 에이전트 파이프라인과 핸드오프 파일
- [[05-agent-specifications]] — System Prompt 주입 방법
- [[06-agent-pool-orchestrator]] — Agent Pool과 Orchestrator 패턴
- [[09-loop-and-hooks]] — 자동화 Loop과 Hook 이벤트
