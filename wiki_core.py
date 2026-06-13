"""
wiki_core.py — ArchWiki 핵심 라이브러리
MCP 서버와 Streamlit GUI가 공유하는 위키 파일 I/O 함수들.
"""

from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path

WIKI_ROOT = Path(__file__).parent
WIKI_DIR = WIKI_ROOT / "wiki"
JOURNAL_PATH = WIKI_ROOT / "journal.md"
INDEX_PATH = WIKI_ROOT / "index.md"


# ── 파싱 유틸 ────────────────────────────────────────────────────────────────

def parse_frontmatter(content: str) -> tuple[dict, str]:
    """마크다운 YAML 프론트매터를 파싱하여 (meta_dict, body) 반환."""
    if not content.startswith("---"):
        return {}, content
    end = content.find("---", 3)
    if end == -1:
        return {}, content
    fm_str = content[3:end].strip()
    body = content[end + 3:].strip()
    meta: dict = {}
    for line in fm_str.splitlines():
        if ":" in line:
            key, _, value = line.partition(":")
            meta[key.strip()] = value.strip().strip('"\'')
    return meta, body


def extract_tags(meta: dict) -> list[str]:
    """프론트매터 tags 필드에서 태그 리스트를 추출한다."""
    raw = meta.get("tags", "")
    return [t.strip() for t in re.findall(r"[\w-]+", raw) if t.strip()]


# ── 페이지 조회 ──────────────────────────────────────────────────────────────

def get_all_pages(include_body: bool = False) -> list[dict]:
    """모든 위키 페이지의 메타데이터 목록을 반환한다."""
    pages = []
    for f in sorted(WIKI_DIR.glob("*.md")):
        content = f.read_text(encoding="utf-8")
        meta, body = parse_frontmatter(content)
        page = {
            "slug": f.stem,
            "title": meta.get("title", f.stem),
            "tags": extract_tags(meta),
            "date": meta.get("date", ""),
            "source": meta.get("source", ""),
            "version": meta.get("version", "1"),
        }
        if include_body:
            page["body"] = body
        pages.append(page)
    return pages


def get_page(slug: str) -> dict | None:
    """슬러그(부분 일치 허용)로 페이지를 반환한다. 없으면 None."""
    for f in sorted(WIKI_DIR.glob("*.md")):
        if f.stem == slug or slug in f.stem:
            content = f.read_text(encoding="utf-8")
            meta, body = parse_frontmatter(content)
            return {
                "slug": f.stem,
                "title": meta.get("title", f.stem),
                "tags": extract_tags(meta),
                "date": meta.get("date", ""),
                "source": meta.get("source", ""),
                "version": meta.get("version", "1"),
                "related": meta.get("related", ""),
                "body": body,
                "raw": content,
            }
    return None


def get_related_slugs(slug: str) -> list[str]:
    """페이지의 related 필드에서 슬러그 목록을 추출한다."""
    page = get_page(slug)
    if not page:
        return []
    return re.findall(r"\[\[([^\]|]+)", page["related"])


# ── 검색 ─────────────────────────────────────────────────────────────────────

def search(query: str, top_k: int = 10) -> list[dict]:
    """제목·태그·본문을 검색하여 관련도 순으로 정렬된 결과를 반환한다."""
    if not query.strip():
        return []

    terms = query.lower().split()
    results = []

    for f in sorted(WIKI_DIR.glob("*.md")):
        content = f.read_text(encoding="utf-8")
        meta, body = parse_frontmatter(content)
        content_lower = content.lower()
        title_lower = meta.get("title", "").lower()
        tags_lower = meta.get("tags", "").lower()

        score = 0
        for term in terms:
            score += title_lower.count(term) * 5
            score += tags_lower.count(term) * 3
            score += body.lower().count(term)

        if score > 0:
            # 첫 매칭 스니펫 추출
            snippet = ""
            for term in terms:
                m = re.search(rf".{{0,80}}{re.escape(term)}.{{0,80}}", body, re.IGNORECASE | re.DOTALL)
                if m:
                    snippet = m.group(0).replace("\n", " ").strip()
                    break

            results.append({
                "slug": f.stem,
                "title": meta.get("title", f.stem),
                "tags": extract_tags(meta),
                "score": score,
                "snippet": snippet[:180],
            })

    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:top_k]


# ── 쓰기 ─────────────────────────────────────────────────────────────────────

def create_page(slug: str, content: str) -> dict:
    """새 위키 페이지를 생성한다. 이미 존재하면 오류 반환."""
    target = WIKI_DIR / f"{slug}.md"
    if target.exists():
        return {"ok": False, "error": f"Already exists: {slug}"}
    WIKI_DIR.mkdir(exist_ok=True)
    target.write_text(content, encoding="utf-8")
    append_journal(f"Created `wiki/{slug}.md` via MCP")
    return {"ok": True, "slug": slug}


def update_page(slug: str, content: str) -> dict:
    """기존 위키 페이지를 수정한다. version +1, date 갱신."""
    for f in sorted(WIKI_DIR.glob("*.md")):
        if f.stem == slug or slug in f.stem:
            # version bump
            def bump(m: re.Match) -> str:
                return f"version: {int(m.group(1)) + 1}"
            updated = re.sub(r"version:\s*(\d+)", bump, content)
            # date 갱신
            today = datetime.today().strftime("%Y-%m-%d")
            updated = re.sub(r"date:\s*\S+", f"date: {today}", updated)
            f.write_text(updated, encoding="utf-8")
            append_journal(f"Updated `wiki/{f.stem}.md` via MCP")
            return {"ok": True, "slug": f.stem}
    return {"ok": False, "error": f"Page not found: {slug}"}


def append_journal(message: str) -> None:
    """journal.md에 타임스탬프와 함께 한 줄을 추가한다."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    entry = f"- [{now}] {message}\n"
    with open(JOURNAL_PATH, "a", encoding="utf-8") as f:
        f.write(entry)


def get_journal(last_n: int = 20) -> str:
    """journal.md의 마지막 n줄을 반환한다."""
    if not JOURNAL_PATH.exists():
        return ""
    lines = JOURNAL_PATH.read_text(encoding="utf-8").splitlines()
    return "\n".join(lines[-last_n:])


def get_index() -> str:
    """index.md 전체 내용을 반환한다."""
    if INDEX_PATH.exists():
        return INDEX_PATH.read_text(encoding="utf-8")
    return "index.md not found"
