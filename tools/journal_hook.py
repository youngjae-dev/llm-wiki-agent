#!/usr/bin/env python3
"""
PostToolUse Hook: wiki/*.md 파일이 Write될 때 자동으로 journal.md에 기록한다.
Claude Code가 stdin으로 JSON payload를 전달한다.
"""
import json
import sys
from pathlib import Path
from datetime import datetime

data = json.load(sys.stdin)
file_path = data.get("tool_input", {}).get("file_path", "")
p = Path(file_path)

# wiki/*.md 파일만 처리
if p.parent.name != "wiki" or p.suffix != ".md":
    sys.exit(0)

journal_path = Path(__file__).parent.parent / "journal.md"
timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

# 같은 슬러그가 오늘 이미 기록됐는지 확인 (중복 방지)
today = datetime.now().strftime("%Y-%m-%d")
slug = p.stem
try:
    existing = journal_path.read_text(encoding="utf-8")
    if f"[{today}" in existing and slug in existing:
        sys.exit(0)
except FileNotFoundError:
    pass

with open(journal_path, "a", encoding="utf-8") as f:
    f.write(f"- [{timestamp}] [Hook] Auto-logged write: wiki/{p.name}\n")
