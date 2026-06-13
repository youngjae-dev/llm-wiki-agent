# RULES.md — 에이전트 하네스 운영 지침

> 이 파일은 모든 에이전트 세션의 **최우선 규칙**이다.  
> `AGENTS.md`(역할 정의), `SCHEMA.md`(구조 규약)보다 이 파일이 우선한다.

---

## 0. 세션 시작 의식 (Mandatory)

```
모든 세션은 아래 순서로 시작한다:
1. RULES.md (이 파일) 전체 읽기
2. journal.md 마지막 10줄 읽기
3. index.md 읽기 (현재 위키 상태 파악)
4. 사용자 요청 처리
```

---

## 1. 파일 접근 규칙

| 경로 | 읽기 | 쓰기 | 삭제 |
|---|---|---|---|
| `wiki/*.md` | ✅ | ✅ | ❌ (비활성화만) |
| `raw/` | ✅ | ❌ | ❌ |
| `journal.md` | ✅ | append만 | ❌ |
| `index.md` | ✅ | ✅ | ❌ |
| `RULES.md` / `SCHEMA.md` | ✅ | ❌ | ❌ |
| `tools/` | ✅ | ❌ | ❌ |
| `.claude/` | ✅ | ❌ | ❌ |

---

## 2. 절대 금지 행동

```
❌ raw/ 파일 수정 또는 삭제
❌ journal.md 기존 내용 수정 (append 전용)
❌ RULES.md / SCHEMA.md 사용자 승인 없이 변경
❌ 한 세션에서 wiki 페이지 3개 초과 동시 생성
❌ 존재하지 않는 [[slug]] 링크를 확인 없이 사용
❌ 외부 API 직접 호출 (subprocess 또는 MCP Tool만 허용)
```

---

## 3. 위키 페이지 작성 기준

새 페이지를 만들기 전 반드시 SCHEMA.md를 읽고 다음을 준수한다:

- 파일명: `NN-kebab-case.md` (현재 최대 순번 + 1)
- 프론트매터 전체 필드 필수 (title, tags, source, date, related, version)
- 본문 구조: Overview → Key Concepts → Details → Examples → Related
- 내부 링크 `[[slug]]` 최소 1개 포함
- 저장 후 반드시 `journal.md`에 기록

---

## 4. journal.md 기록 규칙

형식: `- [YYYY-MM-DD HH:MM] <동작> <대상> — <결과>`

```
예시:
- [2026-06-15 10:30] Ingested raw/my-doc.md → wiki/17-my-topic.md
- [2026-06-15 10:35] Updated wiki/12-architecture-patterns.md v1→v2 — 예제 코드 추가
- [2026-06-15 10:40] Query: "캐싱 전략?" — wiki/14-system-design-basics.md 참조
```

---

## 5. SKILL 실행 기준

`.claude/commands/` 아래 SKILL을 실행할 때:

- **wiki-ingest**: raw/ 파일이 존재하는지 먼저 확인. 없으면 중단.
- **wiki-query**: index.md → 해당 wiki/*.md 순서로 탐색. 없으면 "페이지 없음" 보고.
- **wiki-update**: 기존 페이지 내용 유지 최대화. 필요한 부분만 수정.

---

## 6. 막힌 경우 처리

```
1. 같은 방법으로 2번 이상 실패 → 멈추고 journal.md에 기록
2. 원본 내용 모호 → 추측하지 말고 사용자에게 질문
3. 슬러그 충돌 → 순번 재확인 후 사용자 승인
```

---

## 7. 컨텍스트 파일 목록

| 파일 | 역할 |
|---|---|
| `RULES.md` | 최우선 운영 규칙 (이 파일) |
| `AGENTS.md` | 에이전트 역할·권한 명세 |
| `SCHEMA.md` | 위키 구조 규약 |
| `index.md` | 전체 페이지 목차 |
| `journal.md` | 감사 로그 (append-only) |
| `.claude/commands/*.md` | 실행 가능한 SKILL 목록 |
