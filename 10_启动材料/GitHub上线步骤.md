---
id: LAUNCH-GITHUB-001
type: launch_plan
status: current
owner: 陈纪言
reviewer: 刘大/老王/肖明
scope: GitHub 上线
sensitivity: internal
last_reviewed: 2026-05-19
source: 第一版仓库上线流程
---

# GitHub上线步骤

## 目标

把本地 `ai-workbench-memory` 推到 GitHub，形成团队共享仓库。

## 建议仓库名

```text
ai-workbench-memory
```

## 建议权限

| 人员 | 权限 | 说明 |
| --- | --- | --- |
| 刘大 | Admin | 最终规则确认 |
| 老王 | Maintainer | 架构和方案审核 |
| 陈纪言 | Maintainer | 共享 MD 系统维护 |
| 肖明 | Maintainer | 技能库维护 |
| 其他成员 | Write 或 Read | 视参与程度决定 |

## 本地推送命令

创建 GitHub 空仓库后，在本地执行：

```bash
cd /Users/sediment/Documents/ai-workbench-memory
git remote add origin <GitHub仓库地址>
git push -u origin main
```

## 分支保护建议

`main` 分支建议开启：

- 不允许直接 push。
- 必须通过 PR。
- 必须通过 `Memory Repo Check`。
- 至少 1 人 review。
- 资源登记变更需要陈纪言或刘大/老王确认。
- Skill 变更需要肖明确认。

## 上线后第一件事

开一个测试 PR，只改 `05_待审核/记忆提案/示例提案.md` 或新增一条提案，确认：

- PR 模板可用。
- GitHub Actions 能跑自检。
- review 流程可用。

