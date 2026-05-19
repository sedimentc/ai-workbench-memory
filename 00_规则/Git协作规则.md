---
id: RULE-GIT-001
type: rule
status: current
owner: 陈纪言
reviewer: 肖明/刘大
scope: 全局
sensitivity: internal
last_reviewed: 2026-05-19
source: 肖明 GitHub 共享库方案
---

# Git协作规则

第一版共享 MD 系统用 GitHub 管理版本、分支和审核。

## 分支建议

| 分支 | 用途 |
| --- | --- |
| `main` | 公司当前正式版本 |
| `person/chenjiyan` | 陈纪言个人实验 |
| `person/xiaoming` | 肖明个人实验 |
| `proposal/...` | 准备提交审核的提案分支 |

## 合并规则

正式目录的变更建议走 PR 或负责人确认。资源编号、页面角标、端口登记必须避免多人直接抢改。

## 个人实验

个人可以在自己的分支和 `06_个人实验/` 里自由试，但这些内容默认不推荐给团队使用。

好用内容应整理为 `05_待审核/` 提案，审核通过后再进入正式目录。

## 提交前检查

每次合并前运行：

```bash
python3 scripts/check_memory_repo.py
```

