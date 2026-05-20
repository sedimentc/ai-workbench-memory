---
id: IMPORT-005
type: imported_material
status: current
owner: 陈纪言
reviewer: 刘大/老王
scope: 导入资料
sensitivity: internal
last_reviewed: 2026-05-20
source: /Users/sediment/Documents/DoneGuard使用说明书.md
---

# DoneGuard使用说明书

## 来源

```text
/Users/sediment/Documents/DoneGuard使用说明书.md
```

## 原文

# DoneGuard 使用说明书

## 1. DoneGuard 是什么

DoneGuard 是一套防止 AI “看起来做完了，但其实是假完成”的验收流程。

它的核心思想很简单：

- 主任务 AI 负责做事。
- 测试方案 Agent 负责先写验收标准。
- 人工确认验收标准。
- 独立测试 Agent 负责验收，不让主任务 AI 自己证明自己。
- 所有证据、报告、状态都沉淀到 `.doneguard` 和控制面板里。

适合用在这些任务：

- 在线表格写入、飞书表格更新、Excel 数据处理。
- 股票研究、财务数据核验、雪球/网页信息整理。
- 前端页面、后端接口、数据库写入。
- 任何容易出现“页面看起来好了，但实际没写进后端/数据库/线上表”的任务。

## 2. 当前可用状态

当前 DoneGuard 已经可用。

Provider 状态：

| Provider | 当前状态 | 用途 |
| --- | --- | --- |
| DeepSeek | 已可用 | 测试方案、第一次正式验收 |
| Codex Desktop / spawn_agent | 已有文件桥协议 | 独立 Codex Agent 验收，需要宿主或主线程调用 |
| Claude Code / caudecode | 已预留 | 后续配置命令后可做第二模型复核 |
| local | 已可用 | 只生成模板，不做真正模型验收 |

控制面板：

```text
/Users/sediment/Documents/doneguard-board/index.html
```

## 3. 标准流程

### 第一步：在项目目录初始化 DoneGuard

进入任务所在项目目录后执行：

```bash
python3 /Users/sediment/.codex/skills/doneguard/scripts/doneguard.py init --task "这里写任务摘要"
```

会生成：

```text
.doneguard/task.md
.doneguard/test_plan.md
.doneguard/approved_test_plan.md
.doneguard/verification_report.md
.doneguard/context/
.doneguard/expected/
.doneguard/evidence/
.doneguard/artifacts/
```

### 第二步：生成测试方案

推荐优先用 DeepSeek：

```bash
python3 /Users/sediment/.codex/skills/doneguard/scripts/doneguard.py plan --provider deepseek --type spreadsheet,research --task .doneguard/task.md
```

常见 `--type`：

| 类型 | 适用任务 |
| --- | --- |
| `spreadsheet` | Excel、飞书表格、CSV、TSV |
| `research` | 投研、数据来源核验、财务指标 |
| `web-automation` | 网页点击、雪球、第三方网站 |
| `frontend` | 页面、交互、截图 |
| `backend` | API、服务、日志 |
| `database` | 数据库写入、迁移、读回 |

### 第三步：人工确认测试方案

打开：

```text
.doneguard/test_plan.md
```

你可以：

- 直接通过。
- 删除不需要的检查项。
- 补充更严格的检查项。
- 放弃本轮测试。

确认后，把最终版本保存为：

```text
.doneguard/approved_test_plan.md
```

注意：测试方案 Agent 需要人工确认；测试执行 Agent 在方案确认后不需要再次确认，除非涉及删除、写入、付费、泄密或越权。

### 第四步：主任务 AI 执行任务并保留证据

主任务 AI 做完后，需要把证据放进：

```text
.doneguard/evidence/
```

常见证据包括：

- 线上读回 JSON。
- 写入前后截图。
- Excel/TSV 对比文件。
- 数据来源链接。
- API 返回结果。
- 日志文件。
- 关键命令输出。

原则：不要只说“做完了”，要能证明“真的做完了”。

### 第五步：正式验收

如果用 DeepSeek 验收：

```bash
python3 /Users/sediment/.codex/skills/doneguard/scripts/doneguard.py verify --provider deepseek --type spreadsheet,research --approved-plan .doneguard/approved_test_plan.md --evidence .doneguard/evidence/readback.json
```

如果证据有多个，可以重复传：

```bash
--evidence .doneguard/evidence/a.json --evidence .doneguard/evidence/b.tsv
```

验收报告会写入：

```text
.doneguard/verification_report.md
```

报告结论只有三种：

| 状态 | 含义 |
| --- | --- |
| `pass` | 验收通过 |
| `fail` | 验收失败，需要返工 |
| `partial` | 部分通过或证据不足，需要人工判断 |

## 4. Codex Desktop / spawn_agent 验收流程

Python 脚本不能直接调用 Codex Desktop 的 `spawn_agent`，所以 DoneGuard 使用文件桥。

### 生成 Codex Desktop 验收请求

```bash
python3 /Users/sediment/.codex/skills/doneguard/scripts/doneguard.py bridge-request --provider codex-desktop --role verify
```

会生成：

```text
.doneguard/artifacts/bridge/requests/<request-id>.json
.doneguard/artifacts/bridge/latest_request.json
.doneguard/artifacts/agent_packet/agent_prompt.md
.doneguard/artifacts/agent_packet.zip
```

### 查看请求状态

