---
title: "SDLC Pipeline in Vibe/Agentic Coding"
tags: [sdlc, agentic-coding, vibe-coding, pipeline, context-engineering]
source: "raw/2. SDLC pipeline in Vibe coding.pdf"
date: 2026-06-13
related: ["[[01-vibe-coding-and-agentic-coding]]", "[[04-plan-mode-sequential-agents]]", "[[05-agent-specifications]]"]
version: 1
---

# SDLC Pipeline in Vibe/Agentic Coding

> AI-Assisted 코딩 시대에서도 SDLC(Software Development Life Cycle)는 필수이며, PRD 기반 Spec-Driven Development가 품질을 보장하는 핵심 접근법이다.

---

## Overview

단순한 정렬 알고리즘 시각화 도구 하나를 만드는 데에도, 체계적인 Requirements가 정의되지 않으면 사용자가 기대하는 결과를 내기 어렵다. 복잡한 정보 시스템이나 Embedded 시스템에서는 더 큰 문제이며, 구체적인 문서화와 이해관계자 논의 없이는 제대로 된 시스템을 개발할 수 없다.

AI가 코드를 생성하는 시대에도 SDLC는 사라지지 않는다. 오히려 에이전트가 각 단계를 담당하는 구조로 진화한다.

---

## Key Concepts

### SDLC (Software Development Life Cycle)

| 단계 | 핵심 질문 | 주요 활동 |
|---|---|---|
| Planning | 무엇을 왜 만드는가? | System Request, Feasibility Analysis |
| Analysis | 무엇이 필요한가? | 요구사항 수집, 분석 모델 |
| Design | 어떻게 만드는가? | 아키텍처, 인터페이스, DB 설계 |
| Implementation | 실제로 만든다 | 코딩, 테스트, 배포 |

### System Requests (시스템 요청서)

새 프로젝트 시작 시 반드시 정의해야 하는 5가지 요소:

| 항목 | 질문 | 설명 |
|---|---|---|
| Project Sponsor | 누가 이 프로젝트를 원하는가? | 의뢰자·후원자 |
| Business Need | 왜 만드는가? | 문제·기회 |
| Business Requirements | 무엇을 제공해야 하는가? | 기능 요구사항 |
| Business Value | 만들면 뭐가 좋은가? | 기대 효과 |
| Special Issues/Constraints | 제약조건은 무엇인가? | 시간·비용·규정·성능 |

### PRD (Product Requirements Document)

**Spec-Driven Development**의 핵심 산출물. 코딩 시작 전에 PRD를 먼저 작성한다.

PRD 포함 요소:
- **Target User**: 누가 사용하는가?
- **Key Feature**: 핵심 기능은 무엇인가?
- **Constraint**: 제약조건 (브라우저 기반, 단일 파일 등)
- **Acceptance Criteria**: 완료 기준 (측정 가능해야 함)

```
PRD 없이 생성: "랜덤화된 퀵정렬을 시각화해줘" → 그럭저럭 동작하는 UI
PRD 포함 생성: Target User + Key Feature + Constraint + AC → 월등히 향상된 결과물
```

### Vibe Coder의 작업 방식

```
1. PRD(Product Requirements Document)를 먼저 작성
2. PRD + 단계별 계획(Plan)을 AI와 협업하여 작성, 작업 분해
3. SRS(Software Requirements Spec)를 LLM과 논의
4. PRD + 수용 기준(AC)이 포함된 User Story 산출
→ Why → What → How 달성
```

---

## Details

### 단위 수준 vs 전체 시스템 개발

| 구분 | Simple Tool (단위) | Product (전체 시스템) |
|---|---|---|
| Stakeholders | User | User, Admin, Operators, … |
| Expectations | Low | Extremely High |
| Non-Functional Req. | None or Small | Performance, Security, Extendability, … |
| Integration | None or Small | DB, Auth, API, … |
| Failure Costs | Low | High |

### 비체계적 개발의 문제점

Incremental Requirements(점진적 요구사항)만 있는 경우:
```
일단 뭔가 만든다 → 결과 확인 → 분석 → 수정
→ 비체계적 개발 → 기술부채 누적
```

### 에이전트 구조별 SDLC 처리

**Single Agent**:
```
사용자 프롬프트 → 단일 에이전트 → 출력
(사용자의 요청은 명확하고 구조화되어 있어야 함)
```

**Sequential Agent**:
```
각 에이전트가 독립적으로 작동, 앞 단계 완료 후 다음 단계 시작
→ 태스크 순서와 의존관계를 사전에 정확히 설계 (= SDLC Analysis 단계의 작업 분해)
```

**Parallel Agent**:
```
하나의 입력을 여러 전문 서브 에이전트가 동시에 처리, 독립된 결과 산출
→ Research/WebSearch에서 강력한 접근
```

### YOLO Mode (주의)

```bash
claude --dangerously-skip-permissions
gemini --yolo
codex --dangerously-bypass-approvals-and-sandbox
```

각 도구에게 무제한적 권한 부여. 사용 시 주의:
- 권한 수준이 높으면 사용자가 완전한 제어권을 잃음
- 테스트 완료 후 산출물과 테스트용 코드를 복구 불가능하게 삭제하는 사고 발생 가능

---

## Examples / Code

### Case: Quicksort Algorithm Viewer PRD

```markdown
# PRD: Randomized Quicksort Viewer

## Target User
정렬 알고리즘은 이해하지만 Randomized Quicksort를 모르는 학습자

## Key Feature
- 상세 로그
- 시간복잡도 O(n log n) 시각적 추적
- 단계별 실행

## Constraint
- 브라우저 기반, 단일 HTML 파일

## Acceptance Criteria
사용자가 pivot 선택의 무작위성이 최악 케이스를 방지하는 원리를
이해할 수 있어야 함
```

### CLI 최초 실행

```bash
# 설치 후 최초 실행 시 Web-Auth 필요
claude    # Claude Code
codex     # OpenAI Codex CLI
gemini    # Google Gemini CLI

# 세션 이어가기
claude -c                          # 최근 세션 즉시
claude --resume                    # 세션 목록에서 선택
claude --resume <session-id>       # 특정 세션으로
```

### 실습 도구 (Agentic Coding 체험)

```bash
git clone https://github.com/INHA-SELAB/cse3308_easy_agent.git
cd cse3308_easy_agent
python main.py
```

---

## Related

- [[01-vibe-coding-and-agentic-coding]] — 바이브 코딩과 에이전틱 코딩의 개념 정의
- [[04-plan-mode-sequential-agents]] — Plan Mode와 순차 에이전트 파이프라인
- [[05-agent-specifications]] — 에이전트 명세(System Prompt) 설계
- [[07-harness-and-skills]] — Contract-Driven Iteration과 TASK.md
