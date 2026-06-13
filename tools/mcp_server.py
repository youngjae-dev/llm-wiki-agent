"""
tools/mcp_server.py — ArchWiki MCP 서버 (FastMCP)
wiki_core.py 함수들을 MCP Tool로 노출한다.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

# repo root를 sys.path에 추가 (wiki_core.py 위치)
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastmcp import FastMCP
import wiki_core as wc

mcp = FastMCP(
    name="ArchWiki",
    instructions=(
        "You are ArchWiki Agent — an expert in system architecture design for personal projects. "
        "Use the provided tools to read wiki pages, search knowledge, create/update pages, "
        "and append to the journal. Always cite page slugs when answering."
    ),
)


# ── 조회 ─────────────────────────────────────────────────────────────────────

@mcp.tool()
def wiki_list_pages() -> str:
    """모든 위키 페이지의 slug, title, tags 목록을 반환한다."""
    pages = wc.get_all_pages()
    return json.dumps(pages, ensure_ascii=False, indent=2)


@mcp.tool()
def wiki_get_page(slug: str) -> str:
    """slug로 위키 페이지 전체 내용(프론트매터 + 본문)을 반환한다.
    slug는 부분 일치를 허용한다. 예: '12' 또는 '12-architecture-patterns'.
    """
    page = wc.get_page(slug)
    if page is None:
        return json.dumps({"error": f"Page not found: {slug}"}, ensure_ascii=False)
    return json.dumps(page, ensure_ascii=False, indent=2)


@mcp.tool()
def wiki_search(query: str) -> str:
    """제목·태그·본문을 대상으로 키워드 검색한다.
    관련도 순 결과(최대 10개)와 스니펫을 반환한다.
    """
    results = wc.search(query)
    return json.dumps(results, ensure_ascii=False, indent=2)


@mcp.tool()
def wiki_get_related(slug: str) -> str:
    """페이지의 related 필드에 연결된 페이지들의 메타데이터를 반환한다."""
    related_slugs = wc.get_related_slugs(slug)
    pages = []
    for s in related_slugs:
        p = wc.get_page(s.strip())
        if p:
            pages.append({k: v for k, v in p.items() if k != "raw"})
    return json.dumps(pages, ensure_ascii=False, indent=2)


@mcp.tool()
def wiki_get_index() -> str:
    """index.md 전체 내용을 반환한다 (전체 페이지 목차)."""
    return wc.get_index()


# ── 쓰기 ─────────────────────────────────────────────────────────────────────

@mcp.tool()
def wiki_create_page(slug: str, content: str) -> str:
    """새 위키 페이지를 생성한다.
    slug: 파일명 (확장자 없이). 예: '17-new-topic'
    content: YAML 프론트매터 포함 전체 마크다운.
    이미 존재하는 slug이면 오류를 반환한다.
    """
    result = wc.create_page(slug, content)
    return json.dumps(result, ensure_ascii=False)


@mcp.tool()
def wiki_update_page(slug: str, content: str) -> str:
    """기존 위키 페이지를 수정한다.
    version 번호를 자동으로 +1하고 date를 오늘로 갱신한다.
    slug: 부분 일치 허용.
    content: YAML 프론트매터 포함 전체 마크다운.
    """
    result = wc.update_page(slug, content)
    return json.dumps(result, ensure_ascii=False)


@mcp.tool()
def wiki_append_journal(message: str) -> str:
    """journal.md에 새 항목을 추가한다.
    현재 타임스탬프가 자동으로 붙는다.
    message: 기록할 내용 (예: 'Reviewed microservices patterns for project X').
    """
    wc.append_journal(message)
    return json.dumps({"ok": True, "message": message}, ensure_ascii=False)


@mcp.tool()
def wiki_get_journal(last_n: int = 20) -> str:
    """journal.md의 최근 N개 항목을 반환한다 (기본 20개)."""
    return wc.get_journal(last_n)


if __name__ == "__main__":
    mcp.run()
