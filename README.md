# Resume Craft

> **一个「先查证、再写作、后审查」的多 Agent 简历制作 Skill。** 基于 Claude Agent SDK：意图路由 → 分模块写作 → 事实核查 + 面试官双 Agent 并行质保 → 交叉验证，产出经得起面试官追问的简历。

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](./LICENSE)
[![Python](https://img.shields.io/badge/python-3.x-blue)](#)
[![Built on](https://img.shields.io/badge/built_on-Claude_Agent_SDK-111827)](#)

---

## 它能做什么

| 能力 | 说明 |
| --- | --- |
| **从零写简历** | 意图路由 + 每次一个问题引导，逐步收集信息 |
| **针对 JD 优化** | 简历-JD 差距分析 → 调整 → 质量检查 → 输出 |
| **简历诊断** | 给出整体评分、必须修复项、建议修改项 |
| **增量更新** | 单独编写 / 修改项目经历、技能、实习、教育等子部分 |
| **并行质保** | 事实核查 Agent + 面试官 Agent 独立盲审，视角互不污染 |
| **交叉验证** | 面试官标记的「事实疑点」自动触发核查员二次验证 |
| **反包装约束** | 防止术语升级（如「函数调用」不写成「Agent 间通信」） |

---

## 30 秒上手

在 Claude Code 中直接说：

```
帮我写简历
```

Claude 自动识别意图并引导：**选模式 → 逐步提问 → 写作 → 双 Agent 质保 → 交叉验证 → 输出**。

针对 JD 优化：

```
针对这个 JD 优化我的简历：<粘贴 JD>
```

---

## 架构：双 Agent 质保闭环

```
用户输入
  │  意图路由（从零写 / JD 优化 / 诊断 / 增量更新）
  ▼
写作流程 ────────► 质量保证（spawn 子 Agent）
(Claude 原生)      ├── 事实核查 Agent   ←── 并行执行
  ▲                └── 面试官 Agent     （独立视角，互不污染）
  │                      │
  └──── 修正 ◄── 面试官标记 [事实疑点]？
                        │ 是
                        ▼
                  核查员定向二次验证
```

- **共享记忆**：所有子 Agent 通过 `resume-state.json` 同步状态，避免重复检查，支持多轮收敛
- **交叉验证**：事实疑点触发核查员定向复验，能过的疑点才消除
- **方向偏差检测**：质保发现 ≥3 个「必须修复 / 包装过度」时，判定初稿方向偏了，重新生成而非逐个修补

---

## 设计原则

**四条红线**：零编造（所有内容基于客观真源，不猜测）· 简历正直（不虚构夸大，「参与」不写成「主导」）· 信息密度（30 秒抓住重点）· 面试官视角（始终站在面试官角度审查）

**反包装约束**：确保描述与实际实现匹配——「文件读写」不升级为「存储层」、「条件分支」不升级为「动态编排」、「函数调用」不升级为「Agent 间通信」。

---

## 工程质量

- **两层 Eval**，可独立运行：
  - Layer 1 · 结构完整性：14 项检查（SKILL.md、references、子 Agent、四条红线、交叉审查、共享记忆等）
  - Layer 2 · 内容质量：9 项检查（教育背景、STAR 结构、量化成果、篇幅、排版等）
- **状态管理**：`state_manager.py` 提供状态 CRUD 与变更历史
- **零第三方依赖**：Python 3.x + Claude Code 即可运行

```bash
# 结构完整性检查（秒级，14 项）
python evals/eval_runner.py structure
# 内容质量检查（9 项）
python evals/eval_runner.py quality "简历文本"
```

---

## 目录结构

```
├── SKILL.md            # 入口：意图路由 + 4 个功能模块 + 约束规则
├── references/         # 7 个领域文档（STAR 方法论、面试官视角、校招模板等）
├── scripts/
│   └── state_manager.py   # 状态管理（CRUD + 历史）
├── evals/
│   ├── eval_runner.py     # 两层 Eval 运行器
│   └── test_cases.json
└── docs/superpowers/   # 设计规格与实现计划
```

## License

[MIT](./LICENSE)
