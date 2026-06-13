---
title: "Vibe Coding & Agentic Coding"
tags: [vibe-coding, agentic-coding, sdlc, context-engineering]
source: "raw/1. Vibe coding and Agent coding.pdf"
date: 2026-06-13
related: ["[[02-sdlc-pipeline]]", "[[05-agent-specifications]]"]
version: 1
---

# Vibe Coding & Agentic Coding

> 소프트웨어 엔지니어링의 진화 흐름과, 자연어 기반 개발 패러다임인 바이브 코딩 및 에이전틱 코딩의 개념·차이를 정의한다.

---

## Overview

소프트웨어 엔지니어링은 세 단계를 거쳐 진화했다.

1. **하드웨어 종속 단계 (1940~)**: 물리 회로, 천공카드, 어셈블리
2. **추상화/프레임워크 단계 (~2024)**: 컴파일 언어, 인터프리터 언어, 클라우드
3. **지능형 시스템 시대 (2024~)**: 자연어·의도 기반 프로그래밍, AI-Assisted 개발·자동화

이 변화 속에서 개발자의 역할은 코드 작성자에서 **시스템 설계자 + 오케스트레이터**로 전환되고 있다.

---

## Key Concepts

### System (시스템)

> A system is a set of interacting, interrelated, or interdependent components forming a complex, unified whole that works together to achieve a common purpose or goal.

시스템의 구성 요소:

| 요소 | 설명 |
|---|---|
| Goal | 달성하려는 목적 |
| Components | 구성 요소 (Builder 포함) |
| Interactions | 컴포넌트 간 상호작용 규칙 |
| Boundaries | 시스템 내부와 외부의 경계 |
| Constraints | 시간·비용·규정·성능 제약 |

### System Analysis (시스템 분석)

시스템 분석의 역할:
- 사용자/운영/비즈니스가 원하는 목표 도출
- 시스템 범위(안/밖)와 제약을 명확화
- 요구사항을 모델·명세(Use Case, BPMN/DFD, ERD 등)로 검증 가능하게 변환
- 제약 내에서 우선순위·리스크·대안 설계

책임 분담:

| 역할 | 책임 |
|---|---|
| 시스템 설계자 | 의사결정 및 책임 |
| 프로젝트 관리자 | 계획 수립 및 관리 |
| 소프트웨어 엔지니어 | 구현 및 검증 |

### Vibe Coding (2024.4Q ~ 2025.3Q 트렌드)

**정의**: 자연어로 목표/제약을 말하고, LLM이 코드를 만들게 하는 방식.

**개발자 역할 전환**:
- 기존: 구문·로직을 직접 작성, 컴파일·테스트로 반복 개선
- 바이브 코딩: 개념적 개요와 구조 전달 (데이터, API, 플랜), 점진적 개선 (v1 → v1.1 → …), 분위기(vibe) — 스타일/우선순위/트레이드오프 전달

**인지적 전환**:
- 저수준 구현 세부사항의 부담 감소
- 창의적 문제 해결, UX 디자인, 시스템 아키텍처에 집중
- 구문 암기 → 개념적 표현과 전략적 상호작용 강조

**한계**: 코드 규모 증가 시 일관성·검증·운영에서 기술 부채가 빠르게 누적됨.

### Agentic Coding (2025.4Q ~)

**정의**: 코딩 에이전트를 통해 SDLC가 보장되는 개발 프로세스를 수행하는 방식.

바이브 코딩이 "Accept All"로 밀어붙이는 방식이라면, 에이전틱 코딩은 SDLC 각 단계를 에이전트가 담당하여 일관성과 검증을 보장한다.

---

## Details

### 에이전트 구조 유형

| 유형 | 설명 | 적합한 규모 |
|---|---|---|
| Single Agent | 단일 대화로 처리 | 소규모 앱 |
| Sequential Agent | 앞 단계 완료 후 다음 단계 시작 | 중규모 |
| Parallel Agent | 독립 서브 에이전트가 동시에 처리 | 연구·리서치 |
| Multi-Agent | 복합 구조 | 대규모 제품 |

### Vibe Coding vs Agentic Coding 비교

| 항목 | Vibe Coding | Agentic Coding |
|---|---|---|
| 접근 방식 | One-Shot Generation | Description per each Agents |
| 문서화 | PRD/SRS 링크 또는 없음 | Appropriate Prompt + PRD/SRS |
| 인간의 역할 | Prompt Engineering | Orchestrator |
| 에이전트 구조 | Single Conversation | Single → Sequential → Multi-Agent |
| SDLC 단계 | Simple Loop | Co-operation with AI after SDLC Step |

### Software Engineer의 역할 (주니어 관점)

- 협업 과정 학습: PR/코드리뷰, 이슈추적, Git, 협업 Tool
- 코드베이스 분석 및 버그 분석
- 기존 시스템과 호환 가능한 소규모 기능 개발
- 문서 작성: 보고서, 협업을 위한 명세서

> 소프트웨어 엔지니어 = 한 기업의 시스템을 구성하는 Component의 일부  
> 산출물 = 기업과 시스템이 목표를 달성하도록 하는 포괄적인 Solutions

---

## Examples / Code

### Requirements (강의 기준)

```
- 1개 이상의 CLI를 지원하는 유료 LLM 구독 필요
  - (추천) Anthropic Claude
  - Open AI ChatGPT
  - Google Gemini

- CLI 설치:
  claude  (Claude Code)
  codex   (OpenAI Codex CLI)
  gemini  (Google Gemini CLI)
```

### 참고 자료

- Andrej Karpathy — Vibe Coding 개념 제안
- Dario Amodei (CEO of Anthropic) — "The End of Programming as We Know It"
- Sapkota et al. (2025) — "Vibe coding vs. agentic coding: Fundamentals and practical implications"

---

## Related

- [[02-sdlc-pipeline]] — SDLC와 PRD 기반 Spec-Driven Development
- [[05-agent-specifications]] — 에이전트 명세 설계 (Role, Input, Output)
- [[06-agent-pool-orchestrator]] — Orchestrator 패턴과 Agent Pool
- [[07-harness-and-skills]] — Harness Engineering과 Contract-Driven Iteration
