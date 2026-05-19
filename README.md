---
id: SYS-README-001
type: overview
status: current
owner: 陈纪言
reviewer: 刘大/老王/肖明
scope: 全局
sensitivity: internal
last_reviewed: 2026-05-19
source: 第一版共享 MD 系统落地
---

# AI 工作台协作记忆库

本仓库是第一版共享 MD 系统，用来承载 AI 工作台的项目记忆、接手说明、资源登记、工作流、待审核提案和模板。

第一版采用 GitHub + Markdown 方式落地。MD 是人和 AI 都能读的协作层，不承担最终运行态职责；页面角标发号、窗口心跳、资源锁、Start Pack 自动生成等能力，后续可迁移到中心服务或数据库。

## 当前边界

- 做：AI 新窗口接手、项目记忆、资源登记、待审核、Git 协作、AI 工作台样板项目。
- 不做：完整中心服务、自动语义搜索、复杂权限系统、技能库正文、全公司知识库一次性铺开。

详细边界见 `00_规则/阶段边界.md`。

## 主要入口

- `AI入口.md`：新 AI 窗口必须先读。
- `演示入口.md`：现场演示从这里开始。
- `总览.md`：人和 AI 的导航页。
- `01_项目/AI工作台/StartPack.md`：AI 工作台项目接手包。
- `05_待审核/`：所有候选记忆、规则、资源变更先进入这里。
- `scripts/check_memory_repo.py`：基础自检脚本。
- `scripts/new_proposal.py`：生成标准待审核提案。
- `scripts/run_demo_check.py`：演示前准备检查。
- `10_启动材料/`：上线步骤、演示脚本、第一周推进清单和验收清单。
- `10_启动材料/功能对照表.md`：对照刘大、王老师、肖明原始框架。
- `10_启动材料/二期中心服务路线图.md`：说明后续如何升级到中心服务。

## 分工

陈纪言负责共享 MD 系统底座、项目记忆、AI 入口、资源登记、待审核流程和模板。

肖明负责技能共享库、程序提示词、Skill 效果测试和技能库维护。

## 常用命令

自检：

```bash
python3 scripts/check_memory_repo.py
```

演示前检查：

```bash
python3 scripts/run_demo_check.py
```

新建记忆提案：

```bash
python3 scripts/new_proposal.py "提案标题" --type memory
```

新建资源变更提案：

```bash
python3 scripts/new_proposal.py "申请页面编号" --type resource
```

## 当前实测闭环

- 已有新窗口接手测试用例。
- 已有新窗口接手实测记录模板。
- 已有新窗口演示提示词和现场答辩问答。
- 已用 `scripts/new_proposal.py` 生成过真实记忆提案。
- 自检脚本会检查项目目录是否包含接手所需核心文件。
