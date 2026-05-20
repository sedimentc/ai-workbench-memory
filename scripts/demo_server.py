#!/usr/bin/env python3
"""Local interactive demo server for the AI workbench memory repo."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse


ROOT = Path(__file__).resolve().parents[1]
RUNTIME_DIR = ROOT / ".demo_runtime" / "proposals"
FRONTMATTER = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)


def read_text(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


def strip_frontmatter(text: str) -> str:
    return FRONTMATTER.sub("", text, count=1).strip()


def run(command: list[str]) -> dict[str, object]:
    proc = subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    return {"code": proc.returncode, "output": proc.stdout.strip()}


def markdown_files_count() -> int:
    return sum(
        1
        for path in ROOT.rglob("*.md")
        if ".git" not in path.parts
        and ".github" not in path.parts
        and ".demo_runtime" not in path.parts
        and "dist" not in path.parts
        and "__pycache__" not in path.parts
    )


def parse_table(rel: str) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    headers: list[str] | None = None
    for raw in read_text(rel).splitlines():
        line = raw.strip()
        if not line.startswith("|"):
            continue
        cells = [cell.strip().strip("`") for cell in line.strip("|").split("|")]
        if all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells):
            continue
        if headers is None:
            headers = cells
            continue
        if len(cells) != len(headers):
            continue
        rows.append(dict(zip(headers, cells)))
    return rows


def extract_section(text: str, heading: str, max_chars: int = 700) -> str:
    pattern = re.compile(rf"^##\s+{re.escape(heading)}\s*$([\s\S]*?)(?=^##\s+|\Z)", re.MULTILINE)
    match = pattern.search(strip_frontmatter(text))
    if not match:
        return ""
    content = match.group(1).strip()
    return content[:max_chars].rstrip()


def status_payload() -> dict[str, object]:
    check = run(["python3", "scripts/check_memory_repo.py"])
    git = run(["git", "log", "--oneline", "-1"])
    remote = run(["git", "remote", "-v"])
    clean = run(["git", "status", "--short"])
    return {
        "repo": str(ROOT),
        "check": check,
        "gitLatest": git["output"],
        "gitRemote": remote["output"],
        "workingTreeClean": clean["output"] == "",
        "markdownFiles": markdown_files_count(),
        "modules": [
            {"name": "00_规则", "purpose": "读取、安全、Git、审核、生命周期"},
            {"name": "01_项目", "purpose": "StartPack、当前状态、接手说明"},
            {"name": "03_工作流", "purpose": "接手、会议沉淀、测试 Agent、资源申请"},
            {"name": "04_资源登记", "purpose": "页面编号、端口、电脑、secret 引用"},
            {"name": "05_待审核", "purpose": "记忆、Skill、资源变更先提案后合并"},
            {"name": "07_实战索引", "purpose": "刘大式口语映射和快速定位"},
        ],
    }


def resolve_payload(query: str) -> dict[str, object]:
    query = query.strip() or "页面22"
    aliases = parse_table("07_实战索引/别名词典.md")
    pages = parse_table("07_实战索引/页面索引.md")
    skills = parse_table("07_实战索引/技能索引.md")
    alias = next(
        (
            row
            for row in aliases
            if query in row.get("平时说法", "")
            or query == row.get("标准编号", "")
            or query == row.get("标准对象", "")
        ),
        None,
    )
    standard = alias.get("标准编号", query) if alias else query
    page = next((row for row in pages if row.get("页面编号") == standard), None)
    skill = next((row for row in skills if row.get("技能ID") == standard or row.get("简化名") == query), None)
    return {
        "query": query,
        "alias": alias,
        "standard": standard,
        "page": page,
        "skill": skill,
        "route": [
            "用户口语",
            "07_实战索引/别名词典.md",
            "PAGE编号 / SKILL编号",
            "07_实战索引/页面索引.md 或 技能索引.md",
            "项目 StartPack / 当前状态 / 具体文档",
        ],
    }


def start_pack_payload() -> dict[str, object]:
    start_pack = read_text("01_项目/AI工作台/StartPack.md")
    current = read_text("01_项目/AI工作台/当前状态.md")
    return {
        "filesRead": [
            "AI入口.md",
            "总览.md",
            "01_项目/AI工作台/StartPack.md",
            "01_项目/AI工作台/当前状态.md",
        ],
        "goal": extract_section(start_pack, "当前目标"),
        "state": extract_section(start_pack, "当前状态"),
        "confirmedRules": extract_section(start_pack, "已确认规则"),
        "currentFacts": strip_frontmatter(current)[:1200].rstrip(),
    }


def proposal_payload(body: bytes) -> dict[str, object]:
    data = json.loads(body.decode("utf-8") or "{}")
    title = str(data.get("title") or "演示提案-页面22接手规则").strip()
    detail = str(data.get("detail") or "用户说页面22时，AI 应先查别名词典和页面索引，再读项目 StartPack。").strip()
    now = datetime.now().astimezone()
    proposal_id = now.strftime("DEMO-PROPOSAL-%Y%m%d-%H%M%S")
    RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
    path = RUNTIME_DIR / f"{proposal_id}.md"
    content = f"""---
