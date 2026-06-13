# SCHEMA — LLM Wiki 운영 방안

> 이 파일은 LLM Wiki의 **구조·형식·운영 규칙** 전체를 정의한다.  
> 페이지를 생성하거나 수정하는 모든 에이전트는 반드시 이 파일을 먼저 읽어야 한다.

---

## 1. 디렉토리 구조

```
my-wiki/
├── AGENTS.md          # LLM 유지보수 에이전트 행동 지침
├── SCHEMA.md          # 이 파일 — 위키 구조·운영 규칙
├── index.md           # 위키 전체 색인 (자동 갱신)
├── journal.md         # 유지보수 로그 (append-only, 절대 수정 금지)
├── raw/               # 원본 소스 자료 (PDF, 텍스트 등)
├── specs/             # 요구사항·설계 명세
├── wiki/              # 위키 페이지 (핵심 콘텐츠)
│   ├── 01-vibe-coding-and-agentic-coding.md
│   ├── 02-sdlc-pipeline.md
│   ├── 03-cli-subprocess.md
│   ├── 04-plan-mode-sequential-agents.md
│   ├── 05-agent-specifications.md
│   ├── 06-agent-pool-orchestrator.md
│   ├── 07-harness-and-skills.md
│   ├── 08-model-context-protocol.md
│   └── 09-loop-and-hooks.md
└── pipeline/
    ├── ingest.py      # raw → wiki 변환 파이프라인
    └── README.md      # 파이프라인 사용법
```

---

## 2. 파일 명명 규칙

| 대상 | 규칙 | 예시 |
|---|---|---|
| 위키 페이지 | `NN-kebab-case.md` (NN = 2자리 순번) | `07-harness-and-skills.md` |
| 원본 소스 | 원본 파일명 유지 | `7. Harness and Skills.pdf` |
| 슬러그 | 영문 소문자, 하이픈 구분 | `harness-and-skills` |

- 순번이 없는 신규 페이지는 현재 최대 순번 + 1로 부여
- 순번 변경 금지 (기존 링크 깨짐 방지)

---

## 3. 페이지 프론트매터 (Frontmatter)

모든 위키 페이지는 YAML 프론트매터로 시작해야 한다.

```yaml
---
title: "페이지 제목"
tags: [tag1, tag2, tag3]
source: "raw/원본파일명.pdf"
date: YYYY-MM-DD
related: ["[[slug1]]", "[[slug2]]"]
version: 1
---
```

### 필수 필드

| 필드 | 타입 | 설명 |
|---|---|---|
| `title` | string | 사람이 읽는 제목 |
| `tags` | list | 검색용 태그 (아래 태그 분류표 참고) |
| `source` | string | 원본 소스 경로 |
| `date` | YYYY-MM-DD | 최초 생성일 |
| `related` | list | 연관 페이지 (슬러그) |
| `version` | int | 수정 버전 (초기값 1, 갱신 시 +1) |

---

## 4. 페이지 본문 구조

```markdown
---
(frontmatter)
---

# 제목

> 한 줄 요약: 이 페이지가 다루는 핵심 개념을 한 문장으로.

---

## Overview

이 개념이 무엇인지, 왜 중요한지 2~4문단으로 설명.

## Key Concepts

### 개념 A
설명

### 개념 B
설명

## Details

심화 내용, 세부 구조, 트레이드오프 등.

## Examples / Code

코드 예시 또는 실습 예시.

## Related

- [[관련-페이지-슬러그]] — 관계 설명 한 줄
```

### 구조 규칙

- 섹션 순서는 Overview → Key Concepts → Details → Examples → Related 고정
- `##` 이하 섹션은 내용에 따라 자유롭게 추가 가능
- 코드 블록은 언어 명시 필수 (`python`, `bash`, `json`, `yaml` 등)
- 표(Table)는 비교·나열에 적극 사용

---

## 5. 내부 링크 문법

```markdown
[[page-slug]]                     # 기본 링크
[[page-slug|표시 텍스트]]          # 별칭 링크
```

- 슬러그는 파일명에서 `.md` 제거한 값 사용
- 존재하지 않는 슬러그 링크는 TODO로 표시: `[[미작성-페이지]]`

---

## 6. 태그 분류표

| 태그 | 대상 개념 |
|---|---|
| `agentic-coding` | 에이전틱 코딩 전반 |
| `vibe-coding` | 바이브 코딩 |
| `sdlc` | 소프트웨어 개발 생명주기 |
| `subprocess` | Python subprocess / CLI 호출 |
| `agent-design` | 에이전트 설계·명세 |
| `orchestrator` | 오케스트레이터 패턴 |
| `harness` | 하네스 엔지니어링 |
| `mcp` | Model Context Protocol |
| `hooks` | 훅 이벤트 |
| `loop` | 자동화 루프 |
| `plan-mode` | 계획 모드 |
| `pipeline` | 처리 파이프라인 |
| `context-engineering` | 컨텍스트 엔지니어링 |
| `skills` | 에이전트 스킬 |

---

## 7. index.md 갱신 규칙

`index.md`는 위키 전체의 진입점이다.

- 새 위키 페이지 생성 시 반드시 `index.md`에 행 추가
- 형식: `| [[slug\|제목]] | 태그 | 한 줄 요약 |`
- 순번 순서로 정렬 유지

---

## 8. journal.md 기록 규칙

```
- [YYYY-MM-DD HH:MM] <동작> `<대상>` — <결과>
```

예시:
```
- [2026-06-13 14:30] Ingested `raw/7. Harness and Skills.pdf` → `wiki/07-harness-and-skills.md`
- [2026-06-13 15:00] Updated `wiki/01-vibe-coding-and-agentic-coding.md` v1→v2 — added EPCC pattern
```

**절대 수정 금지. 오직 append만 허용.**

---

## 9. 갱신 조건

에이전트는 다음 조건에서 위키를 갱신해야 한다.

| 트리거 | 동작 |
|---|---|
| `raw/`에 새 파일 추가 | `pipeline/ingest.py` 실행 → 새 페이지 생성 + index 갱신 |
| 사용자가 없는 개념 질의 | 관련 페이지 생성 또는 기존 페이지 보강 |
| 기존 페이지 오류 발견 | 해당 페이지 수정, version +1, journal 기록 |
| 링크 깨짐 발견 | 대상 페이지 생성 또는 링크 수정 |

---

## 10. 품질 기준

위키 페이지는 다음을 만족해야 한다.

- [ ] 프론트매터 전체 필드 존재
- [ ] Overview 섹션이 개념을 독립적으로 설명 (다른 페이지 없이 읽혀야 함)
- [ ] 최소 1개의 내부 링크 `[[...]]` 포함
- [ ] 코드 예시가 있는 경우 언어 태그 명시
- [ ] Related 섹션에 최소 1개 연관 항목
