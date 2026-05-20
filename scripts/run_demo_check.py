#!/usr/bin/env python3
"""Check whether the memory repo is ready for a live demo."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    "README.md",
    "演示入口.md",
    "运行演示.html",
    "AI入口.md",
    "总览.md",
    "00_规则/阶段边界.md",
    "00_规则/敏感信息规则.md",
    "01_项目/AI工作台/StartPack.md",
    "01_项目/AI工作台/当前状态.md",
    "01_项目/AI工作台/历史证据.md",
    "02_技能库/README.md",
    "04_资源登记/页面角标编号.md",
    "07_实战索引/README.md",
    "07_实战索引/别名词典.md",
    "07_实战索引/页面索引.md",
    "07_实战索引/技能索引.md",
    "07_实战索引/项目索引.md",
    "07_实战索引/窗口索引.md",
    "07_实战索引/字段契约索引.md",
    "07_实战索引/连接信息索引.md",
    "08_导入资料/README.md",
    "05_待审核/记忆提案/20260519-新窗口必须先读StartPack.md",
    "10_启动材料/功能对照表.md",
    "10_启动材料/当前系统状态.md",
    "10_启动材料/二期中心服务路线图.md",
    "10_启动材料/逐分钟演示讲稿.md",
    "10_启动材料/新窗口演示提示词.md",
    "10_启动材料/现场答辩问答.md",
    "10_启动材料/新窗口接手实测记录.md",
    "dist/index.html",
    "dist/演示包.md",
    "scripts/check_memory_repo.py",
    "scripts/new_proposal.py",
    "scripts/export_demo_packet.py",
    "scripts/demo_server.py",
]


def run(command: list[str]) -> tuple[int, str]:
    proc = subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    return proc.returncode, proc.stdout.strip()


def main() -> int:
    errors: list[str] = []

    for rel in REQUIRED_FILES:
        if not (ROOT / rel).exists():
            errors.append(f"missing required demo file: {rel}")

    code, output = run(["python3", "scripts/check_memory_repo.py"])
    if code != 0:
        errors.append("check_memory_repo.py failed")
        errors.append(output)

    code, output = run(["git", "status", "--short"])
    if code != 0:
        errors.append("git status failed")
        errors.append(output)
    elif output:
        errors.append("git working tree is not clean")
        errors.append(output)

    code, output = run(["git", "log", "--oneline", "-1"])
    if code != 0:
        errors.append("git log failed")
        errors.append(output)

    if errors:
        print("DEMO_NOT_READY")
        for error in errors:
            print(f"- {error}")
        return 1

    print("DEMO_READY")
    print(f"repo={ROOT}")
    print(f"latest_commit={output}")
    print("start_here=dist/index.html")
    return 0


if __name__ == "__main__":
    sys.exit(main())
