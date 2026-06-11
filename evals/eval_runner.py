#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
resume-craft Eval 运行器
==========================================

两层 eval：
  Layer 1 (structure)：SKILL.md 结构完整性检查，秒级
  Layer 2 (quality)：简历内容质量检查（STAR/量化/表达/格式），秒级

用法:
    python evals/eval_runner.py structure
    python evals/eval_runner.py quality <简历文本或文件路径>
    python evals/eval_runner.py all <简历文本或文件路径>
"""

import re
import subprocess
import sys
from pathlib import Path


def configure_output_encoding() -> None:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            try:
                reconfigure(encoding="utf-8", errors="replace")
            except Exception:
                pass


configure_output_encoding()

BASE_DIR = Path(__file__).resolve().parent.parent
SKILL_FILE = BASE_DIR / "SKILL.md"
REFERENCES_DIR = BASE_DIR / "references"
SCRIPTS_DIR = BASE_DIR / "scripts"
EVALS_DIR = BASE_DIR / "evals"

REQUIRED_REFERENCES = [
    "interaction-rules.md",
    "resume-guide.md",
    "campus-templates.md",
    "interviewer-perspective.md",
    "verification-rules.md",
    "chinese-format.md",
    "job-database.md",
]


# =============================================================================
# Layer 1: Structure Integrity
# =============================================================================

def check_skill_frontmatter() -> dict:
    if not SKILL_FILE.exists():
        return {"id": "S001", "name": "SKILL.md exists", "passed": False, "message": "SKILL.md not found"}
    content = SKILL_FILE.read_text(encoding="utf-8")
    has_name = bool(re.search(r"^name:\s*resume-craft", content, re.MULTILINE))
    has_desc = bool(re.search(r"^description:", content, re.MULTILINE))
    if has_name and has_desc:
        return {"id": "S001", "name": "SKILL.md frontmatter", "passed": True, "message": "OK"}
    missing = []
    if not has_name: missing.append("name")
    if not has_desc: missing.append("description")
    return {"id": "S001", "name": "SKILL.md frontmatter", "passed": False, "message": f"missing: {', '.join(missing)}"}


def check_references_exist() -> dict:
    missing = []
    empty = []
    for ref in REQUIRED_REFERENCES:
        path = REFERENCES_DIR / ref
        if not path.exists():
            missing.append(ref)
        elif path.stat().st_size < 100:
            empty.append(ref)
    if not missing and not empty:
        return {"id": "S002", "name": "References", "passed": True, "message": f"All {len(REQUIRED_REFERENCES)} references OK"}
    problems = []
    if missing: problems.append(f"missing: {', '.join(missing)}")
    if empty: problems.append(f"too short: {', '.join(empty)}")
    return {"id": "S002", "name": "References", "passed": False, "message": "; ".join(problems)}


def check_state_manager() -> dict:
    path = SCRIPTS_DIR / "state_manager.py"
    if not path.exists():
        return {"id": "S003", "name": "state_manager.py", "passed": False, "message": "not found"}
    try:
        result = subprocess.run([sys.executable, str(path), "--help"], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            return {"id": "S003", "name": "state_manager.py", "passed": True, "message": "executable"}
        return {"id": "S003", "name": "state_manager.py", "passed": False, "message": f"exit {result.returncode}"}
    except Exception as e:
        return {"id": "S003", "name": "state_manager.py", "passed": False, "message": str(e)[:80]}


def check_modules_in_skill() -> dict:
    if not SKILL_FILE.exists():
        return {"id": "S004", "name": "Modules", "passed": False, "message": "SKILL.md not found"}
    content = SKILL_FILE.read_text(encoding="utf-8")
    modules = ["模块一", "模块二", "模块三", "模块四"]
    missing = [m for m in modules if m not in content]
    if not missing:
        return {"id": "S004", "name": "Modules", "passed": True, "message": "All 4 modules present"}
    return {"id": "S004", "name": "Modules", "passed": False, "message": f"missing: {', '.join(missing)}"}


def check_red_lines() -> dict:
    if not SKILL_FILE.exists():
        return {"id": "S005", "name": "Red lines", "passed": False, "message": "SKILL.md not found"}
    content = SKILL_FILE.read_text(encoding="utf-8")
    lines = ["零编造", "简历正直", "信息密度", "面试官视角"]
    missing = [l for l in lines if l not in content]
    if not missing:
        return {"id": "S005", "name": "Red lines", "passed": True, "message": "All 4 red lines declared"}
    return {"id": "S005", "name": "Red lines", "passed": False, "message": f"missing: {', '.join(missing)}"}


def check_intent_table() -> dict:
    if not SKILL_FILE.exists():
        return {"id": "S006", "name": "Intent table", "passed": False, "message": "SKILL.md not found"}
    content = SKILL_FILE.read_text(encoding="utf-8")
    priorities = ["P0", "P1", "P2", "P3"]
    missing = [p for p in priorities if p not in content]
    if not missing:
        return {"id": "S006", "name": "Intent table", "passed": True, "message": "P0-P3 present"}
    return {"id": "S006", "name": "Intent table", "passed": False, "message": f"missing: {', '.join(missing)}"}


def check_subagent_prompts() -> dict:
    if not SKILL_FILE.exists():
        return {"id": "S007", "name": "Sub-agent prompts", "passed": False, "message": "SKILL.md not found"}
    content = SKILL_FILE.read_text(encoding="utf-8")
    has_agent_tool = "Agent 工具" in content or "Agent tool" in content
    has_prompt_template = "prompt 如下" in content or "prompt:" in content.lower()
    if has_agent_tool and has_prompt_template:
        return {"id": "S007", "name": "Sub-agent prompts", "passed": True, "message": "Agent tool + prompt templates present"}
    missing = []
    if not has_agent_tool: missing.append("Agent tool reference")
    if not has_prompt_template: missing.append("prompt template")
    return {"id": "S007", "name": "Sub-agent prompts", "passed": False, "message": f"missing: {', '.join(missing)}"}


def run_structure_checks() -> dict:
    checks = [
        check_skill_frontmatter(),
        check_references_exist(),
        check_state_manager(),
        check_modules_in_skill(),
        check_red_lines(),
        check_intent_table(),
        check_subagent_prompts(),
    ]
    passed = sum(1 for c in checks if c["passed"])
    return {
        "layer": "structure",
        "total": len(checks),
        "passed": passed,
        "failed": len(checks) - passed,
        "score": round(passed / len(checks) * 100),
        "details": checks,
    }


# =============================================================================
# Layer 2: Resume Content Quality Check
# (参考 tencent-campus-recruit 的 resume_checker.py 模式)
# =============================================================================

def check_education(text: str) -> dict:
    """Q001: 检查是否包含教育背景"""
    keywords = ["大学", "学院", "本科", "硕士", "博士", "学士", "研究生", "毕业", "专业", "GPA", "学历"]
    found = any(k in text for k in keywords)
    return {
        "id": "Q001", "name": "教育背景", "severity": "error",
        "passed": found,
        "message": "[OK] 包含教育背景信息" if found else "[ERROR] 未检测到教育背景，建议补充学校、专业、毕业时间"
    }


def check_project(text: str) -> dict:
    """Q002: 检查是否包含项目经历"""
    keywords = ["项目", "开发", "设计", "实现", "负责", "参与", "搭建", "研发", "完成"]
    found = sum(1 for k in keywords if k in text) >= 2
    return {
        "id": "Q002", "name": "项目经历", "severity": "error",
        "passed": found,
        "message": "[OK] 包含项目经历描述" if found else "[ERROR] 项目经历不够突出，建议用STAR法则详细描述2-3个核心项目"
    }


def check_skills(text: str) -> dict:
    """Q003: 检查是否包含技能列表"""
    keywords = ["技能", "熟悉", "精通", "掌握", "熟练", "了解", "技术栈", "工具", "语言"]
    found = any(k in text for k in keywords)
    return {
        "id": "Q003", "name": "技能列表", "severity": "warning",
        "passed": found,
        "message": "[OK] 包含技能描述" if found else "[WARN] 建议添加技能列表，明确列出掌握的技术/工具"
    }


def check_star(text: str) -> dict:
    """Q004: 检查项目是否使用 STAR 结构"""
    has_situation = any(k in text for k in ["背景", "问题", "需求", "面临", "挑战", "场景", "痛点"])
    has_action = any(k in text for k in ["设计", "实现", "开发", "优化", "搭建", "采用", "使用", "通过"])
    has_result = any(k in text for k in ["提升", "增长", "降低", "减少", "达到", "实现了", "效果", "%", "倍"])
    score = sum([has_situation, has_action, has_result])
    if score >= 3:
        msg = "[OK] 项目描述具有STAR结构要素"
    elif score >= 2:
        msg = "[WARN] 部分使用了STAR结构，建议补充缺失的要素（情境/行动/结果）"
    else:
        msg = "[WARN] 建议使用STAR法则：情境(S)→任务(T)→行动(A)→结果(R)"
    return {"id": "Q004", "name": "STAR结构", "severity": "warning", "passed": score >= 2, "message": msg}


def check_quantified(text: str) -> dict:
    """Q005: 检查是否有量化成果"""
    patterns = [r'\d+%', r'\d+倍', r'\d+万', r'\d+人', r'提升\d+', r'增长\d+', r'减少\d+', r'降低\d+', r'覆盖\d+',
                r'\d+ms', r'\d+\s*QPS', r'\d+\s*并发', r'\d+\s*GB', r'\d+\s*TB']
    found = any(re.search(p, text) for p in patterns)
    return {
        "id": "Q005", "name": "量化成果", "severity": "suggestion",
        "passed": found,
        "message": "[OK] 包含量化数据" if found else "[TIP] 建议添加量化成果，如'提升XX%'、'覆盖XX万用户'、'响应时间从Xms降至Yms'"
    }


def check_weak_verbs(text: str) -> dict:
    """Q006: 检查常见弱表达"""
    weak_patterns = {
        "参与了": "建议改为具体职责，如'负责XX模块的设计与实现'",
        "协助": "建议明确你的独立贡献",
        "沟通能力强": "建议用具体事例佐证",
        "学习能力强": "建议用具体学习经历佐证",
        "熟悉编程": "过于泛化，建议列出具体技术栈",
    }
    issues = [f"「{p}」→ {s}" for p, s in weak_patterns.items() if p in text]
    if issues:
        return {"id": "Q006", "name": "表达优化", "severity": "suggestion", "passed": False,
                "message": "[TIP] 发现可优化的表达：\n" + "\n".join(f"  - {i}" for i in issues)}
    return {"id": "Q006", "name": "表达优化", "severity": "suggestion", "passed": True,
            "message": "[OK] 未发现常见弱表达"}


def check_length(text: str) -> dict:
    """Q007: 检查篇幅"""
    n = len(text)
    if n < 200:
        return {"id": "Q007", "name": "篇幅", "severity": "warning", "passed": False,
                "message": f"[WARN] 内容偏少（{n}字），建议补充更多项目经历"}
    if n > 3000:
        return {"id": "Q007", "name": "篇幅", "severity": "warning", "passed": False,
                "message": f"[WARN] 内容偏长（{n}字），建议精简至1500-2500字"}
    return {"id": "Q007", "name": "篇幅", "severity": "warning", "passed": True,
            "message": f"[OK] 长度适中（{n}字）"}


def check_format(text: str) -> dict:
    """Q008: 检查中英混排格式"""
    issues = []
    # 中英文之间缺少空格
    if re.search(r'[一-鿿][a-zA-Z]', text):
        issues.append("中英文之间缺少空格")
    if re.search(r'[a-zA-Z][一-鿿]', text):
        issues.append("中英文之间缺少空格")
    # 中文语境使用英文标点
    if re.search(r'[一-鿿],\s*[一-鿿]', text):
        issues.append("中文语境使用了英文逗号")
    if issues:
        return {"id": "Q008", "name": "排版格式", "severity": "suggestion", "passed": False,
                "message": f"[TIP] 排版问题：{'、'.join(set(issues))}。参考 references/chinese-format.md"}
    return {"id": "Q008", "name": "排版格式", "severity": "suggestion", "passed": True,
            "message": "[OK] 排版格式良好"}


def check_personal_highlights(text: str) -> dict:
    """Q009: 检查是否有个人亮点"""
    keywords = ["GitHub", "github", "博客", "blog", "开源", "竞赛", "获奖", "论文", "专利",
                "ACM", "黑客马拉松", "hackathon", "作品集", "portfolio"]
    found = any(k in text for k in keywords)
    return {
        "id": "Q009", "name": "个人亮点", "severity": "suggestion",
        "passed": found,
        "message": "[OK] 包含个人亮点" if found else "[TIP] 建议补充个人亮点：GitHub、技术博客、竞赛成绩、开源贡献等"
    }


def check_resume_quality(text: str) -> dict:
    checks = [
        check_education(text),
        check_project(text),
        check_skills(text),
        check_star(text),
        check_quantified(text),
        check_weak_verbs(text),
        check_length(text),
        check_format(text),
        check_personal_highlights(text),
    ]
    passed = sum(1 for c in checks if c["passed"])
    errors = sum(1 for c in checks if not c["passed"] and c["severity"] == "error")
    warnings = sum(1 for c in checks if not c["passed"] and c["severity"] == "warning")
    suggestions = sum(1 for c in checks if not c["passed"] and c["severity"] == "suggestion")
    return {
        "layer": "quality",
        "total": len(checks),
        "passed": passed,
        "failed": len(checks) - passed,
        "score": round(passed / len(checks) * 100),
        "errors": errors,
        "warnings": warnings,
        "suggestions": suggestions,
        "details": checks,
    }


# =============================================================================
# CLI
# =============================================================================

def print_report(result: dict) -> None:
    layer = result.get("layer", "unknown")
    total = result.get("total", 0)
    passed = result.get("passed", 0)
    failed = result.get("failed", 0)
    score = result.get("score", 0)

    print(f"\n{'='*50}")
    print(f"  Layer: {layer}")
    print(f"  Total: {total} | Passed: {passed} | Failed: {failed}")
    print(f"  Score: {score}%")
    if "errors" in result:
        print(f"  Errors: {result['errors']} | Warnings: {result['warnings']} | Suggestions: {result['suggestions']}")
    print(f"{'='*50}")

    for detail in result.get("details", []):
        status = "PASS" if detail["passed"] else "FAIL"
        print(f"  [{status}] {detail['id']} {detail['name']}: {detail['message']}")

    print()


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python evals/eval_runner.py structure                        # Layer 1: structure check")
        print("  python evals/eval_runner.py quality <resume text or file>   # Layer 2: quality check")
        print("  python evals/eval_runner.py all <resume text or file>       # Both layers")
        return 1

    cmd = sys.argv[1].lower()

    if cmd == "structure":
        result = run_structure_checks()
        print_report(result)
        return 0 if result["failed"] == 0 else 1

    elif cmd == "quality":
        if len(sys.argv) < 3:
            print("Error: quality check requires resume text or file path as argument")
            return 1
        arg = sys.argv[2]
        # Check if it's a file path
        p = Path(arg)
        if p.exists():
            text = p.read_text(encoding="utf-8")
        else:
            text = arg
        result = check_resume_quality(text)
        print_report(result)
        return 0 if result.get("errors", 0) == 0 else 1

    elif cmd == "all":
        s = run_structure_checks()
        print_report(s)
        if len(sys.argv) >= 3:
            arg = sys.argv[2]
            p = Path(arg)
            if p.exists():
                text = p.read_text(encoding="utf-8")
            else:
                text = arg
            q = check_resume_quality(text)
            print_report(q)
            return 0 if s["failed"] == 0 and q.get("errors", 0) == 0 else 1
        else:
            print("  Note: quality check skipped (no resume text provided)")
            return 0 if s["failed"] == 0 else 1

    else:
        print(f"Unknown command: {cmd}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
