# Resume Craft

基于 Claude Agent SDK 的多 Agent 简历制作 Skill。通过意图路由、并行质保、交叉审查机制，帮你制作经得起面试官追问的简历。

## 特性

- **意图路由** — 自动识别用户意图（从零写 / JD 优化 / 诊断 / 增量更新），分发至对应模块
- **子任务分流** — 支持单独编写项目经历、技能、实习、教育等子部分
- **并行质保** — 事实核查 Agent + 面试官 Agent 并行审查，独立视角互不污染
- **交叉审查** — 面试官标记的「事实疑点」自动触发核查员二次验证
- **共享记忆** — 跨 Agent 状态同步，避免重复检查，支持多轮收敛
- **反包装约束** — 防止术语升级（如「函数调用」不写成「Agent 间通信」）
- **两层 Eval** — 结构完整性（14 项）+ 内容质量（9 项），可独立运行

## 快速开始

### 环境要求

- Python 3.x（无第三方依赖）
- Claude Code（需要 Agent 工具支持）

### 安装

将本仓库克隆到 Claude Code 的 skills 目录：

```bash
git clone https://github.com/<your-username>/resume-craft.git ~/.claude/skills/resume-craft
```

### 使用

在 Claude Code 中直接说：

```
帮我写简历
```

Claude 会自动识别意图并引导你完成整个流程。

## 使用示例

### 从零写简历

```
用户：帮我写简历

Claude：请选择：
1. 从零写简历
2. 针对 JD 优化
3. 简历诊断
4. 增量更新

用户：1

Claude：你想投哪类岗位？
1. 技术岗（后端 / 前端 / 算法 / 测试）
2. 产品岗（产品经理 / 产品运营）
3. 设计岗（UI / UX / 交互）
4. 市场 / 职能岗

...（逐步引导，每次一个问题）
```

### 针对 JD 优化

```
用户：针对这个 JD 优化我的简历
[粘贴 JD 文本]

Claude：请提供你的当前简历。

用户：[粘贴简历]

Claude：
## 简历-JD 差距分析

### 匹配技能
- Python：简历中有在线商城项目经验佐证

### 缺失技能
- **required**：Docker
  → 风险：JD 明确要求，缺失可能导致被筛掉

...（差距分析 → 调整 → 质量检查 → 输出）
```

### 简历诊断

```
用户：诊断简历
[粘贴简历]

Claude：
## 简历审查报告

整体评分：6/10

### [必须修复]
1. 缺少教育背景信息 → 建议补充学校、专业、毕业时间

### [建议修改]
1. "负责后端开发" 描述过于空泛 → 建议用 STAR 结构重写
```

## 架构设计

```
用户输入
│
▼
┌──────────────────────────────────────────┐
│  SKILL.md（入口 + 意图路由）              │
│                                          │
│  ┌─────────┐  ┌─────────┐  ┌──────────┐ │
│  │ 模块一   │  │ 模块二   │  │ 模块三   │ │
│  │ 从零写   │  │ JD 优化  │  │ 诊断     │ │
│  └────┬────┘  └────┬────┘  └────┬─────┘ │
│       │            │            │        │
│  ┌────┴────┐       │       ┌────┴─────┐ │
│  │ 模块四   │       │       │ 子任务   │ │
│  │ 增量更新 │       │       │ 路由     │ │
│  └─────────┘       │       └──────────┘ │
└───────┬─────────────┬────────────────────┘
        │             │
  核心流程       质量保证阶段
  (Claude 原生)   (spawn 子 Agent)
        │             │
        ▼             ▼
  references/     ┌─────────────────┐
  (7 个领域文档)  │ 事实核查 Agent   │ ←── 并行执行
                  │ 面试官 Agent     │
                  └────────┬────────┘
                           │
                    面试官标记 [事实疑点]？
                           │
                    ┌──────┴──────┐
                    │ 是          │ 否
                    ▼             ▼
              触发第二轮      直接汇总
              交叉验证        结果
```

### 核心流程说明

1. **意图路由** — SKILL.md 根据用户输入识别意图，分发至对应模块
2. **引导提问** — 每次一个问题，优先选择题，逐步收集信息
3. **真源解析** — 读取用户提供的代码 / 文档 / URL，提取客观数据
4. **内容生成** — 基于真源数据和 STAR 结构生成简历初稿
5. **并行质保** — 事实核查 + 面试官盲审同时进行
6. **交叉验证** — 面试官的疑点触发核查员定向二次验证
7. **优化输出** — 修正问题、精简内容、规范排版

### 共享记忆结构

所有子 Agent 通过 `resume-state.json` 共享状态：

```json
{
  "version": "1.0",
  "module": "intake | generating | verifying | optimizing | done",
  "user_profile": {
    "name": "",
    "target_position": "",
    "education": [],
    "skills": [],
    "projects": []
  },
  "truth_sources": [],
  "resume_draft": "",
  "verification_results": [
    {
      "round": 1,
      "agent": "fact_checker",
      "findings": [],
      "conclusion": "pass"
    },
    {
      "round": 1,
      "agent": "interviewer",
      "score": 8.5,
      "factual_doubts": []
    },
    {
      "round": 2,
      "agent": "fact_checker",
      "cross_check": true,
      "verified_doubts": []
    }
  ],
  "history": []
}
```

## 目录结构

