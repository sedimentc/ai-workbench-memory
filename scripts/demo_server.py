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
RESTRICTED_DOC = re.compile(r"(?ms)\A---\n.*?sensitivity:\s*restricted\s*\n.*?credential_allowed:\s*true\s*\n.*?\n---\n")

STRUCTURE = [
    {
        "module": "00_规则",
        "role": "系统治理层",
        "purpose": "定义 AI 读取、安全、Git、审核、状态生命周期、阶段边界。",
        "files": [
            "00_规则/AI读取规则.md",
            "00_规则/敏感信息规则.md",
            "00_规则/Git协作规则.md",
            "00_规则/审核规则.md",
            "00_规则/阶段边界.md",
        ],
        "defaultRead": "按任务读取",
    },
    {
        "module": "01_项目",
        "role": "项目记忆层",
        "purpose": "保存项目 StartPack、当前状态、接手说明、页面编号、决策和证据。",
        "files": [
            "01_项目/AI工作台/StartPack.md",
            "01_项目/AI工作台/当前状态.md",
            "01_项目/AI工作台/接手说明.md",
            "01_项目/AI工作台/历史证据.md",
        ],
        "defaultRead": "接手项目时读取",
    },
    {
        "module": "07_实战索引",
        "role": "刘大式快速定位层",
        "purpose": "把页面22、技能1、小测、第四级窗口等口语映射成标准对象。",
        "files": [
            "07_实战索引/别名词典.md",
            "07_实战索引/页面索引.md",
            "07_实战索引/技能索引.md",
            "07_实战索引/窗口索引.md",
            "07_实战索引/字段契约索引.md",
            "07_实战索引/连接信息索引.md",
        ],
        "defaultRead": "页面、技能、字段、窗口任务优先读取",
    },
    {
        "module": "03_工作流",
        "role": "操作流程层",
        "purpose": "定义新窗口接手、会议沉淀、测试 Agent 和资源申请怎么走。",
        "files": [
            "03_工作流/新窗口接手流程.md",
            "03_工作流/会议沉淀流程.md",
            "03_工作流/测试Agent流程.md",
            "03_工作流/资源申请流程.md",
        ],
        "defaultRead": "按任务读取",
    },
    {
        "module": "04_资源登记",
        "role": "资源台账层",
        "purpose": "登记页面编号、端口、电脑环境、secret 引用和服务器候选。",
        "files": [
            "04_资源登记/页面角标编号.md",
            "04_资源登记/端口占用.md",
            "04_资源登记/电脑环境.md",
            "04_资源登记/secret引用.md",
            "04_资源登记/服务器候选.md",
        ],
        "defaultRead": "资源任务读取",
    },
    {
        "module": "05_待审核",
        "role": "沉淀审核层",
        "purpose": "AI 或个人总结先变成 proposed，审核后再进入正式记忆。",
        "files": [
            "05_待审核/README.md",
            "05_待审核/记忆提案/20260519-新窗口必须先读StartPack.md",
            "05_待审核/Skill提案/README.md",
            "05_待审核/资源变更提案/README.md",
        ],
        "defaultRead": "审核任务读取",
    },
    {
        "module": "08_导入资料",
        "role": "本机资料接入层",
        "purpose": "导入本机项目 MD/TXT，普通资料进项目资料，敏感资料进受限资料。",
        "files": [
            "08_导入资料/README.md",
        ],
        "defaultRead": "资料追溯和整理时读取",
    },
]


