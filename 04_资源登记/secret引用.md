---
id: RES-SECRET-REF-001
type: resource_registry
status: current
owner: 陈纪言
reviewer: 刘大/老王
scope: secret 引用
sensitivity: internal
last_reviewed: 2026-05-19
source: 王老师 Secret Ref 思路
---

# secret引用

本文件只登记敏感信息的引用方式，不登记真实值。

## 引用格式

```text
secret://<位置>/<系统>/<名称>
```

示例：

```text
secret://computer0/keychain/dashboard-login
secret://computer1/env/DEEPSEEK_API_KEY
secret://liuda/private-channel/tailscale-dashboard-password
```

## 当前引用

| 引用 | 用途 | 负责人 | 状态 |
| --- | --- | --- | --- |
| `secret://liuda/private-channel/dashboard-password` | Dashboard 登录密码 | 刘大 | current |
| `secret://local/env/DEEPSEEK_API_KEY` | DoneGuard DeepSeek 验收 | 使用者本人 | current |

## 规则

- 共享 MD、技能库、证据和提案里都不能写真实值。
- AI 发现真实值时，要提醒用户改为 secret 引用。

