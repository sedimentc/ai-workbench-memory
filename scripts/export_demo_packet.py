#!/usr/bin/env python3
"""Export a single Markdown packet for live demos."""

from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "dist"
OUT_FILE = OUT_DIR / "演示包.md"

DEMO_FILES = [
    "演示入口.md",
    "README.md",
    "AI入口.md",
    "总览.md",
    "01_项目/AI工作台/StartPack.md",
    "01_项目/AI工作台/当前状态.md",
    "01_项目/AI工作台/历史证据.md",
    "05_待审核/记忆提案/20260519-新窗口必须先读StartPack.md",
    "04_资源登记/页面角标编号.md",
    "04_资源登记/服务器候选.md",
    "10_启动材料/功能对照表.md",
    "10_启动材料/二期中心服务路线图.md",
    "10_启动材料/逐分钟演示讲稿.md",
    "10_启动材料/现场答辩问答.md",
    "10_启动材料/新窗口演示提示词.md",
]

FRONTMATTER = re.compile(r"\A---\n.*?\n---\n", re.DOTALL)


def strip_frontmatter(text: str) -> str:
    return FRONTMATTER.sub("", text, count=1).strip()


def main() -> int:
    OUT_DIR.mkdir(exist_ok=True)
    now = datetime.now().astimezone().isoformat(timespec="seconds")
    parts = [
        "# AI 工作台共享 MD 系统演示包",
        "",
        f"生成时间：{now}",
        "",
        "本文件由 `scripts/export_demo_packet.py` 自动生成，方便会议演示时打开单份 Markdown。",
        "",
        "## 目录",
        "",
    ]
    for index, rel in enumerate(DEMO_FILES, start=1):
        parts.append(f"{index}. `{rel}`")
    parts.append("")

    for rel in DEMO_FILES:
        path = ROOT / rel
        if not path.exists():
            raise SystemExit(f"Missing demo source file: {rel}")
        body = strip_frontmatter(path.read_text(encoding="utf-8"))
        parts.extend(
            [
                "---",
                "",
                f"## 来源文件：`{rel}`",
                "",
                body,
                "",
            ]
        )

    OUT_FILE.write_text("\n".join(parts).rstrip() + "\n", encoding="utf-8")
    print(OUT_FILE.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