```
resume-craft/
├── SKILL.md                          # 入口：意图路由 + 4 个功能模块 + 约束规则
├── README.md                         # 本文件
│
├── references/                       # 领域知识文档（按需加载）
│   ├── interaction-rules.md          # 交互规则和话术模板
│   ├── resume-guide.md               # 简历制作方法论（STAR 法则等）
│   ├── campus-templates.md           # 校招简历模板（5 种岗位方向）
│   ├── interviewer-perspective.md    # 面试官视角审查指南
│   ├── verification-rules.md         # 事实核查规则（含实现诚实度检查）
│   ├── chinese-format.md             # 中文排版规范
│   ├── job-database.md               # 校招方向面试官考察视角
│   └── troubleshooting.md            # 常见问题处理
│
├── scripts/
│   └── state_manager.py              # 状态管理工具（CRUD + 历史记录）
│
├── evals/
│   ├── eval_runner.py                # 两层 Eval 运行器
│   └── test_cases.json               # 测试用例
│
└── docs/
    └── superpowers/
        ├── specs/                    # 设计规格文档
        └── plans/                    # 实现计划
```

## 脚本使用

### 状态管理 — state_manager.py

```bash
# 初始化状态文件
python scripts/state_manager.py init

# 查看当前状态
python scripts/state_manager.py show

# 更新字段（支持嵌套路径）
python scripts/state_manager.py update --field user_profile.name --value "张三"
python scripts/state_manager.py update --field resume_draft --value "## 简历内容..."

# 追加到数组
python scripts/state_manager.py append --field truth_sources --value "GitHub: github.com/test"

# 查看变更历史
python scripts/state_manager.py history

# 重置状态
python scripts/state_manager.py reset
```

### 质量检查 — eval_runner.py

```bash
# 第一层：结构完整性检查（秒级，14 项）
python evals/eval_runner.py structure

# 第二层：简历内容质量检查（9 项）
python evals/eval_runner.py quality "简历文本内容"
python evals/eval_runner.py quality /path/to/resume.md

# 两层全部运行
python evals/eval_runner.py all "简历文本内容"
```

#### 结构完整性检查项（Layer 1）

| ID | 检查项 | 说明 |
|----|--------|------|
| S001 | SKILL.md frontmatter | name 和 description 是否存在 |
| S002 | References | 7 个参考文档是否齐全 |
| S003 | state_manager.py | 是否可执行 |
| S004 | Modules | 4 个功能模块是否定义 |
| S005 | Red lines | 四条红线是否声明 |
| S006 | Intent table | P0-P3 意图表是否完整 |
| S007 | Sub-agent prompts | 子 Agent prompt 模板是否定义 |
| S008 | Flow integrity | 流程完整性约束是否声明 |
| S009 | Sub-task routing | 子任务路由是否定义 |
| S010 | Cross-review | 交叉审查机制是否定义 |
| S011 | Shared memory | 共享记忆层是否定义 |
| S012 | Anti-packaging | 反包装约束是否定义 |
| S013 | Honesty dimension | 实现诚实度检查类是否定义 |
| S014 | Follow-up check | 可追问性检查是否定义 |

#### 内容质量检查项（Layer 2）

| ID | 检查项 | 严重程度 | 说明 |
|----|--------|---------|------|
| Q001 | 教育背景 | error | 是否包含学校、专业等信息 |
| Q002 | 项目经历 | error | 是否有具体项目描述 |
| Q003 | 技能列表 | warning | 是否列出技术栈 |
| Q004 | STAR 结构 | warning | 是否包含情境 / 行动 / 结果 |
| Q005 | 量化成果 | suggestion | 是否有数据支撑 |
| Q006 | 表达优化 | suggestion | 是否存在弱表达 |
| Q007 | 篇幅 | warning | 是否在 1500-2500 字范围内 |
| Q008 | 排版格式 | suggestion | 中英混排是否规范 |
| Q009 | 个人亮点 | suggestion | 是否有 GitHub / 博客 / 竞赛等 |

## 设计原则

### 四条红线

| 红线 | 说明 |
|------|------|
| 零编造 | 所有内容必须基于客观真源，不猜测、不补齐 |
| 简历正直 | 不帮助用户虚构、夸大经历，「参与」不能写成「主导」 |
| 信息密度 | 不堆砌技术细节，确保 30 秒能抓住重点 |
| 面试官视角 | 始终站在面试官角度审查简历 |

### 反包装约束

防止术语升级，确保简历描述与实际实现匹配：

- 「文件读写」不升级为「存储层」
- 「条件分支」不升级为「动态编排」
- 「函数调用」不升级为「Agent 间通信」
- 「变量传递」不升级为「共享记忆」
- 「if-else」不升级为「策略引擎」

### 方向偏差检测

当质保发现大量问题（≥ 3 个 [必须修复] 或 [包装过度]）时，系统会判断初稿方向偏了，此时会重新生成而非逐个修补。

## 依赖

- **Python 3.x** — 用于 state_manager.py 和 eval_runner.py，无第三方包依赖
- **Claude Code** — 需要 Agent 工具支持，用于质量保证阶段的子 Agent 调度

## 致谢

- 架构模式参考 [tencent-campus-recruit](https://github.com/nicepkg/tencent-campus-recruit)

## 许可证

[MIT](./LICENSE)
