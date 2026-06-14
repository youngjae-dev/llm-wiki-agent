#!/usr/bin/env python3
"""
LLM Wiki Ingestion Pipeline
raw/ 디렉토리의 파일(PDF, 텍스트)을 받아 wiki/ 페이지로 변환한다.
Claude CLI subprocess를 사용하여 LLM이 위키 페이지를 생성한다.

사용법:
  python pipeline/ingest.py "raw/7. Harness and Skills.pdf"
  python pipeline/ingest.py --all
  python pipeline/ingest.py --text "인라인 원본 텍스트" --title "페이지 제목"
"""

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# 경로 설정
WIKI_ROOT = Path(__file__).parent.parent
WIKI_DIR = WIKI_ROOT / "wiki"
RAW_DIR = WIKI_ROOT / "raw"
SCHEMA_PATH = WIKI_ROOT / "SCHEMA.md"
INDEX_PATH = WIKI_ROOT / "index.md"
JOURNAL_PATH = WIKI_ROOT / "journal.md"
WORKSPACE_DIR = Path(__file__).parent / "workspace"


def extract_text_from_pdf(pdf_path: str) -> str:
    """pdftotext를 사용하여 PDF에서 텍스트를 추출한다."""
    result = subprocess.run(
        ["pdftotext", pdf_path, "-"],
        capture_output=True,
        text=True,
        timeout=30,
    )
    if result.returncode != 0:
        raise RuntimeError(f"pdftotext 실패: {result.stderr}")
    return result.stdout


def read_file_content(file_path: str) -> str:
    """파일 확장자에 따라 내용을 읽는다."""
    p = Path(file_path)
    if not p.exists():
        raise FileNotFoundError(f"파일 없음: {file_path}")

    ext = p.suffix.lower()
    if ext == ".pdf":
        return extract_text_from_pdf(file_path)
    elif ext in (".txt", ".md"):
        return p.read_text(encoding="utf-8")
    else:
        raise ValueError(f"지원하지 않는 파일 형식: {ext}")


def get_next_slug_number() -> int:
    """wiki/ 디렉토리에서 현재 최대 순번을 구하고 +1을 반환한다."""
    existing = list(WIKI_DIR.glob("[0-9][0-9]-*.md"))
    if not existing:
        return 1
    nums = [int(f.name[:2]) for f in existing if f.name[:2].isdigit()]
    return max(nums) + 1 if nums else 1


def slugify(name: str) -> str:
    """문자열을 kebab-case 슬러그로 변환한다."""
    name = re.sub(r"[^\w\s-]", "", name.lower())
    name = re.sub(r"[\s_]+", "-", name)
    return name.strip("-")


def call_claude(prompt: str, timeout: int = 240) -> str:
    """Claude CLI subprocess를 호출하고 결과 텍스트를 반환한다."""
    result = subprocess.run(
        ["claude", "-p", "--output-format", "json", "--no-session-persistence"],
        input=prompt,
        capture_output=True,
        encoding="utf-8",
        timeout=timeout,
    )
    if result.returncode != 0:
        raise RuntimeError(f"Claude CLI 실패 (returncode={result.returncode}): {result.stderr[:500]}")

    try:
        response = json.loads(result.stdout)
        text = response.get("result", "")
    except json.JSONDecodeError:
        text = result.stdout

    # Claude가 마크다운 출력을 코드펜스로 감싸는 경우 제거
    text = text.strip()
    if text.startswith("```markdown"):
        text = text[len("```markdown"):].lstrip("\n")
    elif text.startswith("```"):
        text = text[3:].lstrip("\n")
    if text.endswith("```"):
        text = text[:-3].rstrip("\n")
    return text