```bash
python3 /Users/sediment/.codex/skills/doneguard/scripts/doneguard.py bridge-status
```

状态一般是：

```text
pending_host
```

意思是：等待宿主层或主线程打开独立 Codex Agent。

### 独立 Codex Agent 验收

当前过渡方式：

1. 主线程读取 request JSON。
2. 用 `spawn_agent` 开一个独立 Agent。
3. 把 `agent_prompt.md` 和 `agent_packet` 路径交给它。
4. 独立 Agent 输出验收报告。
5. 把报告保存成 Markdown。

### 导入 Codex Agent 验收结果

```bash
python3 /Users/sediment/.codex/skills/doneguard/scripts/doneguard.py bridge-result --request <request.json> --report <agent-report.md> --agent-id <agent-id>
```

导入后会自动写回：

```text
.doneguard/verification_report.md
```

## 5. 多模型交叉验证

高风险任务可以同时跑多模型：

```bash
python3 /Users/sediment/.codex/skills/doneguard/scripts/doneguard.py cross-check --providers deepseek,codex-desktop,claude-code --type spreadsheet,research
```

行为：

- DeepSeek 可用时直接出报告。
- Codex Desktop 会生成 `pending_host` bridge request。
- Claude Code 如果没配置，会显示 `not_configured`。
- 汇总写到：

```text
.doneguard/artifacts/cross_checks/summary.json
```

## 6. 控制面板

生成单任务面板：

```bash
python3 /Users/sediment/.codex/skills/doneguard/scripts/doneguard.py dashboard
```

生成统一看板：

```bash
python3 /Users/sediment/.codex/skills/doneguard/scripts/doneguard.py board --root /Users/sediment/Documents --out /Users/sediment/Documents/doneguard-board
```

统一看板路径：

```text
/Users/sediment/Documents/doneguard-board/index.html
```

看板里能看到：

- 每个任务的状态。
- 单任务 dashboard。
- agent packet。
- bridge request。
- cross-check 汇总。
- DeepSeek / Claude Code / Codex Desktop provider 状态。

## 7. 推荐使用规则

### 普通任务

使用：

```text
DeepSeek 测试方案 + DeepSeek 正式验收
```

适合：

- 表格整理。
- 数据核验。
- 简单研究任务。

### 在线表格写入任务

必须要求：

- 写入前读取线上真实表结构。
- 用股票代码/主键匹配，不要按旧行号写。
- 写入后全量读回。
- 验证写入列、行数、关键字段、空值、是否串行。

### 代码或 UI 任务

建议：

```text
DeepSeek 第一次验收 + Codex Desktop 独立 Agent 再验一次
```

适合：

- 前端页面。
- 后端接口。
- 数据库写入。
- 复杂代码修改。

### 高风险任务

建议：

```text
DeepSeek + Codex Desktop + Claude Code 三方交叉验证
```

适合：

- 批量写线上表。
- 数据库写入。
- 大规模自动化点击。
- 重要投研结论。
- 会影响老板决策的数据表。

## 8. 常见问题

### 1. DoneGuard 现在能不能用？

能用。DeepSeek 已经实测可调用，dashboard/board 已可生成，Codex Desktop bridge 请求和结果导入也已跑通。

### 2. 它能不能自动打开一个新的 Codex 窗口？

目前还不能由 Python 脚本自动打开。`spawn_agent` 是 Codex Desktop 宿主能力，不是普通脚本能力。

现在的正确做法是：

- DoneGuard 生成 bridge request。
- 主线程或宿主层调用 `spawn_agent`。
- 再把报告导回 DoneGuard。

### 3. 为什么不让主任务 AI 自己验收？

因为最容易出现“假跑通”：

- 页面看起来改好了，但后端没接。
- 表格看起来写了，但刷新后没保存。
- 数据看起来完整，但字段口径拿错。
- AI 自己测试时漏掉关键边界。

### 4. 什么情况下可以不用 DoneGuard？

很小、低风险、不会写线上数据的任务可以不用。

例如：

- 改一句文案。
- 简单解释代码。
- 本地小文件格式调整。

但只要涉及线上写入、批量数据、投研结论、数据库、网页自动化，就建议用。

## 9. 最短使用模板

```bash
cd <项目目录>

python3 /Users/sediment/.codex/skills/doneguard/scripts/doneguard.py init --task "任务摘要"

python3 /Users/sediment/.codex/skills/doneguard/scripts/doneguard.py plan --provider deepseek --type spreadsheet,research --task .doneguard/task.md

# 人工确认 .doneguard/test_plan.md，并保存为 .doneguard/approved_test_plan.md

# 主任务 AI 执行任务，并把证据放入 .doneguard/evidence/

python3 /Users/sediment/.codex/skills/doneguard/scripts/doneguard.py verify --provider deepseek --type spreadsheet,research --approved-plan .doneguard/approved_test_plan.md --evidence .doneguard/evidence/readback.json

python3 /Users/sediment/.codex/skills/doneguard/scripts/doneguard.py dashboard

python3 /Users/sediment/.codex/skills/doneguard/scripts/doneguard.py board --root /Users/sediment/Documents --out /Users/sediment/Documents/doneguard-board
```

## 10. 一句话记忆

DoneGuard 不是让 AI 多说一句“我检查过了”，而是把验收变成一个独立、可追踪、可复盘的流程。
