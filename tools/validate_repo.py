#!/usr/bin/env python3
"""Lightweight repository validator for mq5_skills."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_PATHS = [
    "mql5-ea-expert/SKILL.md",
    "mql5-ea-expert/references/ea-blueprint.md",
    "mql5-ea-expert/references/example-prompts.md",
    "README.md", "CHANGELOG.md", "CONTRIBUTING.md", "LICENSE", "evals.json",
    "docs/AI_SETUP_GUIDE.md", "docs/ROADMAP.md",
    "tools/validate_repo.py",
]

def fail(message: str) -> None:
    print(f"FAIL: {message}")
    raise SystemExit(1)

def check_required_paths() -> None:
    missing = [path for path in REQUIRED_PATHS if not (ROOT / path).exists()]
    if missing:
        fail("Missing required paths: " + ", ".join(missing))

def check_skill_frontmatter() -> None:
    text = (ROOT / "mql5-ea-expert/SKILL.md").read_text(encoding="utf-8")
    if not text.startswith("---\n") or text.find("\n---", 4) == -1:
        fail("SKILL.md frontmatter invalid")
    frontmatter = text[4:text.find("\n---", 4)]
    for key in ["name:", "version:", "description:", "license:", "tags:"]:
        if key not in frontmatter:
            fail(f"SKILL.md frontmatter missing {key}")

def check_evals_json() -> None:
    data = json.loads((ROOT / "evals.json").read_text(encoding="utf-8"))
    evals = data.get("evals")
    if not isinstance(evals, list) or not evals:
        fail("evals.json must contain non-empty evals list")
    ids = [item.get("id") for item in evals]
    if len(ids) != len(set(ids)):
        fail("evals.json contains duplicate ids")

def check_readme_links() -> None:
    text = (ROOT / "README.md").read_text(encoding="utf-8")
    for link in re.findall(r"\[[^\]]+\]\(([^)]+)\)", text):
        if link.startswith(("http://", "https://", "../../", "#")):
            continue
        if not (ROOT / link.split("#", 1)[0]).exists():
            fail(f"README link target missing: {link}")

def main() -> int:
    check_required_paths(); check_skill_frontmatter(); check_evals_json(); check_readme_links()
    print("OK: repository structure valid")
    return 0

if __name__ == "__main__":
    sys.exit(main())
