# resume-craft Skill 设计规格

## 概述

基于 tencent-campus-recruit 的架构模式，构建一个面向校招场景的简历制作 Skill。采用功能模块模式组织，核心流程由 Claude 原生能力完成，质量保证阶段使用真子Agent获得独立视角。

## 决策记录

| 决策 | 选择 | 理由 |
|------|------|------|
| Agent 架构 | 混合模式 | 核心流程用模块路由（简单可靠），质量保证用真子Agent（独立视角避免上下文污染） |
| 脚本层 | 最小脚本集 | 只做 Claude 做不好的事（状态管理、eval 运行），不做 JD 解析/关键词匹配 |
| Evals | 两层 | 结构完整性（秒级）+ API 调用规则检查（分钟级） |
| 初始范围 | 校招优先 | 先覆盖校招/应届生场景，后续扩展到社招 |
| 模块组织 | 功能模块 | 按用户意图组织（从零写/JD优化/诊断/更新），与 tencent 一致 |
| 输出格式 | Markdown | 基础格式，易于编辑和版本控制 |

## 上一版问题（本版已解决）

| 旧版问题 | 本版解决方案 |
|----------|------------|
| 12个"Agent"是虚假宣传（只是 prompt 段落标题） | 不称"Agent"，用"模块"；质量保证阶段用真子Agent |
| 3个 Python 脚本是玩具（硬编码关键词） | 砍掉 JD 解析/关键词匹配/排版检查脚本，Claude 原生更强 |
| resume-state.json 从未实现 | 新增 state_manager.py，提供 init/show/update/history 命令 |
| Evals 不可执行 | 两层 eval：结构完整性 + API 调用规则检查 |
| Reference 太薄（30-50行常识） | 6个文档，每个 80-200行，包含真正的领域专家知识 |
| 设计复杂度是实现的10倍 | SKILL.md ~120行，脚本只有2个 |

## 架构设计

### 整体架构

```
用户输入
│
▼
┌─────────────────────────────────────────────┐
│  SKILL.md（入口 + 意图路由 + 4个功能模块）     │
│  - 意图识别：if-else 分发                     │
│  - 模块1: 从零写简历（全流程）                  │
│  - 模块2: 针对JD优化                          │
│  - 模块3: 简历诊断（spawn 子Agent）            │
│  - 模块4: 增量更新                            │
│  - 四条红线 + 输出风格约束                      │
└───────┬─────────────────┬───────────────────┘
        │                 │
  模块内直接执行      spawn 子Agent（质量保证）
  (Claude 原生能力)    (独立上下文)
        │                 │
        ▼                 ▼
  references/          scripts/
  (6个领域知识文档)     state_manager.py
                       evals/eval_runner.py
```

### 目录结构

```
D:\简历skill_2\
├── SKILL.md                          # 入口：意图路由 + 4个功能模块 + 约束
├── README.md                         # 简洁说明
│
├── references/                       # 领域知识（按需加载）
│   ├── interaction-rules.md          # 交互规则和话术（~150行）
│   ├── resume-guide.md               # 简历制作方法论（~200行）
│   ├── campus-templates.md           # 校招简历模板（~150行）
│   ├── interviewer-perspective.md    # 面试官视角审查（~120行）
│   ├── verification-rules.md         # 事实核查规则（~100行）
│   └── chinese-format.md             # 中文排版规范（~80行）
│
├── scripts/                          # 工具脚本
│   └── state_manager.py              # 状态管理 CRUD
│
└── evals/                            # 质量检查
    ├── eval_runner.py                # 两层 eval 运行器
    └── test_cases.json               # 测试用例
```

## 功能模块设计

### 模块一：从零写简历（P0 全流程）

**触发词**：帮我写简历、从零开始、还没有简历

**流程**：

1. **引导提问**
   - 每次一个问题，优先选择题（2-4选项）
   - 提问顺序：目标岗位/行业 → 教育背景 → 项目经历 → 实习经历 → 技术栈 → 成果亮点 → 可验证信号
   - 校招场景默认引导到腾讯校招方向
   - 参考：`references/interaction-rules.md`

2. **真源解析**（可选，用户有文件时）
   - 代码文件 → 提取项目名、技术栈、功能描述
   - 文档/PDF → 提取关键信息
   - URL → WebFetch 获取内容
   - 工具：Claude 原生 Read/Glob/Grep/WebFetch

3. **JD解析**（可选，用户有目标JD时）
   - Claude 原生能力解析
   - 提取：硬性条件、软性素质、加分项、技术栈
   - 输出结构化 JD（类似 tencent 的 structured_jd）

