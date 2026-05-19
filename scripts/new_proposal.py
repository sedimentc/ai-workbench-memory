#!/usr/bin/env python3
"""Create a standard review proposal markdown file."""

from __future__ import annotations

import argparse
import re
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROPOSAL_DIRS = {
    "memory": ROOT / "05_待审核" / "记忆提案",
    "skill": ROOT / "05_待审核" / "Skill提案",
    "resource": ROOT / "05_待审核" / "资源变更提案",
}
ID_PREFIXES = {
    "memory": "PROPOSAL-MEMORY",
    "skill": "PROPOSAL-SKILL",
    "resource": "PROPOSAL-RESOURCE",
}


def safe_slug(text: str) -> str:
    slug = re.sub(r"[^0-9A-Za-z\u4e00-\u9fff]+", "-", text.strip()).strip("-")
    return slug or "untitled"


def next_id(kind: str, date: str) -> str:
    directory = PROPOSAL_DIRS[kind]
    prefix = f"{ID_PREFIXES[kind]}-{date}-"
    max_seen = 0
    for path in directory.glob("*.md"):
        text = path.read_text(encoding="utf-8", errors="ignore")
        match = re.search(rf"^id:\s*{re.escape(prefix)}(\d+)\s*$", text, re.MULTILINE)
        if match:
            max_seen = max(max_seen, int(match.group(1)))
    return f"{prefix}{max_seen + 1:03d}"


def proposal_body(args: argparse.Namespace, proposal_id: str) -> str:
    today = datetime.now().astimezone().strftime("%Y-%m-%d")
    return f"""---
id: {proposal_id}
type: proposal
status: proposed
owner: {args.owner}
reviewer: {args.reviewer}
scope: {args.scope}
sensitivity: internal
last_reviewed: {today}
source: {args.source}
---

# {args.title}

## 问题是什么

待补充。

## 适用场景

待补充。

## 不适用场景

待补充。

## 具体内容

待补充。

## 测试案例

待补充。

## 风险

待补充。

## 建议合并位置

待补充。

## 审核结论

待审核
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a review proposal")
    parser.add_argument("title", help="Proposal title")
    parser.add_argument("--type", choices=sorted(PROPOSAL_DIRS), default="memory")
    parser.add_argument("--owner", default="陈纪言")
    parser.add_argument("--reviewer", default="待确认")
    parser.add_argument("--scope", default="AI工作台")
    parser.add_argument("--source", default="人工提交")
    args = parser.parse_args()

    date = datetime.now().astimezone().strftime("%Y%m%d")
    proposal_id = next_id(args.type, date)
    directory = PROPOSAL_DIRS[args.type]
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{date}-{safe_slug(args.title)}.md"
    if path.exists():
        raise SystemExit(f"File already exists: {path}")
    path.write_text(proposal_body(args, proposal_id), encoding="utf-8")
    print(path.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

