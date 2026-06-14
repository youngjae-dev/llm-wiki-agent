---
description: raw/ 폴더의 파일을 분석하여 wiki 페이지를 생성합니다
---

# SKILL: wiki-ingest

raw/ 폴더에 있는 파일을 wiki 페이지로 변환합니다.

## 실행 전 체크

1. `RULES.md` 읽기 (이미 읽었다면 생략)
2. `SCHEMA.md` 읽기 (프론트매터 형식 확인)
3. `index.md` 읽기 (현재 최대 페이지 번호 확인)
4. 대상 `raw/` 파일 읽기

## 절차

**Step 1 — 슬러그 결정**
- index.md에서 현재 최대 순번(NN) 확인
- 새 슬러그: `(NN+1)-kebab-case-제목.md`
- kebab-case: 공백→하이픈, 소문자, 한글은 영문으로 축약

**Step 2 — 프론트매터 작성**
```yaml
---
title: "페이지 제목"
tags: [관련태그1, 관련태그2]
source: "raw/파일명"
date: YYYY-MM-DD
related: ["[[연관슬러그]]"]
version: 1
---
```

**Step 3 — 본문 작성 (필수 섹션 순서)**
```
## Overview       ← 독립적으로 이해 가능한 요약 (3-5문장)
## Key Concepts   ← 핵심 개념 목록 (소제목 + 설명)
## Details        ← 세부 내용, 표, 비교
## Examples       ← 코드 예시 또는 적용 사례
## Related        ← [[slug]] 링크 목록
```

**Step 4 — 저장**
- `wiki/NN-slug.md`에 저장

**Step 5 — index.md 갱신**
- index.md 페이지 목록에 새 항목 추가:
  `| [[NN-slug]] | 태그 | 한 줄 요약 |`

**Step 6 — journal.md 기록 (선택)**
```
- [YYYY-MM-DD HH:MM] Ingested raw/<파일명> → wiki/NN-slug.md — <요약 한 줄>
```
> Hook이 기본 write 이벤트를 자동 기록함. 변환 이유·요약 등 추가 컨텍스트가 있을 때만 수동 append.

## 완료 보고 형식

```
✅ wiki/NN-slug.md 생성 완료
   제목: ...
   태그: [...]
   연관 페이지: [[...]]
   journal.md 기록 완료
```
