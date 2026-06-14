---
description: 기존 wiki 페이지를 업데이트합니다 (version 자동 증가)
---

# SKILL: wiki-update

기존 위키 페이지를 최소한의 변경으로 업데이트합니다.

## 실행 전 체크

1. `RULES.md` 읽기
2. 대상 `wiki/NN-slug.md` 읽기 (현재 내용 파악)

## 절차

**Step 1 — 현재 페이지 읽기**
- 프론트매터의 현재 version 번호 확인
- 수정이 필요한 섹션만 파악

**Step 2 — 최소 변경 원칙**
```
✅ 허용: 내용 추가, 오류 수정, 예시 보강
❌ 금지: 기존 내용 삭제, 구조 변경, title 변경
```

**Step 3 — 프론트매터 갱신**
```yaml
version: (기존 번호 + 1)
date: 오늘 날짜 (YYYY-MM-DD)
```

**Step 4 — 저장 후 journal 기록 (선택)**
```
- [YYYY-MM-DD HH:MM] Updated wiki/NN-slug.md v(N)→v(N+1) — <변경 이유 한 줄>
```
> Hook이 기본 write 이벤트를 자동 기록함. 변경 이유 등 추가 컨텍스트가 있을 때만 수동 append.

## 완료 보고 형식

```
✅ wiki/NN-slug.md v(N)→v(N+1) 업데이트 완료
   변경 내용: ...
   journal.md 기록 완료
```