def read_text(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


def safe_relative_path(raw: str) -> Path:
    rel = unquote(raw).strip().lstrip("/")
    path = (ROOT / rel).resolve()
    if ROOT not in path.parents and path != ROOT:
        raise ValueError("path outside repository")
    if ".git" in path.parts or ".demo_runtime" in path.parts:
        raise ValueError("path is not readable from panel")
    return path


def strip_frontmatter(text: str) -> str:
    return FRONTMATTER.sub("", text, count=1).strip()


def parse_frontmatter(text: str) -> dict[str, str]:
    match = FRONTMATTER.match(text)
    if not match:
        return {}
    data: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip()
    return data


def markdown_files() -> list[str]:
    files: list[str] = []
    for path in ROOT.rglob("*.md"):
        if any(part in path.parts for part in (".git", ".github", ".demo_runtime", "dist", "__pycache__")):
            continue
        files.append(str(path.relative_to(ROOT)))
    return sorted(files)


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


def run_lines(command: list[str]) -> list[str]:
    output = str(run(command)["output"])
    return [line for line in output.splitlines() if line.strip()]


def file_summary(rel: str) -> dict[str, object]:
    path = ROOT / rel
    text = path.read_text(encoding="utf-8", errors="ignore") if path.exists() else ""
    data = parse_frontmatter(text)
    title_match = re.search(r"^#\s+(.+)$", strip_frontmatter(text), re.MULTILINE)
    return {
        "path": rel,
        "title": title_match.group(1) if title_match else Path(rel).stem,
        "status": data.get("status", ""),
        "type": data.get("type", ""),
        "sensitivity": data.get("sensitivity", ""),
    }


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
    lines = read_text(rel).splitlines()
    index = 0
    def clean_cell(value: str) -> str:
        value = value.strip()
        if value.startswith("`") and value.endswith("`") and value.count("`") == 2:
            return value[1:-1]
        return value

    while index < len(lines):
        raw = lines[index]
        line = raw.strip()
        if not line.startswith("|"):
            headers = None
            index += 1
            continue
        cells = [clean_cell(cell) for cell in line.strip("|").split("|")]
        next_line = lines[index + 1].strip() if index + 1 < len(lines) else ""
        next_cells = [cell.strip() for cell in next_line.strip("|").split("|")] if next_line.startswith("|") else []
        if next_cells and all(re.fullmatch(r":?-{3,}:?", cell) for cell in next_cells):
            headers = cells
            index += 2
            continue
        if all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells):
            index += 1
            continue
        if len(cells) != len(headers):
            index += 1
            continue
        rows.append(dict(zip(headers, cells)))
        index += 1
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
        "modules": STRUCTURE,
    }


def git_payload() -> dict[str, object]:
    branches = []
    for line in run_lines(["git", "branch", "--all", "--verbose", "--no-abbrev"]):
        active = line.startswith("*")
        cleaned = line[2:].strip() if active else line.strip()
        parts = cleaned.split(None, 2)
        if not parts:
            continue
        branches.append(
            {
                "active": active,
                "name": parts[0],
                "commit": parts[1] if len(parts) > 1 else "",
                "message": parts[2] if len(parts) > 2 else "",
            }
        )
    commits = []
    for line in run_lines(["git", "log", "--oneline", "--decorate", "-8"]):
        commit, _, message = line.partition(" ")
        commits.append({"commit": commit, "message": message})
    return {
        "current": run(["git", "branch", "--show-current"])["output"],
        "branches": branches,
        "commits": commits,
        "status": run_lines(["git", "status", "--short"]),
        "remote": run(["git", "remote", "-v"])["output"],
    }


def structure_payload() -> dict[str, object]:
    return {
        "workflow": [
            "用户口语/需求",
            "AI入口.md 路由",
            "07_实战索引定位",
            "01_项目 StartPack 接手",
            "03_工作流执行",
            "05_待审核沉淀",
            "Git PR + 自检合并",
        ],
        "modules": STRUCTURE,
        "files": markdown_files(),
        "core": [
            file_summary("AI入口.md"),
            file_summary("总览.md"),
            file_summary("01_项目/AI工作台/StartPack.md"),
            file_summary("07_实战索引/别名词典.md"),
            file_summary("04_资源登记/页面角标编号.md"),
            file_summary("05_待审核/README.md"),
        ],
    }


