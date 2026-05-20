---
id: IMPORT-004
type: imported_material
status: current
owner: 陈纪言
reviewer: 刘大/老王
scope: 导入资料
sensitivity: internal
last_reviewed: 2026-05-20
source: /Users/sediment/Downloads/CodexManager-同事接入说明.md
---

# CodexManager同事接入说明

## 来源

```text
/Users/sediment/Downloads/CodexManager-同事接入说明.md
```

## 原文

# CodexManager 同事接入说明

更新时间：2026-05-11 17:41 CST

这份说明给 Mac 上使用 Codex 的同事使用。接入后，同事的 Codex 会通过这台远程 Mac 上的 CodexManager 服务调用模型。

## 接入信息

- API 地址：`https://phwork1mac-mini.tail3e8fb9.ts.net/v1`
- 默认模型：`gpt-5.3-codex`
- Provider 名称：`codexmanager`
- 是否需要加入 Tailscale：不需要，使用公网 Funnel 地址即可

请给每位同事分配独立 API key。不要把 API key 写进文档、仓库、群聊或截图。

## 一键接入

让同事在自己的 Mac 终端里运行下面这段命令。运行后会提示输入 API key，输入时终端不会显示内容，这是正常的。

```bash
/bin/bash <<'CM_SETUP'
set -euo pipefail

BASE_URL="https://phwork1mac-mini.tail3e8fb9.ts.net/v1"
MODEL="gpt-5.3-codex"
PROVIDER="codexmanager"
CODEX_BIN="${CODEX_BIN:-}"

if [[ -z "$CODEX_BIN" ]]; then
  if command -v codex >/dev/null 2>&1; then
    CODEX_BIN="$(command -v codex)"
  elif [[ -x "/usr/local/bin/codex" ]]; then
    CODEX_BIN="/usr/local/bin/codex"
  elif [[ -x "/opt/homebrew/bin/codex" ]]; then
    CODEX_BIN="/opt/homebrew/bin/codex"
  else
    echo "未找到 codex 命令。请先安装或打开 Codex，再重试。"
    exit 1
  fi
fi

CONFIG_DIR="$HOME/.codex"
CONFIG_FILE="$CONFIG_DIR/config.toml"
mkdir -p "$CONFIG_DIR"
touch "$CONFIG_FILE"

STAMP="$(date +%Y%m%d-%H%M%S)"
cp "$CONFIG_FILE" "$CONFIG_FILE.bak.$STAMP"

python3 - "$CONFIG_FILE" "$PROVIDER" "$MODEL" "$BASE_URL" <<'PY'
from pathlib import Path
import re
import sys

path = Path(sys.argv[1])
provider, model, base_url = sys.argv[2], sys.argv[3], sys.argv[4]
text = path.read_text(encoding="utf-8") if path.exists() else ""
lines = text.splitlines()

remove_tables = {
    f"model_providers.{provider}",
    f"profiles.{provider}",
    f"profiles.{provider}_codex",
}
top_keys = {
    "model_provider",
    "model",
    "model_reasoning_effort",
    "forced_login_method",
}

out = []
i = 0
inside_removed_table = False
seen_table = False
table_re = re.compile(r"^\s*\[([^\]]+)\]\s*$")

while i < len(lines):
    line = lines[i]
    m = table_re.match(line)
    if m:
        seen_table = True
        inside_removed_table = m.group(1).strip() in remove_tables
        if inside_removed_table:
            i += 1
            continue
    if inside_removed_table:
        i += 1
        continue
    if not seen_table:
        key = line.split("=", 1)[0].strip() if "=" in line else ""
        if key in top_keys:
            i += 1
            continue
    out.append(line)
    i += 1

prefix = [
    f'model_provider = "{provider}"',
    f'model = "{model}"',
    'model_reasoning_effort = "medium"',
    'forced_login_method = "api"',
    "",
]

body = "\n".join(out).strip()
suffix = f"""
[model_providers.{provider}]
name = "CodexManager"
base_url = "{base_url}"
wire_api = "responses"
requires_openai_auth = true
request_max_retries = 4
stream_max_retries = 10
stream_idle_timeout_ms = 300000

[profiles.{provider}]
model_provider = "{provider}"
model = "{model}"
model_reasoning_effort = "medium"

[profiles.{provider}_codex]
model_provider = "{provider}"
model = "{model}"
model_reasoning_effort = "medium"
""".strip()

parts = ["\n".join(prefix).rstrip()]
if body:
    parts.append(body)
parts.append(suffix)
path.write_text("\n\n".join(parts) + "\n", encoding="utf-8")
PY

echo "已备份原配置到：$CONFIG_FILE.bak.$STAMP"
echo "已写入 CodexManager 配置：$BASE_URL"
echo
printf "请输入你拿到的 CodexManager API key（输入时不会显示）："
IFS= read -rs CM_KEY
printf "\n"

if [[ -z "$CM_KEY" ]]; then
  echo "API key 为空，已停止。配置文件已写入，但还没有登录。"
  exit 1
fi

printf '%s\n' "$CM_KEY" | "$CODEX_BIN" login --with-api-key

echo
echo "接入完成。之后新开的 Codex 会话会使用 CodexManager。"
echo "如需验证，可运行："
echo "$CODEX_BIN --ask-for-approval never exec -C /tmp --skip-git-repo-check --sandbox read-only --ephemeral 'Reply with exactly OK. Do not use tools.'"
CM_SETUP
```

