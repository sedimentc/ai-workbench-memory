#!/usr/bin/env python3
"""Export Markdown and HTML packets for live demos."""

from __future__ import annotations

import re
import html
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "dist"
OUT_MD = OUT_DIR / "演示包.md"
OUT_HTML = OUT_DIR / "index.html"

DEMO_FILES = [
    "10_启动材料/当前系统状态.md",
    "演示入口.md",
    "README.md",
    "AI入口.md",
    "总览.md",
    "07_实战索引/README.md",
    "07_实战索引/别名词典.md",
    "07_实战索引/页面索引.md",
    "07_实战索引/技能索引.md",
    "07_实战索引/连接信息索引.md",
    "08_导入资料/README.md",
    "01_项目/部门总览.md",
    "01_项目/AI工作台部门/部门总览.md",
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
RESTRICTED_DOC = re.compile(r"(?ms)\A---\n.*?sensitivity:\s*restricted\s*\n.*?credential_allowed:\s*true\s*\n.*?\n---\n")


def strip_frontmatter(text: str) -> str:
    return FRONTMATTER.sub("", text, count=1).strip()


def redacted_restricted_body(rel: str) -> str:
    return "\n".join(
        [
            "# 受限凭据文档",
            "",
            f"`{rel}` 是核心成员受限文档，允许记录必要账号、密码、API key、token 等协作凭据。",
            "",
            "演示包不会导出该文件正文，避免真实凭据被复制到 `dist/`。",
            "",
            "现场只讲规则：真实凭据只允许写在 `sensitivity: restricted` 且 `credential_allowed: true` 的文档里，并且必须标用途、负责人、风险级别和轮换规则。",
        ]
    )


def read_demo_sections() -> list[tuple[str, str]]:
    sections: list[tuple[str, str]] = []
    for rel in DEMO_FILES:
        path = ROOT / rel
        if not path.exists():
            raise SystemExit(f"Missing demo source file: {rel}")
        text = path.read_text(encoding="utf-8")
        if RESTRICTED_DOC.search(text):
            sections.append((rel, redacted_restricted_body(rel)))
        else:
            sections.append((rel, strip_frontmatter(text)))
    return sections


def export_markdown(now: str, sections: list[tuple[str, str]]) -> None:
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
    for index, (rel, _) in enumerate(sections, start=1):
        parts.append(f"{index}. `{rel}`")
    parts.append("")

    for rel, body in sections:
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

    OUT_MD.write_text("\n".join(parts).rstrip() + "\n", encoding="utf-8")


def markdownish_to_html(text: str) -> str:
    lines = []
    in_code = False
    code_lines: list[str] = []
    for raw in text.splitlines():
        line = raw.rstrip()
        if line.startswith("```"):
            if in_code:
                lines.append("<pre><code>" + html.escape("\n".join(code_lines)) + "</code></pre>")
                code_lines = []
                in_code = False
            else:
                in_code = True
            continue
        if in_code:
            code_lines.append(line)
            continue
        if line.startswith("# "):
            lines.append(f"<h1>{html.escape(line[2:].strip())}</h1>")
        elif line.startswith("## "):
            lines.append(f"<h2>{html.escape(line[3:].strip())}</h2>")
        elif line.startswith("### "):
            lines.append(f"<h3>{html.escape(line[4:].strip())}</h3>")
        elif line.startswith("- "):
            lines.append(f"<p class=\"bullet\">{html.escape(line)}</p>")
        elif line.startswith("|"):
            lines.append(f"<pre class=\"table-line\">{html.escape(line)}</pre>")
        elif not line:
            lines.append("")
        else:
            lines.append(f"<p>{html.escape(line)}</p>")
    if in_code:
        lines.append("<pre><code>" + html.escape("\n".join(code_lines)) + "</code></pre>")
    return "\n".join(lines)


def export_html(now: str, sections: list[tuple[str, str]]) -> None:
    nav = "\n".join(
        f'<a href="#section-{index}">{index}. {html.escape(rel)}</a>' for index, (rel, _) in enumerate(sections, start=1)
    )
    body_sections = []
    for index, (rel, body) in enumerate(sections, start=1):
        body_sections.append(
            f"""
<section id="section-{index}">
  <div class="source">来源文件：<code>{html.escape(rel)}</code></div>
  {markdownish_to_html(body)}
</section>
"""
        )
    page = f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>AI 工作台共享 MD 系统演示包</title>
  <style>
    :root {{
      --bg: #f6f7f9;
      --panel: #ffffff;
      --ink: #172033;
      --muted: #647084;
      --line: #d9dee8;
      --accent: #b42318;
      --code: #f0f3f8;
    }}
    body {{
      margin: 0;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background: var(--bg);
      color: var(--ink);
      line-height: 1.6;
    }}
    header {{
      background: var(--panel);
      border-bottom: 1px solid var(--line);
      padding: 28px 32px 20px;
      position: sticky;
      top: 0;
      z-index: 2;
    }}
    header h1 {{
      margin: 0 0 8px;
      font-size: 28px;
    }}
    header p {{
      margin: 0;
      color: var(--muted);
    }}
    main {{
      display: grid;
      grid-template-columns: minmax(220px, 300px) minmax(0, 1fr);
      gap: 20px;
      max-width: 1280px;
      margin: 20px auto;
      padding: 0 20px 40px;
    }}
    nav {{
      align-self: start;
      position: sticky;
      top: 116px;
      background: var(--panel);
      border: 1px solid var(--line);
      padding: 14px;
      max-height: calc(100vh - 140px);
      overflow: auto;
    }}
    nav a {{
      display: block;
      color: var(--ink);
      text-decoration: none;
      padding: 7px 8px;
      border-radius: 6px;
      font-size: 14px;
    }}
    nav a:hover {{
      background: var(--code);
    }}
    section {{
      background: var(--panel);
      border: 1px solid var(--line);
      padding: 22px 26px;
      margin-bottom: 18px;
    }}
    .source {{
      color: var(--muted);
      font-size: 13px;
      border-bottom: 1px solid var(--line);
      padding-bottom: 10px;
      margin-bottom: 18px;
    }}
    h1, h2, h3 {{
      line-height: 1.25;
    }}
    h1 {{
      font-size: 26px;
      margin: 0 0 16px;
    }}
    h2 {{
      font-size: 20px;
      margin: 24px 0 10px;
    }}
    h3 {{
      font-size: 16px;
      margin: 18px 0 8px;
    }}
    p {{
      margin: 8px 0;
    }}
    .bullet {{
      padding-left: 10px;
    }}
    code {{
      background: var(--code);
      padding: 2px 5px;
      border-radius: 4px;
    }}
    pre {{
      background: var(--code);
      padding: 12px;
      overflow: auto;
      border-radius: 6px;
      border: 1px solid var(--line);
    }}
    .table-line {{
      margin: 0;
      border-radius: 0;
      border-bottom: 0;
      padding: 4px 8px;
    }}
    @media (max-width: 860px) {{
      header {{
        position: static;
      }}
      main {{
        display: block;
      }}
      nav {{
        position: static;
        margin-bottom: 20px;
      }}
    }}
  </style>
</head>
<body>
  <header>
    <h1>AI 工作台共享 MD 系统演示包</h1>
    <p>生成时间：{html.escape(now)}。打开本页即可按顺序演示，不需要切换多个 Markdown 文件。</p>
  </header>
  <main>
    <nav>{nav}</nav>
    <div>{"".join(body_sections)}</div>
  </main>
</body>
</html>
"""
    OUT_HTML.write_text(page, encoding="utf-8")


def main() -> int:
    OUT_DIR.mkdir(exist_ok=True)
    now = datetime.now().astimezone().isoformat(timespec="seconds")
    sections = read_demo_sections()
    export_markdown(now, sections)
    export_html(now, sections)
    print(OUT_MD.resolve())
    print(OUT_HTML.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
