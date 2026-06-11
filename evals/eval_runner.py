#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
resume-craft 两层 Eval 运行器
==========================================

第一层（structure）：结构完整性检查，秒级
第二层（quality）：测试用例结构验证

用法:
    python evals/eval_runner.py structure
    python evals/eval_runner.py quality
    python evals/eval_runner.py all
"""

import json
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
TEST_CASES_FILE = EVALS_DIR / "test_cases.json"

REQUIRED_REFERENCES = [
    "interaction-rules.md",
    "resume-guide.md",
    "campus-templates.md",
    "interviewer-perspective.md",
    "verification-rules.md",
    "chinese-format.md",
]


# =============================================================================
# 第一层：结构完整性检查
# =============================================================================

def check_skill_frontmatter() -> dict:
    if not SKILL_FILE.exists():
        return {"id": "S001", "name": "SKILL.md exists", "passed": False, "message": "SKILL.md not found"}

    content = SKILL_FILE.read_text(encoding="utf-8")
    has_name = bool(re.search(r"^name:\s*resume-craft", content, re.MULTILINE))
    has_desc = bool(re.search(r"^description:", content, re.MULTILINE))

    if has_name and has_desc:
        return {"id": "S001", "name": "SKILL.md frontmatter", "passed": True, "message": "frontmatter has name and description"}
    missing = []
    if not has_name:
        missing.append("name")
    if not has_desc:
        missing.append("description")
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
        return {"id": "S002", "name": "References completeness", "passed": True, "message": f"All {len(REQUIRED_REFERENCES)} references exist and non-empty"}

    problems = []
    if missing:
        problems.append(f"missing: {', '.join(missing)}")
    if empty:
        problems.append(f"too short: {', '.join(empty)}")
    return {"id": "S002", "name": "References completeness", "passed": False, "message": "; ".join(problems)}


def check_state_manager() -> dict:
    path = SCRIPTS_DIR / "state_manager.py"
    if not path.exists():
        return {"id": "S003", "name": "state_manager.py", "passed": False, "message": "state_manager.py not found"}

    try:
        result = subprocess.run(
            [sys.executable, str(path), "--help"],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            return {"id": "S003", "name": "state_manager.py", "passed": True, "message": "state_manager.py executable"}
        return {"id": "S003", "name": "state_manager.py", "passed": False, "message": f"execution failed: {result.stderr[:100]}"}
    except Exception as e:
        return {"id": "S003", "name": "state_manager.py", "passed": False, "message": f"error: {e}"}


def check_eval_runner() -> dict:
    path = EVALS_DIR / "eval_runner.py"
    if path.exists():
        return {"id": "S004", "name": "eval_runner.py", "passed": True, "message": "eval_runner.py exists"}
    return {"id": "S004", "name": "eval_runner.py", "passed": False, "message": "eval_runner.py not found"}


def check_modules_in_skill() -> dict:
    if not SKILL_FILE.exists():
        return {"id": "S005", "name": "Functional modules", "passed": False, "message": "SKILL.md not found"}

    content = SKILL_FILE.read_text(encoding="utf-8")
    modules = ["模块一", "模块二", "模块三", "模块四"]
    missing = [m for m in modules if m not in content]

    if not missing:
        return {"id": "S005", "name": "Functional modules", "passed": True, "message": f"All {len(modules)} modules present"}
    return {"id": "S005", "name": "Functional modules", "passed": False, "message": f"missing: {', '.join(missing)}"}


def check_red_lines() -> dict:
    if not SKILL_FILE.exists():
        return {"id": "S006", "name": "Red lines", "passed": False, "message": "SKILL.md not found"}

    content = SKILL_FILE.read_text(encoding="utf-8")
    lines = ["零编造", "简历正直", "信息密度", "面试官视角"]
    missing = [l for l in lines if l not in content]

    if not missing:
        return {"id": "S006", "name": "Red lines", "passed": True, "message": "All 4 red lines declared"}
    return {"id": "S006", "name": "Red lines", "passed": False, "message": f"missing: {', '.join(missing)}"}


def check_intent_table() -> dict:
    if not SKILL_FILE.exists():
        return {"id": "S007", "name": "Intent table", "passed": False, "message": "SKILL.md not found"}

    content = SKILL_FILE.read_text(encoding="utf-8")
    priorities = ["P0", "P1", "P2", "P3"]
    found = [p for p in priorities if p in content]

    if len(found) == len(priorities):
        return {"id": "S007", "name": "Intent table", "passed": True, "message": "Intent table has P0-P3"}
    missing = [p for p in priorities if p not in content]
    return {"id": "S007", "name": "Intent table", "passed": False, "message": f"missing: {', '.join(missing)}"}


def run_structure_checks() -> dict:
    checks = [
        check_skill_frontmatter(),
        check_references_exist(),
        check_state_manager(),
        check_eval_runner(),
        check_modules_in_skill(),
        check_red_lines(),
        check_intent_table(),
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
# 第二层：测试用例结构验证
# =============================================================================

def load_test_cases() -> list:
    if not TEST_CASES_FILE.exists():
        return []
    try:
        with open(TEST_CASES_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("test_cases", [])
    except (json.JSONDecodeError, IOError):
        return []


def run_quality_checks() -> dict:
    test_cases = load_test_cases()
    if not test_cases:
        return {
            "layer": "quality",
            "total": 0,
            "passed": 0,
            "failed": 0,
            "score": 0,
            "message": "No test cases found",
            "details": [],
        }

    checks = []
    for tc in test_cases:
        tc_id = tc.get("id", "unknown")
        tc_name = tc.get("name", "unknown")
        has_expected = "expected" in tc
        has_input = "user_input" in tc

        if has_expected and has_input:
            checks.append({"id": tc_id, "name": tc_name, "passed": True, "message": "Test case structure valid"})
        else:
            missing = []
            if not has_expected:
                missing.append("expected")
            if not has_input:
                missing.append("user_input")
            checks.append({"id": tc_id, "name": tc_name, "passed": False, "message": f"Missing: {', '.join(missing)}"})

    passed = sum(1 for c in checks if c["passed"])
    return {
        "layer": "quality",
        "total": len(checks),
        "passed": passed,
        "failed": len(checks) - passed,
        "score": round(passed / len(checks) * 100) if checks else 0,
        "message": "Test case structure validated. Full API quality checks require ANTHROPIC_API_KEY.",
        "details": checks,
    }


# =============================================================================
# CLI 入口
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
    print(f"{'='*50}")

    for detail in result.get("details", []):
        status = "PASS" if detail["passed"] else "FAIL"
        print(f"  [{status}] {detail['id']} {detail['name']}: {detail['message']}")

    if "message" in result:
        print(f"\n  Note: {result['message']}")

    print()


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python evals/eval_runner.py structure   # Layer 1: structure check")
        print("  python evals/eval_runner.py quality     # Layer 2: test case validation")
        print("  python evals/eval_runner.py all         # Run all")
        return 1

    cmd = sys.argv[1].lower()

    if cmd == "structure":
        result = run_structure_checks()
        print_report(result)
        return 0 if result["failed"] == 0 else 1

    elif cmd == "quality":
        result = run_quality_checks()
        print_report(result)
        return 0 if result["failed"] == 0 else 1

    elif cmd == "all":
        s = run_structure_checks()
        print_report(s)
        q = run_quality_checks()
        print_report(q)
        total_failed = s["failed"] + q["failed"]
        return 0 if total_failed == 0 else 1

    else:
        print(f"Unknown command: {cmd}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