def generate_wiki_page(raw_content: str, source_name: str, schema: str, slug: str) -> str:
    """Claude를 사용하여 원본 내용으로부터 위키 페이지를 생성한다."""
    today = datetime.today().strftime("%Y-%m-%d")
    next_num = get_next_slug_number()
    full_slug = f"{next_num:02d}-{slug}"

    prompt = f"""당신은 LLM Wiki 페이지 생성 에이전트입니다.

다음은 이 위키의 SCHEMA(구조 규칙)입니다:
<schema>
{schema}
</schema>

다음 원본 내용(source: {source_name})을 기반으로 위키 페이지를 생성하세요:
<raw_content>
{raw_content[:8000]}
</raw_content>

요구사항:
1. SCHEMA의 프론트매터 형식을 정확히 따를 것
   - title: 적절한 한국어/영어 제목
   - tags: SCHEMA의 태그 분류표에서 적합한 태그 선택
   - source: "raw/{source_name}"
   - date: {today}
   - related: 관련 페이지 슬러그 목록 (예: ["[[01-vibe-coding-and-agentic-coding]]"])
   - version: 1
2. 본문 구조: Overview → Key Concepts → Details → Examples/Code → Related
3. 한국어 원본은 한국어로, 영어는 영어로 작성
4. 최소 1개 이상의 내부 링크 [[slug]] 포함
5. 코드 블록에 언어 명시 (python, bash, json 등)
6. Related 섹션에 최소 1개 항목

슬러그 후보: {full_slug}

출력: 마크다운 파일 내용만 출력하세요. 추가 설명 없이.
중요: 어떠한 도구(Write, Edit 등)도 사용하지 마세요. 텍스트만 출력하세요."""

    return call_claude(prompt)


