# resume-craft

面向校招场景的简历制作 Skill。基于 tencent-campus-recruit 架构模式，采用功能模块组织 + 混合Agent模式。

## 功能

- **从零写简历** — 引导提问 → 内容生成 → 质量保证 → 优化输出
- **针对JD优化** — JD解析 → 差距分析 → 简历调整
- **简历诊断** — 面试官盲审，分级反馈
- **增量更新** — 只改指定部分，diff展示

## 目录结构

```
├── SKILL.md                          # 入口：意图路由 + 4个功能模块
├── references/                       # 领域知识（按需加载）
│   ├── interaction-rules.md          # 交互规则和话术
│   ├── resume-guide.md               # 简历制作方法论
│   ├── campus-templates.md           # 校招简历模板
│   ├── interviewer-perspective.md    # 面试官视角审查
│   ├── verification-rules.md         # 事实核查规则
│   └── chinese-format.md             # 中文排版规范
├── scripts/
│   └── state_manager.py              # 状态管理
└── evals/
    ├── eval_runner.py                # 两层 eval
    └── test_cases.json               # 测试用例
```

## 使用

在 Claude Code 中触发 `/resume-craft`，或直接说"帮我写简历"。

### 状态管理

```bash
python scripts/state_manager.py init
python scripts/state_manager.py show
python scripts/state_manager.py update --field user_profile.name --value "张三"
python scripts/state_manager.py history
python scripts/state_manager.py reset
```

### 质量检查

```bash
python evals/eval_runner.py structure   # 结构完整性（秒级）
python evals/eval_runner.py quality     # 测试用例验证
python evals/eval_runner.py all         # 全部
```

## 四条红线

1. **零编造** — 所有内容基于客观真源
2. **简历正直** — 不帮助虚构、夸大
3. **信息密度** — 控制密度，30秒抓住重点
4. **面试官视角** — 始终站在面试官角度审查