id: {proposal_id}
type: proposal
status: proposed
owner: 陈纪言
reviewer: 演示中待确认
scope: AI工作台
sensitivity: internal
last_reviewed: {now.strftime("%Y-%m-%d")}
source: 运行演示页面
---

# {title}

## 问题是什么

演示如何把口语任务进入待审核沉淀，而不是直接污染正式规则。

## 具体内容

{detail}

## 建议合并位置

`07_实战索引/别名词典.md` 或对应项目 `StartPack.md`

## 审核结论

待审核
"""
    path.write_text(content, encoding="utf-8")
    return {"path": str(path), "content": content}


def secret_policy_payload() -> dict[str, object]:
    return {
        "ruleFile": "00_规则/敏感信息规则.md",
        "restrictedFile": "07_实战索引/连接信息索引.md",
        "allowedWhen": [
            "用户明确要求或刘大/老王确认需要记录",
            "文档头部为 sensitivity: restricted",
            "文档头部有 credential_allowed: true",
            "凭据行写明用途、负责人、风险级别和轮换规则",
            "GitHub 仓库是核心成员受限访问",
        ],
        "demoExport": "演示包会自动脱敏受限凭据文档正文。",
    }


class DemoHandler(BaseHTTPRequestHandler):
    server_version = "AIWorkbenchMemoryDemo/1.0"

    def log_message(self, format: str, *args: object) -> None:
        return

    def send_json(self, payload: object, status: int = 200) -> None:
        data = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def send_file(self, rel: str) -> None:
        path = (ROOT / rel).resolve()
        if ROOT not in path.parents and path != ROOT:
            self.send_error(403)
            return
        if not path.exists() or not path.is_file():
            self.send_error(404)
            return
        data = path.read_bytes()
        content_type = "text/plain; charset=utf-8"
        if path.suffix == ".html":
            content_type = "text/html; charset=utf-8"
        elif path.suffix == ".css":
            content_type = "text/css; charset=utf-8"
        elif path.suffix == ".js":
            content_type = "application/javascript; charset=utf-8"
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        path = unquote(parsed.path)
        if path in {"/", "/demo"}:
            self.send_file("运行演示.html")
            return
        if path == "/api/status":
            self.send_json(status_payload())
            return
        if path == "/api/start-pack":
            self.send_json(start_pack_payload())
            return
        if path == "/api/resolve":
            query = parse_qs(parsed.query).get("q", ["页面22"])[0]
            self.send_json(resolve_payload(query))
            return
        if path == "/api/check":
            self.send_json({"check": run(["python3", "scripts/check_memory_repo.py"])})
            return
        if path == "/api/secret-policy":
            self.send_json(secret_policy_payload())
            return
        if path.startswith("/files/"):
            self.send_file(path.removeprefix("/files/"))
            return
        self.send_file(path.lstrip("/"))

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(length)
        if parsed.path == "/api/proposal":
            self.send_json(proposal_payload(body))
            return
        self.send_error(404)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the local workflow demo server")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8766)
    args = parser.parse_args()
    server = ThreadingHTTPServer((args.host, args.port), DemoHandler)
    print(f"AI Workbench Memory demo running at http://{args.host}:{args.port}/demo")
    server.serve_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