def update_index(slug: str, title: str, tags: list[str], summary: str) -> None:
    """index.md의 위키 페이지 목록에 새 항목을 추가한다."""
    if not INDEX_PATH.exists():
        return

    index_content = INDEX_PATH.read_text(encoding="utf-8")
    tag_str = " ".join(f"`{t}`" for t in tags[:3])

    new_row = f"| [[{slug}\\|{title}]] | {tag_str} | {summary} |"

    # 테이블 끝 다음에 삽입
    lines = index_content.splitlines()
    insert_pos = None
    in_table = False
    for i, line in enumerate(lines):
        if "| 페이지 |" in line or "| Page |" in line:
            in_table = True
        if in_table and line.startswith("|") and i + 1 < len(lines) and not lines[i + 1].startswith("|"):
            insert_pos = i + 1
            break

    if insert_pos is not None:
        lines.insert(insert_pos, new_row)
        INDEX_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def append_journal(message: str) -> None:
    """journal.md에 한 줄을 append한다."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    entry = f"- [{now}] {message}\n"
    with open(JOURNAL_PATH, "a", encoding="utf-8") as f:
        f.write(entry)


def extract_frontmatter_field(content: str, field: str) -> str:
    """마크다운 프론트매터에서 특정 필드 값을 추출한다."""
    pattern = rf'^{field}:\s*["\']?(.+?)["\']?\s*$'
    match = re.search(pattern, content, re.MULTILINE)
    return match.group(1).strip() if match else ""


def save_workspace_artifact(stage: str, content: str) -> None:
    """파이프라인 핸드오프 파일을 workspace/에 저장한다."""
    WORKSPACE_DIR.mkdir(exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    artifact_path = WORKSPACE_DIR / f"{stage}_{ts}.md"
    artifact_path.write_text(content, encoding="utf-8")
    print(f"  [workspace] {artifact_path.name}")


def ingest(source: str, title_override: str | None = None) -> Path:
    """
    단일 파일을 수집하여 위키 페이지를 생성한다.

    Args:
        source: PDF 또는 텍스트 파일 경로
        title_override: 제목 직접 지정 (없으면 파일명에서 유추)

    Returns:
        생성된 wiki 페이지 경로
    """
    source_path = Path(source)
    source_name = source_path.name
    print(f"\n[ingest] 처리 중: {source_name}")

    # 1. 원본 추출
    print("  [1/4] 원본 텍스트 추출...")
    raw_content = read_file_content(str(source_path))
    save_workspace_artifact("00_raw_extract", f"# Raw: {source_name}\n\n{raw_content[:3000]}")
    print(f"  → {len(raw_content)} 문자 추출됨")

    # 2. 슬러그 결정
    base_name = title_override or source_path.stem
    # 파일명 앞의 숫자와 점 제거 (예: "7. Harness and Skills" → "Harness and Skills")
    base_name = re.sub(r"^\d+[\.\s]+", "", base_name).strip()
    slug = slugify(base_name)
    next_num = get_next_slug_number()
    full_slug = f"{next_num:02d}-{slug}"

    output_path = WIKI_DIR / f"{full_slug}.md"
    if output_path.exists():
        print(f"  [경고] 이미 존재함: {output_path.name} — 덮어쓰기")

    # 3. 위키 페이지 생성 (Claude CLI)
    print("  [2/4] Claude로 위키 페이지 생성 중...")
    schema = SCHEMA_PATH.read_text(encoding="utf-8")
    wiki_content = generate_wiki_page(raw_content, source_name, schema, slug)
    save_workspace_artifact("01_wiki_draft", wiki_content)

    # 4. 파일 저장
    print("  [3/4] wiki/ 에 저장 중...")
    WIKI_DIR.mkdir(exist_ok=True)
    output_path.write_text(wiki_content, encoding="utf-8")

    # 5. 메타데이터 추출 후 index/journal 갱신
    print("  [4/4] index.md / journal.md 갱신 중...")
    page_title = extract_frontmatter_field(wiki_content, "title") or base_name
    raw_tags = extract_frontmatter_field(wiki_content, "tags")
    tags = re.findall(r"[\w-]+", raw_tags)
    summary = ""
    # Overview 첫 문장 추출
    ov_match = re.search(r"## Overview\n+(.+)", wiki_content)
    if ov_match:
        summary = ov_match.group(1).strip()[:80]

    update_index(full_slug, page_title, tags, summary)
    append_journal(f"Ingested `{source_name}` → `wiki/{full_slug}.md`")

    print(f"\n  완료: {output_path}")
    return output_path


def ingest_all() -> list[Path]:
    """raw/ 디렉토리의 모든 파일 중 아직 위키 페이지가 없는 것을 처리한다."""
    processed = []
    raw_files = sorted(RAW_DIR.iterdir())

    for raw_file in raw_files:
        if raw_file.suffix.lower() not in (".pdf", ".txt", ".md"):
            continue
        if raw_file.name.startswith("."):
            continue

        # 이미 처리됐는지 journal에서 확인
        journal_content = JOURNAL_PATH.read_text(encoding="utf-8") if JOURNAL_PATH.exists() else ""
        if raw_file.name in journal_content:
            print(f"[skip] 이미 처리됨: {raw_file.name}")
            continue

        try:
            output = ingest(str(raw_file))
            processed.append(output)
        except Exception as e:
            print(f"[error] {raw_file.name}: {e}")
            append_journal(f"FAILED ingesting `{raw_file.name}` — {e}")

    return processed


def ingest_text(text: str, title: str) -> Path:
    """인라인 텍스트를 위키 페이지로 변환한다."""
    # 임시 파일 생성
    tmp_path = WORKSPACE_DIR / "inline_input.txt"
    WORKSPACE_DIR.mkdir(exist_ok=True)
    tmp_path.write_text(text, encoding="utf-8")
    return ingest(str(tmp_path), title_override=title)


def main():
    parser = argparse.ArgumentParser(
        description="LLM Wiki Ingestion Pipeline — raw 파일을 wiki 페이지로 변환"
    )
    parser.add_argument("source", nargs="?", help="원본 파일 경로 (PDF, TXT, MD)")
    parser.add_argument("--all", action="store_true", help="raw/ 디렉토리 전체 처리 (미처리 파일만)")
    parser.add_argument("--text", help="인라인 텍스트 입력")
    parser.add_argument("--title", help="제목 지정 (--text와 함께 사용)")
    parser.add_argument("--dry-run", action="store_true", help="실제 저장 없이 미리보기만")

    args = parser.parse_args()

    if args.dry_run:
        print("[dry-run 모드] 실제 파일을 저장하지 않습니다.")

    if args.all:
        results = ingest_all()
        print(f"\n완료: {len(results)}개 페이지 생성됨")
        for r in results:
            print(f"  - {r}")

    elif args.text:
        if not args.title:
            print("오류: --text 사용 시 --title 필수")
            sys.exit(1)
        result = ingest_text(args.text, args.title)
        print(f"\n생성됨: {result}")

    elif args.source:
        result = ingest(args.source)
        print(f"\n생성됨: {result}")

    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
