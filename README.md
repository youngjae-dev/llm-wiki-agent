# LLM Wiki Agent

> **자신의 문서를 넣으면 AI 에이전트가 구조화된 위키 페이지를 만들어 주는 도구.**  
> MCP 서버 + Streamlit 뷰어 + Claude 에이전트 하네스로 구성됩니다.

---

## 30분 퀵스타트

> 이 가이드를 따라하면 **30분 안에 자신의 자료 1건으로 첫 위키 페이지를 만들고 화면에서 확인**할 수 있습니다.

### Step 0 — 사전 요구사항

| 필요 항목 | 확인 방법 | 설치 |
|---|---|---|
| Python 3.10+ | `python3 --version` | [python.org](https://python.org) |
| Claude CLI | `claude --version` | `npm i -g @anthropic-ai/claude-code` |
| poppler (PDF용) | `pdftotext -v` | `brew install poppler` (macOS) |

### Step 1 — 클론 및 설치

```bash
git clone https://github.com/youngjae-dev/llm-wiki-agent.git
cd llm-wiki-agent

# 가상환경 사용 권장
python3 -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

pip install streamlit fastmcp
```

### Step 2 — 자신의 자료 추가

`raw/` 폴더에 자신의 파일을 넣습니다.

```bash
# 마크다운 파일
cp ~/내문서.md raw/

# PDF 파일
cp ~/내자료.pdf raw/
```

### Step 3 — 위키 페이지 생성

**방법 A: Claude Code에서 SKILL 실행 (권장)**

Claude Code를 실행한 후:

```
/wiki-ingest
```

Claude가 `raw/` 파일을 분석해 `wiki/` 페이지를 자동 생성합니다.

**방법 B: 파이프라인 직접 실행**

```bash
# 단일 파일
python3 pipeline/ingest.py "raw/내문서.md"

# raw/ 전체
python3 pipeline/ingest.py --all
```

### Step 4 — 뷰어에서 확인

```bash
streamlit run tools/app.py
```

브라우저에서 `http://localhost:8501` 열기 → 좌측 사이드바에서 새 페이지 확인

> ⚠️ 우측 채팅 패널은 Claude CLI(`claude`)를 subprocess로 호출합니다.
> Claude CLI가 설치되지 않았거나 로그인되지 않은 경우 채팅 패널만 동작하지 않습니다. 나머지 뷰어 기능은 정상 동작합니다.

### Step 5 — 검증

```bash
# wiki 페이지가 생성됐는지 확인
ls wiki/

# journal에 기록됐는지 확인
tail -5 journal.md

# MCP 서버 동작 확인
python tools/mcp_server.py
```

---

## 프로젝트 구조

```
llm-wiki-agent/
├── .claude/
│   └── commands/            # 에이전트 SKILL
│       ├── wiki-ingest.md   # /wiki-ingest: raw 파일 → wiki 페이지
│       ├── wiki-query.md    # /wiki-query: 위키 검색 및 답변
│       └── wiki-update.md   # /wiki-update: 기존 페이지 업데이트
│
├── tools/                   # 시각화 도구
│   ├── mcp_server.py        # FastMCP 서버 (9개 Tool)
│   └── app.py               # Streamlit 3-패널 뷰어
│
├── pipeline/
│   └── ingest.py            # raw/ → wiki/ 변환 파이프라인
│
├── wiki/                    # 생성된 위키 페이지 (Markdown)
├── raw/                     # 원본 소스 파일 (편집 금지)
├── demo/
│   └── screenshot.png       # 실행 화면 캡처
│
├── wiki_core.py             # 공유 I/O 라이브러리
├── RULES.md                 # 에이전트 하네스 운영 지침 ← 항상 먼저 읽기
├── AGENTS.md                # 에이전트 역할·권한 명세
├── SCHEMA.md                # 위키 페이지 구조 규약
├── index.md                 # 전체 페이지 목차
├── journal.md               # 감사 로그 (append-only)
└── requirements.md          # 의존성 목록
```

---

## MCP Tool 목록

`tools/mcp_server.py`가 제공하는 9개 Tool. Claude Desktop / Claude CLI에서 직접 호출 가능합니다.

### 조회 Tool

| Tool | 설명 | 입력 |
|---|---|---|
| `wiki_list_pages` | 모든 위키 페이지 목록 (slug, title, tags) | 없음 |
| `wiki_get_page` | 페이지 전체 내용 조회 | `slug: str` |
| `wiki_search` | 키워드 검색 (관련도 순, 스니펫 포함) | `query: str` |
| `wiki_get_related` | 연관 페이지 목록 | `slug: str` |
| `wiki_get_index` | index.md 전체 내용 | 없음 |
| `wiki_get_journal` | 최근 감사 로그 | `last_n: int` (기본 20) |

### 쓰기 Tool

| Tool | 설명 | 입력 |
|---|---|---|
| `wiki_create_page` | 새 페이지 생성 | `slug, content` |
| `wiki_update_page` | 기존 페이지 수정 (version 자동 +1) | `slug, content` |
| `wiki_append_journal` | 감사 로그 추가 | `message: str` |

### Claude Desktop 연동 방법

`~/Library/Application Support/Claude/claude_desktop_config.json`:

```bash
# 절대경로 확인 방법
cd llm-wiki-agent && pwd
# 예: /Users/yourname/llm-wiki-agent
```

```json
{
  "mcpServers": {
    "wiki": {
      "command": "python3",
      "args": ["/Users/yourname/llm-wiki-agent/tools/mcp_server.py"]
    }
  }
}
```

---

## 에이전트 SKILL 사용법

Claude Code (`claude` CLI)를 실행한 후 슬래시 명령으로 호출합니다.

| 명령 | 동작 |
|---|---|
| `/wiki-ingest` | raw/ 파일 → wiki 페이지 생성 |
| `/wiki-query` | 위키에서 개념 검색 후 답변 |
| `/wiki-update` | 기존 wiki 페이지 업데이트 |

```bash
# Claude Code 실행
claude

# SKILL 호출 예시
> /wiki-ingest
> raw/내문서.md 파일을 위키 페이지로 만들어줘

> /wiki-query
> 마이크로서비스와 모놀리식의 차이점이 뭐야?
```

---

## 자료 투입 → 위키 통합 방법

### 마크다운 파일

```bash
# 1. raw/ 에 파일 복사
cp ~/my-notes.md raw/

# 2. 파이프라인 실행
python3 pipeline/ingest.py "raw/my-notes.md"

# 3. 생성 확인
ls wiki/ | tail -1
```

### PDF 파일

```bash
# poppler 필요: brew install poppler
cp ~/my-paper.pdf raw/

python3 pipeline/ingest.py "raw/my-paper.pdf"
```

### 텍스트 직접 입력

```bash
python3 pipeline/ingest.py --text "학습 내용..." --title "오늘 배운 것"
```

### 드라이런 (파일 저장 없이 미리 보기)

```bash
python3 pipeline/ingest.py "raw/my-doc.md" --dry-run
```

---

## 검증 방법

```bash
# 1. wiki 페이지 생성 확인
ls wiki/
cat wiki/<생성된-파일>.md

# 2. 검색 동작 확인
python3 -c "
import wiki_core as wc
results = wc.search('내가 검색할 키워드')
for r in results:
    print(r['title'], '-', r['snippet'][:60])
"

# 3. MCP 서버 Tool 목록 확인
python3 -c "
from tools.mcp_server import mcp
print('MCP server OK')
"

# 4. 뷰어 실행
streamlit run tools/app.py
# → http://localhost:8501 에서 위키 확인
```

---

## 하네스 구조 설명

이 프로젝트의 에이전트 하네스는 4개 레이어로 구성됩니다:

```
RULES.md          ← 최우선 운영 규칙 (모든 에이전트가 먼저 읽음)
    ↓
AGENTS.md         ← 에이전트 역할·권한 명세 (Ingestion/Query/Maintenance)
    ↓
SCHEMA.md         ← 위키 구조 규약 (프론트매터, 파일명, 태그)
    ↓
.claude/commands/ ← 실행 가능한 SKILL (wiki-ingest, wiki-query, wiki-update)
```

`journal.md`는 모든 에이전트 동작을 append-only로 기록합니다.

---

## Hook 설명

`.claude/settings.json`에 **PostToolUse Hook**이 등록되어 있습니다.

### 동작 방식

`wiki/*.md` 파일이 저장될 때마다 Claude Code가 자동으로 `tools/journal_hook.py`를 실행합니다.

```
에이전트가 wiki/*.md 저장 (Write 도구)
    ↓
PostToolUse Hook 발동
    ↓
tools/journal_hook.py 실행 (stdin으로 파일 경로 수신)
    ↓
journal.md에 자동 append
```

### journal.md 기록 구조

Hook과 에이전트가 역할을 나눠 기록합니다:

```
- [2026-06-15 10:30] [Hook] Auto-logged write: wiki/17-new-topic.md
- [2026-06-15 10:30] Ingested raw/my-doc.pdf → wiki/17-new-topic.md — API 게이트웨이 패턴 요약
```

| 기록 주체 | 내용 | 필수 여부 |
|---|---|---|
| Hook (자동) | 저장 타임스탬프 + 파일명 | 항상 자동 |
| 에이전트 (수동) | 원본 파일명, 변환 이유/요약 | 필수 |

Hook이 "언제 저장됐는지"를 보장하고, 에이전트가 "왜/무엇을 했는지"를 반드시 추가합니다.
두 기록이 합쳐져 나중에 로그만 봐도 전체 히스토리를 파악할 수 있습니다.

### 중복 방지

같은 날 동일 slug에 대한 Hook 기록이 이미 있으면 skip합니다.

### ⚠️ 주의: Hook 적용 범위

Hook은 **`llm-wiki-agent/` 디렉토리 안에서 `claude`를 실행할 때만 동작**합니다.
`.claude/settings.json`은 프로젝트 루트 기준으로 로드되므로, 다른 디렉토리에서 실행하면 Hook이 발동하지 않습니다.

```bash
# ✅ Hook 동작
cd llm-wiki-agent
claude

# ❌ Hook 미동작
cd ~
claude
```

---

## 데모

아래는 시스템 아키텍처 설계 지식 베이스를 이 도구로 서빙한 화면입니다.

<img width="2940" height="1912" alt="screenshot" src="https://github.com/user-attachments/assets/1f7f79cf-f6b3-4c8f-9528-d7a8e7c72527" />


- 좌측: 도메인별 위키 페이지 목록 + 검색
- 중앙: 위키 내용 (태그 뱃지, 메타데이터, Markdown 렌더링)
- 우측: Claude 에이전트 채팅 (현재 페이지 컨텍스트 기반)

---

## 의존성

```
Python 3.10+
streamlit >= 1.40.0
fastmcp >= 0.3.0
Claude CLI (npm i -g @anthropic-ai/claude-code)
poppler (PDF 처리, 선택)
```

전체 상세: [`requirements.md`](requirements.md)

---

## 라이선스

MIT License — 자유롭게 fork해서 자신의 지식 베이스에 활용하세요.