4. **内容生成**
   - 选择模板（校招技术岗/产品岗/设计岗/通用）
   - 参考：`references/campus-templates.md`
   - 生成 Markdown 初稿
   - 使用 STAR 结构描述项目经历
   - 量化成果描述

5. **质量保证**（spawn 子Agent，并行执行）
   - 子Agent A：事实核查
     - 对比简历内容 vs 真源数据
     - 标注：[事实错误] / [疑似夸大] / [信息缺失]
     - 参考：`references/verification-rules.md`
   - 子Agent B：面试官盲审
     - 30秒规则、STAR结构、量化成果、信息密度
     - 分级标注：[必须修复] / [建议修改] / [仅供参考]
     - 参考：`references/interviewer-perspective.md`
   - 有问题 → 返回对应阶段修正

6. **优化输出**
   - 精简冗余（控制1500-2500字）
   - 中英混排规范（参考 `references/chinese-format.md`）
   - 排版一致性

7. **持久化**
   - 运行 `python scripts/state_manager.py update --field resume_draft --value "<简历内容>"`
   - 记录版本历史

### 模块二：针对JD优化（P1 部分流程）

**触发词**：针对JD优化、匹配岗位、改简历

**流程**：

1. **获取简历** — 用户粘贴 / 文件 / 从状态读取
2. **JD解析** — Claude 原生，输出结构化 JD
3. **差距分析**
   - 匹配技能 vs 缺失技能
   - 严重程度分级：required / recommended / nice_to_have
   - 优化建议
4. **简历调整**
   - 补充缺失关键词（基于真实经历，不编造）
   - 调整侧重点，突出匹配技能
5. **质量保证** — 同模块一的子Agent流程
6. **输出** — 优化后简历 + 变更说明

### 模块三：简历诊断（P2）

**触发词**：诊断简历、看看问题、简历点评

**流程**：

1. **获取简历** — 用户粘贴 / 文件
2. **spawn 面试官盲审子Agent**
   - 独立上下文，不带对话历史
   - 按 `references/interviewer-perspective.md` 审查清单逐项检查
   - 输出：分级问题列表 + 整体评分 + 改进建议
3. **汇总反馈**
   - 先肯定亮点
   - 按 [必须修复] > [建议修改] > [仅供参考] 排序
   - 给出具体可执行建议
4. **询问** — 是否需要自动修复部分问题

### 模块四：增量更新（P3）

**触发词**：更新简历、改一下、修改项目经历

**流程**：

1. **读取当前简历** — 从状态或用户粘贴
2. **执行增量修改** — 只改用户指定部分
3. **一致性检查**
   - 修改后与其他部分是否矛盾
   - 时间线是否合理
   - 技能描述是否一致
4. **diff 展示** — Markdown 格式展示变更（新增/删除/修改）
5. **版本记录** — 写入状态文件 history 字段

## 四条红线

1. **零编造**：所有内容必须基于客观真源，不猜测、不补齐
2. **简历正直**：不帮助用户虚构、夸大项目、实习、证书、成果数据；只在真实经历基础上优化表达
3. **信息密度**：不堆砌技术细节，控制信息密度；站在面试官角度，确保30秒能抓住重点
4. **面试官视角**：始终站在面试官角度审查简历，确保易读性

## 状态管理

### state_manager.py 命令

```bash
python scripts/state_manager.py init                                    # 初始化
python scripts/state_manager.py show                                    # 查看
python scripts/state_manager.py update --field <path> --value <value>   # 更新
python scripts/state_manager.py append --field <path> --value <value>   # 追加到数组
python scripts/state_manager.py history                                 # 变更历史
python scripts/state_manager.py reset                                   # 重置
```

### resume-state.json 结构

```json
{
  "version": "1.0",
  "module": "intake|generating|verifying|optimizing|done",
  "user_profile": {
    "name": "",
    "target_position": "",
    "target_company": "",
    "education": [],
    "skills": [],
    "projects": [],
    "work_experience": [],
    "achievements": [],
    "verification_signals": []
  },
  "jd": {
    "raw_text": "",
    "structured": {
      "hard_requirements": [],
      "soft_skills": [],
      "nice_to_have": [],
      "tech_stack": []
    }
  },
  "truth_sources": [],
  "resume_draft": "",
  "verification_results": [],
  "history": []
}
```

## References 设计

