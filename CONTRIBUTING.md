---
id: SYS-CONTRIBUTING-001
type: workflow
status: current
owner: 陈纪言
reviewer: 刘大/老王/肖明
scope: 全局
sensitivity: internal
last_reviewed: 2026-05-19
source: GitHub 协作落地规则
---

# 协作说明

本仓库的目标不是让所有人随手堆资料，而是沉淀能被 AI 稳定读取、能被团队审核、能被追溯来源的协作记忆。

## 提交前必须确认

1. 新增正式文档必须有 YAML 头部。
2. `id` 必须全局唯一。
3. `status` 必须是允许状态之一。
4. 真实密码、token、cookie、API key 不得写入仓库。
5. 页面角标、端口等资源变更必须检查冲突。
6. 草稿、个人实验、待审核内容不得被写成正式规则。

## 推荐流程

```text
个人实验
    ↓
待审核提案
    ↓
负责人审核
    ↓
合并正式目录
    ↓
更新决策记录或当前状态
```

## 提交前自检

```bash
python3 scripts/check_memory_repo.py
```

自检通过后再提交 PR。

## 角色分工

陈纪言负责共享 MD 系统底座、项目记忆、资源登记、工作流、待审核流程和模板。

肖明负责技能库正文、程序提示词、Skill 效果测试和技能提案。

刘大/老王负责关键规则和架构方向确认。

