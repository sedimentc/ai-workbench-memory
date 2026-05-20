---
id: RES-SECRET-REF-001
type: resource_registry
status: current
owner: 陈纪言
reviewer: 刘大/老王
scope: secret 引用
sensitivity: internal
last_reviewed: 2026-05-19
source: 王老师 Secret Ref 思路、刘大受限凭据记录口径
---

# secret引用

本文件登记敏感信息的引用方式。当前团队口径允许少数核心成员在受限文档记录真实凭据，但普通文档仍优先使用 `secret://...` 引用。

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

- 普通共享 MD、技能库、证据和提案里不写真实值。
- 真实值只允许写入 `sensitivity: restricted` 且 `credential_allowed: true` 的文档。
- AI 发现真实值时，要先判断是否应该写入受限文档；不确定时改为 secret 引用。
- 当前推荐真实凭据登记位置：`07_实战索引/连接信息索引.md`。
