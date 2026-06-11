# resume-craft

面向校招场景的简历制作 Skill。基于 tencent-campus-recruit 架构模式，采用功能模块组织 + 混合Agent模式。

## 功能

- **从零写简历** — 引导提问 → 内容生成 → 质量保证 → 优化输出
- **针对JD优化** — JD解析 → 差距分析 → 简历调整
- **简历诊断** — 面试官盲审，分级反馈
- **增量更新** — 只改指定部分，diff展示

## 快速开始

### 在 Claude Code 中使用

1. 将本目录放到 `.claude/skills/resume-craft/` 下
2. 在 Claude Code 中说"帮我写简历"即可触发

### 首次使用示例

```
用户：帮我写简历

Claude：我需要了解更多信息来帮助你。请选择：

1. **从零写简历** — 你还没有简历，需要从头开始
2. **针对JD优化** — 你有简历，想针对某个岗位优化
3. **简历诊断** — 你有简历，想看看有什么问题
4. **增量更新** — 你想修改简历中的某些内容

用户：1

Claude：你想投哪类岗位？
1. 技术岗（后端/前端/算法/测试/运维）
2. 产品岗（产品经理/产品运营）
3. 设计岗（UI/UX/交互）
4. 市场/职能岗

...（逐步引导，每次一个问题）
```

### 针对JD优化示例

```
用户：针对这个JD优化我的简历

[粘贴 JD 文本]

Claude：请提供你的当前简历（粘贴文本或提供文件路径）。

用户：[粘贴简历]

Claude：## 简历-JD 差距分析

### 匹配技能
- Python：简历中有在线商城项目经验佐证
- Redis：简历中有缓存优化经验佐证

### 缺失技能
- **required**：Docker
  → 风险：JD 明确要求，缺失可能导致被筛掉
  → 建议：如有相关经验，补充描述

...（差距分析 → 调整 → 质量检查 → 输出）
```

### 诊断简历示例

```
用户：诊断简历

Claude：请提供你的简历（粘贴文本或提供文件路径）。

用户：[粘贴简历]

Claude：## 简历审查报告

### 整体评分：6/10

### 亮点
- 项目经历有量化数据
- 技术栈分层清晰

### 问题清单

**[必须修复]**
1. 缺少教育背景信息 → 建议补充学校、专业、毕业时间

**[建议修改]**
1. "负责后端开发"描述过于空泛 → 建议用 STAR 结构重写
...（诊断报告 → 询问是否修复）
```

## 目录结构

```
├── SKILL.md                          # 入口：意图路由 + 4个功能模块
├── README.md                         # 本文件
├── references/                       # 领域知识（按需加载）
│   ├── interaction-rules.md          # 交互规则和话术
│   ├── resume-guide.md               # 简历制作方法论（面试官视角）
│   ├── campus-templates.md           # 校招简历模板（5种岗位）
│   ├── interviewer-perspective.md    # 面试官视角审查指南
│   ├── verification-rules.md         # 事实核查规则
│   ├── chinese-format.md             # 中文排版规范
│   ├── job-database.md               # 校招方向面试官考察视角
│   └── troubleshooting.md            # 常见问题处理
├── scripts/
│   └── state_manager.py              # 状态管理
└── evals/
    ├── eval_runner.py                # 两层 eval（结构+质量）
    └── test_cases.json               # 测试用例
```

## 依赖

- Python 3.x（用于 state_manager.py 和 eval_runner.py）
- Claude Code（Agent 工具用于子Agent调度）

无第三方 Python 包依赖。

## 使用脚本

### 状态管理

```bash
# 初始化
python scripts/state_manager.py init

# 查看当前状态
python scripts/state_manager.py show

# 更新字段
python scripts/state_manager.py update --field user_profile.name --value "张三"
python scripts/state_manager.py update --field resume_draft --value "## 简历内容..."

# 追加到数组
python scripts/state_manager.py append --field truth_sources --value "GitHub: github.com/test"

# 查看变更历史
python scripts/state_manager.py history

# 重置
python scripts/state_manager.py reset
```

### 质量检查

```bash
# 第一层：结构完整性检查（秒级）
python evals/eval_runner.py structure

# 第二层：简历内容质量检查
python evals/eval_runner.py quality "简历文本内容"
python evals/eval_runner.py quality /path/to/resume.md

# 全部检查
python evals/eval_runner.py all "简历文本内容"
```

### 质量检查项（Layer 2）

| ID | 检查项 | 严重程度 |
|----|--------|---------|
| Q001 | 教育背景 | error |
| Q002 | 项目经历 | error |
| Q003 | 技能列表 | warning |
| Q004 | STAR 结构 | warning |
| Q005 | 量化成果 | suggestion |
| Q006 | 表达优化 | suggestion |
| Q007 | 篇幅（1500-2500字） | warning |
| Q008 | 排版格式 | suggestion |
| Q009 | 个人亮点 | suggestion |

## 四条红线

1. **零编造** — 所有内容基于客观真源
2. **简历正直** — 不帮助虚构、夸大
3. **信息密度** — 控制密度，30秒抓住重点
4. **面试官视角** — 始终站在面试官角度审查

## 架构说明

- **SKILL.md** 作为入口，意图路由 → 4个功能模块
- **核心流程**由 Claude 原生能力完成（引导提问、内容生成、JD解析）
- **质量保证**使用真子Agent（事实核查 + 面试官盲审），获得独立视角
- **references/** 提供领域专家知识，按需加载
- **scripts/** 只做 Claude 做不好的事（状态管理）
- **evals/** 提供可执行的质量检查