def document_payload(rel: str) -> dict[str, object]:
    path = safe_relative_path(rel)
    if not path.exists() or not path.is_file():
        raise FileNotFoundError(rel)
    text = path.read_text(encoding="utf-8")
    data = parse_frontmatter(text)
    restricted = RESTRICTED_DOC.search(text) is not None
    if restricted:
        body = "# 受限凭据文档\n\n该文档允许核心成员记录真实协作凭据，面板默认不展示正文。需要查看请在本机文件中打开，并确认仓库访问范围。"
    else:
        body = strip_frontmatter(text)
    return {
        "path": str(path.relative_to(ROOT)),
        "frontmatter": data,
        "restricted": restricted,
        "body": body,
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


def resources_payload() -> dict[str, object]:
    return {
        "pageBadges": parse_table("04_资源登记/页面角标编号.md"),
        "ports": parse_table("04_资源登记/端口占用.md"),
        "machines": parse_table("04_资源登记/电脑环境.md"),
        "secretRefs": parse_table("04_资源登记/secret引用.md"),
        "serverCandidates": parse_table("04_资源登记/服务器候选.md"),
    }


def imported_payload() -> dict[str, object]:
    imported = []
    root = ROOT / "08_导入资料"
    if root.exists():
        for path in sorted(root.rglob("*.md")):
            if path.name == "README.md":
                continue
            imported.append(file_summary(str(path.relative_to(ROOT))))
    return {"imported": imported}


def candidate_payload() -> dict[str, object]:
    roots = [Path("/Users/sediment/Downloads"), Path("/Users/sediment/Documents")]
    candidates: list[dict[str, object]] = []
    for base in roots:
        if not base.exists():
            continue
        for path in sorted(base.rglob("*")):
            if len(candidates) >= 220:
                break
            if not path.is_file() or path.suffix.lower() not in {".md", ".txt"}:
                continue
            if ROOT in path.resolve().parents:
                continue
            if ".git" in path.parts or "node_modules" in path.parts:
                continue
            stat = path.stat()
            candidates.append(
                {
                    "path": str(path),
                    "name": path.name,
                    "size": stat.st_size,
                    "mtime": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M"),
                    "restrictedHint": any(
                        word in path.name.lower()
                        for word in ["manual", "secret", "token", "password", "账号", "密码", "shared_program"]
                    ),
                }
            )
    return {"candidates": candidates}


def import_material_payload(body: bytes) -> dict[str, object]:
    data = json.loads(body.decode("utf-8") or "{}")
    source = Path(str(data.get("path") or "")).expanduser()
    if not source.exists() or not source.is_file():
        raise FileNotFoundError(str(source))
    title = str(data.get("title") or source.stem).strip()
    restricted = bool(data.get("restricted"))
    dest_dir = ROOT / "08_导入资料" / ("受限资料" if restricted else "项目资料")
    dest_dir.mkdir(parents=True, exist_ok=True)
    slug = re.sub(r"[^0-9A-Za-z\u4e00-\u9fff]+", "-", title).strip("-") or "untitled"
    dest = dest_dir / f"{slug}.md"
    counter = 2
    while dest.exists():
        dest = dest_dir / f"{slug}-{counter}.md"
        counter += 1
    now = datetime.now().astimezone().strftime("%Y-%m-%d")
    material_id = "IMPORT-" + datetime.now().astimezone().strftime("%Y%m%d%H%M%S")
    text = source.read_text(encoding="utf-8", errors="replace").rstrip()
    credential = "credential_allowed: true\n" if restricted else ""
    content = f"""---
id: {material_id}
type: imported_material
status: current
owner: 陈纪言
reviewer: 刘大/老王
scope: 导入资料
sensitivity: {'restricted' if restricted else 'internal'}
{credential}last_reviewed: {now}
source: {source}
---

# {title}

## 来源

```text
{source}
```

## 原文

{text}
"""
    dest.write_text(content, encoding="utf-8")
    return {"path": str(dest.relative_to(ROOT)), "restricted": restricted}


def proposal_list_payload() -> dict[str, object]:
    proposals: list[dict[str, str]] = []
    roots = [
        ("正式记忆提案", ROOT / "05_待审核" / "记忆提案"),
        ("正式Skill提案", ROOT / "05_待审核" / "Skill提案"),
        ("正式资源提案", ROOT / "05_待审核" / "资源变更提案"),
        ("演示运行提案", RUNTIME_DIR),
    ]
    for category, directory in roots:
        if not directory.exists():
            continue
        for path in sorted(directory.glob("*.md"), reverse=True):
            text = path.read_text(encoding="utf-8", errors="ignore")
            data = parse_frontmatter(text)
            title_match = re.search(r"^#\s+(.+)$", strip_frontmatter(text), re.MULTILINE)
            proposals.append(
                {
                    "category": category,
                    "path": str(path.relative_to(ROOT)) if ROOT in path.resolve().parents else str(path),
                    "id": data.get("id", ""),
                    "status": data.get("status", ""),
                    "owner": data.get("owner", ""),
                    "title": title_match.group(1) if title_match else path.stem,
                }
            )
    return {"proposals": proposals}


def proposal_payload(body: bytes) -> dict[str, object]:
    data = json.loads(body.decode("utf-8") or "{}")
    title = str(data.get("title") or "演示提案-页面22接手规则").strip()
    detail = str(data.get("detail") or "用户说页面22时，AI 应先查别名词典和页面索引，再读项目 StartPack。").strip()
    official = bool(data.get("official"))
    kind = str(data.get("kind") or "memory")
    if kind not in {"memory", "skill", "resource"}:
        kind = "memory"
    now = datetime.now().astimezone()
    date = now.strftime("%Y%m%d")
    timestamp = now.strftime("%H%M%S")
    if official:
        dir_map = {
            "memory": ROOT / "05_待审核" / "记忆提案",
            "skill": ROOT / "05_待审核" / "Skill提案",
            "resource": ROOT / "05_待审核" / "资源变更提案",
        }
        id_map = {
            "memory": "PROPOSAL-MEMORY",
            "skill": "PROPOSAL-SKILL",
            "resource": "PROPOSAL-RESOURCE",
        }
        directory = dir_map[kind]
        proposal_id = f"{id_map[kind]}-{date}-{timestamp}"
    else:
        directory = RUNTIME_DIR
        proposal_id = f"DEMO-PROPOSAL-{date}-{timestamp}"
    directory.mkdir(parents=True, exist_ok=True)
    safe_title = re.sub(r"[^0-9A-Za-z\u4e00-\u9fff]+", "-", title).strip("-") or "untitled"
    path = directory / f"{date}-{safe_title}.md"
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
    return {"path": str(path), "official": official, "content": content}


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
        if path == "/api/structure":
            self.send_json(structure_payload())
            return
        if path == "/api/document":
            rel = parse_qs(parsed.query).get("path", ["README.md"])[0]
            try:
                self.send_json(document_payload(rel))
            except (FileNotFoundError, ValueError) as exc:
                self.send_json({"error": str(exc)}, status=404)
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
        if path == "/api/git":
            self.send_json(git_payload())
            return
        if path == "/api/resources":
            self.send_json(resources_payload())
            return
        if path == "/api/imported":
            self.send_json(imported_payload())
            return
        if path == "/api/import-candidates":
            self.send_json(candidate_payload())
            return
        if path == "/api/proposals":
            self.send_json(proposal_list_payload())
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
        if parsed.path == "/api/import-material":
            try:
                self.send_json(import_material_payload(body))
            except (FileNotFoundError, OSError, ValueError) as exc:
                self.send_json({"error": str(exc)}, status=400)
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