| 文件 | 核心内容 | 行数 |
|------|---------|------|
| `interaction-rules.md` | 意图识别规则、选项式追问模板、输出风格约束、兜底话术 | ~150 |
| `resume-guide.md` | STAR法则详解、常见误区、表达优化表、分方向侧重建议 | ~200 |
| `campus-templates.md` | 校招技术岗/产品岗/设计岗/市场岗/通用岗的 Markdown 模板 | ~150 |
| `interviewer-perspective.md` | 30秒规则、审查清单（格式/内容/表达）、分级标注标准 | ~120 |
| `verification-rules.md` | 四维核查（经历/项目/技能/教育）、交叉验证、逻辑检查 | ~100 |
| `chinese-format.md` | 中英混排规则、标点规范、数字格式、Markdown格式标准 | ~80 |

## Evals 设计

### 第一层：结构完整性（秒级）

检查项：
- [ ] SKILL.md 存在且有正确的 frontmatter（name, description）
- [ ] 6个 references/ 文件全部存在且非空
- [ ] scripts/state_manager.py 存在且可执行
- [ ] evals/eval_runner.py 存在且可执行
- [ ] SKILL.md 中包含4个功能模块（模块一/二/三/四）
- [ ] SKILL.md 中明确声明四条红线
- [ ] SKILL.md 中有意图识别表（P0-P3）

### 第二层：API 调用 + 规则检查（分钟级）

测试用例（`evals/test_cases.json`）包含：
- 用例1：校招技术岗从零写简历
- 用例2：针对JD优化已有简历
- 用例3：简历诊断
- 用例4：增量更新

每个用例检查：
- STAR 结构完整性（情境/行动/结果要素）
- 量化数据存在性（数字/百分比/规模）
- 信息密度（1500-2500字范围）
- 真实性（不包含真源中没有的编造内容）
- 格式规范（中英混排、Markdown 格式）

## 痛点覆盖矩阵

| 痛点 | 解决方式 | 对应模块 |
|------|---------|---------|
| 1. 口述缺失信息多 | 每次一个问题，选择题引导 | 模块一.1 |
| 2. 误读客观真源 | 真源解析 + 事实核查子Agent | 模块一.2 + 一.5 |
| 3. 漏读 | 引导提问清单覆盖完整 | 模块一.1 |
| 4. 修改简历麻烦 | 增量更新 + diff展示 | 模块四 |
| 5. 对应JD改简历麻烦 | JD解析 + 差距分析 + 自动调整 | 模块二 |
| 6. 不美观易读 | 中文排版规范 + 面试官盲审 | 模块一.6 + 一.5 |
| 7. 细节堆砌 | 信息密度控制 + 面试官30秒规则 | 模块一.5 + 一.6 |
| 8. 行业格式差异 | 校招各岗位模板 | references/campus-templates |
| 9. 缺乏量化成果 | 引导量化描述（STAR的R） | 模块一.4 |
| 10. 技术栈泛化/细节 | 分层描述（精通/熟练/了解） | 模块一.4 |
| 11. 缺乏STAR结构 | 强制STAR结构生成 | 模块一.4 |
| 12. 简历长度控制 | 1500-2500字约束 | 模块一.6 |
| 13. 关键词匹配度低 | JD差距分析 + 关键词补充 | 模块二 |
| 14. 缺乏用户价值 | 引导提问中包含"解决了什么问题" | 模块一.1 |
| 15. 缺乏技术选型 | 引导提问中包含"为什么选这个技术" | 模块一.1 |
| 16. 缺乏可验证信号 | 引导提问中收集 GitHub/博客/竞赛 | 模块一.1 |
| 17. 排版不一致 | 中文排版规范 + 面试官审查 | 模块一.6 + 一.5 |
| 18. 版本混乱 | 状态管理 + history 字段 | state_manager.py |
| 19. 多份简历 | 模块二支持针对不同JD生成 | 模块二 |
| 20. 无法追踪变更 | diff展示 + 版本记录 | 模块四 + state_manager.py |

## 实现优先级

### P0：核心骨架（第一批实现）

1. SKILL.md（意图路由 + 4个模块 + 约束）
2. references/interaction-rules.md
3. references/resume-guide.md
4. scripts/state_manager.py

### P1：模块实现

5. 模块一完整流程（引导提问 → 内容生成 → 输出）
6. references/campus-templates.md
7. 模块三（简历诊断，spawn 子Agent）

### P2：质量保证

8. 模块一的质量保证子Agent（事实核查 + 面试官盲审）
9. references/interviewer-perspective.md
10. references/verification-rules.md

### P3：增强功能

11. 模块二（针对JD优化）
12. 模块四（增量更新）
13. references/chinese-format.md
14. evals/eval_runner.py + test_cases.json
15. README.md