## 验证

接入后，同事可以新开一个终端运行：

```bash
codex --ask-for-approval never exec \
  -C /tmp \
  --skip-git-repo-check \
  --sandbox read-only \
  --ephemeral \
  'Reply with exactly OK. Do not use tools.'
```

正常结果应该只回复：

```text
OK
```

## 手动配置

如果同事不想运行一键脚本，也可以手动编辑：

```text
~/.codex/config.toml
```

加入或替换为：

```toml
model_provider = "codexmanager"
model = "gpt-5.3-codex"
model_reasoning_effort = "medium"
forced_login_method = "api"

[model_providers.codexmanager]
name = "CodexManager"
base_url = "https://phwork1mac-mini.tail3e8fb9.ts.net/v1"
wire_api = "responses"
requires_openai_auth = true
request_max_retries = 4
stream_max_retries = 10
stream_idle_timeout_ms = 300000

[profiles.codexmanager]
model_provider = "codexmanager"
model = "gpt-5.3-codex"
model_reasoning_effort = "medium"
```

然后登录 API key：

```bash
printf '%s\n' '这里换成分配给你的 API key' | codex login --with-api-key
```

注意：手动命令会把 API key 留在命令历史里，不推荐。更推荐使用上面的一键脚本，因为它会隐藏输入。

## 常见问题

### 提示 `codex: command not found`

说明本机还没有可用的 Codex CLI。请先安装或打开 Codex，再重新运行一键脚本。

### 仍然请求 `api.openai.com`

说明 Codex 没有读到 `codexmanager` provider。检查 `~/.codex/config.toml` 顶部是否有：

```toml
model_provider = "codexmanager"
```

如果 Codex Desktop 已经打开，改完配置后建议完全退出再重新打开。

### 返回 401 或认证失败

通常是 API key 输入错了，或者 key 已被禁用。请联系管理员重新分配 API key。

### 返回 502 或长时间无响应

先确认网络可以访问：

```bash
curl -I https://phwork1mac-mini.tail3e8fb9.ts.net/v1/models
```

如果能连通但 Codex 仍失败，请把错误时间和错误信息发给管理员排查。

## 管理员提醒

- 每位同事分配独立 API key，方便限流、停用和审计。
- 不要把 CodexManager Web UI 暴露到公网。
- 只对外提供 `https://phwork1mac-mini.tail3e8fb9.ts.net/v1` 这个 API 入口。
- 如果某个 key 泄漏，立即在 CodexManager 中禁用或删除对应 key。
