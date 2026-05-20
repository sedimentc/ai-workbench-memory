---
id: IMPORT-007
type: imported_material
status: current
owner: 陈纪言
reviewer: 刘大/老王
scope: 导入资料
sensitivity: internal
last_reviewed: 2026-05-20
source: /Users/sediment/Documents/openclaw-feishu-control/README.md
---

# openclaw-feishu-control README

## 来源

```text
/Users/sediment/Documents/openclaw-feishu-control/README.md
```

## 原文

# openclaw-feishu-control

把飞书群消息映射成 `openclaw` 控制命令，默认使用飞书“长连接”收事件（不需要公网回调 URL）。

## 1. 本地启动

```bash
cd /Users/sediment/Documents/openclaw-feishu-control
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

加载环境变量后启动（默认长连接）：

```bash
set -a; source .env; set +a
python long_conn.py
```

如需回调模式，设置 `FEISHU_RUN_MODE=webhook` 后使用 `python main.py`。

本项目默认使用 macOS `launchctl` 控制 `openclaw`。如果你的服务标签不是 `com.openclaw.service`，改 `.env` 里的 `OPENCLAW_LAUNCHD_LABEL`。

## 2. 飞书应用配置（自建应用，长连接）

1. 创建自建应用，开启机器人能力。
2. 在事件与回调中选择“长连接”方式订阅事件。
3. 订阅事件：`im.message.receive_v1`
4. 在权限里添加并发布：
   - `im:message`
   - `im:message.group_at_msg`
   - `im:message.send_as_bot`
5. 把机器人拉进你要控制的群。

## 3. 群里如何控制

在群里发：

- `/status`
- `/start`
- `/stop`
- `/restart`

服务会执行 `OPENCLAW_COMMAND_MAP` 中对应命令并把输出回发到群里。

## 3.1 launchctl 预检查

先在机器上确认 openclaw 的 launchd label（示例）：

```bash
launchctl list | grep -i claw
```

把查到的 label 填到 `.env` 的 `OPENCLAW_LAUNCHD_LABEL`。

## 4. 安全建议（强烈建议）

1. 不要把服务暴露到公网裸奔，前面加网关/鉴权白名单。
2. `OPENCLAW_COMMAND_MAP` 只配置固定白名单命令，不要接受任意 shell 文本。
3. 使用专门低权限账号运行服务。
4. 命令如果需要 sudo，请做最小化 sudoers 放行，不要给全 sudo。
