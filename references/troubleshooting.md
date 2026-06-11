# 常见问题处理

> 本文件是 resume-craft Skill 的排障指南。当脚本执行失败或遇到异常时参考。

---

## state_manager.py 问题

### 问题：`python scripts/state_manager.py init` 报错 "No such file"

**原因**：不在 Skill 根目录下执行。

**解决**：
```bash
cd <skill-root-directory>
python scripts/state_manager.py init
```

### 问题：`update` 命令后 `show` 看不到更新

**原因**：`--value` 参数包含特殊字符（如换行符、引号）导致解析失败。

**解决**：
- 确保值用双引号包裹
- 如果值包含引号，用转义：`--value "他说\"你好\""`
- 如果值很长（如完整简历），建议先写入临时文件，再用脚本读取

### 问题：`resume-state.json` 文件损坏

**原因**：手动编辑或写入中断导致 JSON 格式错误。

**解决**：
```bash
python scripts/state_manager.py reset
python scripts/state_manager.py init
```

---

## eval_runner.py 问题

### 问题：`python evals/eval_runner.py structure` 报错 "SKILL.md not found"

**原因**：不在 Skill 根目录下执行，eval_runner.py 找不到 SKILL.md。

**解决**：
```bash
cd <skill-root-directory>
python evals/eval_runner.py structure
```

### 问题：quality 检查报错 "No such file"

**原因**：传入的文件路径不存在。

**解决**：
- 检查文件路径是否正确
- 使用绝对路径：`python evals/eval_runner.py quality /path/to/resume.md`
- 或直接传文本：`python evals/eval_runner.py quality "简历文本内容"`

---

## SKILL.md 执行问题

### 问题：Claude 没有按模块路由执行

**原因**：用户意图不明确，Claude 可能跳过意图识别直接回答。

**解决**：在对话开头明确说"帮我写简历"（模块一）、"针对JD优化"（模块二）、"诊断简历"（模块三）、"更新简历"（模块四）。

### 问题：子Agent没有被 spawn

**原因**：当前环境可能不支持 Agent 工具（如 API 配额已满）。

**解决**：
- 如果 Agent 工具不可用，质量检查可以在模块内直接执行（不 spawn 子Agent）
- 效果略差（上下文污染），但核心功能不受影响

### 问题：引导提问太慢（7个问题太多）

**原因**：用户想快速出初稿，不想走完整流程。

**解决**：
- 用户可以说"跳过提问，我直接给你信息"
- 或者一次性提供所有信息（教育背景+项目+技能）
- Claude 会跳过引导提问，直接进入内容生成

---

## References 加载问题

### 问题：Claude 没有加载对应的 reference 文件

**原因**：references/ 目录不在 Skill 根目录下，或文件名不匹配。

**解决**：
- 确认 `references/` 目录与 `SKILL.md` 在同一级
- 确认文件名与 SKILL.md 中 References 读取规则表一致
- 文件名区分大小写

---

## 通用排障原则

1. **先确认目录**：所有命令在 Skill 根目录下执行
2. **先确认 Python**：`python --version` 确保 Python 3.x 可用
3. **先 reset 再 init**：状态文件损坏时，reset 后重新初始化
4. **查看 git log**：查看最近的变更记录，确认文件是否被修改
