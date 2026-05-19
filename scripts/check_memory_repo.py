#!/usr/bin/env python3
"""Basic checks for the AI workbench memory repository."""

from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ALLOWED_STATUS = {
    "draft",
    "proposed",
    "current",
    "recommended",
    "deprecated",
    "rejected",
    "conflict",
}
REQUIRED_KEYS = {"id", "type", "status", "owner", "scope", "sensitivity", "last_reviewed", "source"}
SECRET_ASSIGNMENT = re.compile(
    r"(?i)\b(password|passwd|token|api[_-]?key|secret)\b\s*[:=]\s*['\"]?([A-Za-z0-9_\-./+=]{8,})"
)
FRONTMATTER = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)


def iter_markdown_files(include_github: bool = False) -> list[Path]:
    return sorted(
        path
        for path in ROOT.rglob("*.md")
        if ".git" not in path.parts and "__pycache__" not in path.parts
        and (include_github or ".github" not in path.parts)
    )


def parse_frontmatter(text: str) -> dict[str, str] | None:
    match = FRONTMATTER.match(text)
    if not match:
        return None
    data: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip()
    return data


def check_frontmatter(files: list[Path]) -> list[str]:
    errors: list[str] = []
    ids: dict[str, Path] = {}
    for path in files:
        rel = path.relative_to(ROOT)
        text = path.read_text(encoding="utf-8")
        data = parse_frontmatter(text)
        if data is None:
            errors.append(f"{rel}: missing YAML frontmatter")
            continue
        missing = sorted(REQUIRED_KEYS - set(data))
        if missing:
            errors.append(f"{rel}: missing frontmatter keys: {', '.join(missing)}")
        status = data.get("status")
        if status and status not in ALLOWED_STATUS:
            errors.append(f"{rel}: unsupported status '{status}'")
        doc_id = data.get("id")
        if not doc_id:
            continue
        if doc_id in ids:
            errors.append(f"{rel}: duplicate id '{doc_id}' also used by {ids[doc_id].relative_to(ROOT)}")
        else:
            ids[doc_id] = path
    return errors


def check_sensitive_values(files: list[Path]) -> list[str]:
    errors: list[str] = []
    for path in files:
        rel = path.relative_to(ROOT)
        text = path.read_text(encoding="utf-8")
        for index, line in enumerate(text.splitlines(), start=1):
            if "secret://" in line:
                continue
            match = SECRET_ASSIGNMENT.search(line)
            if match:
                errors.append(f"{rel}:{index}: possible sensitive value assigned to {match.group(1)}")
    return errors


def check_page_badges() -> list[str]:
    errors: list[str] = []
    registry = ROOT / "04_资源登记" / "页面角标编号.md"
    if not registry.exists():
        return [f"{registry.relative_to(ROOT)}: missing page badge registry"]
    seen: dict[int, str] = {}
    for line in registry.read_text(encoding="utf-8").splitlines():
        match = re.match(r"\|\s*(\d+)\s*\|", line)
        if not match:
            continue
        number = int(match.group(1))
        if number in seen:
            errors.append(f"{registry.relative_to(ROOT)}: duplicate page badge {number}")
        seen[number] = line
    return errors


def main() -> int:
    files = iter_markdown_files()
    all_markdown_files = iter_markdown_files(include_github=True)
    errors: list[str] = []
    errors.extend(check_frontmatter(files))
    errors.extend(check_sensitive_values(all_markdown_files))
    errors.extend(check_page_badges())

    if errors:
        print("CHECK_FAIL")
        for error in errors:
            print(f"- {error}")
        return 1

    print("CHECK_PASS")
    print(f"markdown_files={len(files)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
