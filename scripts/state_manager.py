#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简历状态管理工具
==========================================
管理 resume-state.json 的 CRUD 操作。
所有简历模块通过此文件共享状态。

用法:
    python scripts/state_manager.py init
    python scripts/state_manager.py show
    python scripts/state_manager.py update --field user_profile.name --value "张三"
    python scripts/state_manager.py append --field truth_sources --value "GitHub: github.com/zhangsan"
    python scripts/state_manager.py history
    python scripts/state_manager.py reset
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path


DEFAULT_STATE_PATH = Path("resume-state.json")

TEMPLATE = {
    "version": "1.0",
    "module": "intake",
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


def configure_output_encoding() -> None:
    """Avoid UnicodeEncodeError on Windows terminals."""
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            try:
                reconfigure(encoding="utf-8", errors="replace")
            except Exception:
                pass


configure_output_encoding()


def get_state_path() -> Path:
    override = os.getenv("RESUME_STATE_FILE")
    return Path(override) if override else DEFAULT_STATE_PATH


def load_state(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}


def save_state(path: Path, state: dict) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def get_nested(data: dict, field_path: str):
    """Get value by dot-separated path like 'user_profile.name'."""
    parts = field_path.split(".")
    current = data
    for part in parts:
        if isinstance(current, dict) and part in current:
            current = current[part]
        else:
            return None
    return current


def set_nested(data: dict, field_path: str, value) -> None:
    """Set value by dot-separated path like 'user_profile.name'."""
    parts = field_path.split(".")
    current = data
    for part in parts[:-1]:
        if part not in current or not isinstance(current[part], dict):
            current[part] = {}
        current = current[part]

    # Try to parse JSON values
    if isinstance(value, str):
        try:
            value = json.loads(value)
        except (json.JSONDecodeError, ValueError):
            pass

    current[parts[-1]] = value


def append_nested(data: dict, field_path: str, value) -> None:
    """Append value to array at dot-separated path."""
    parts = field_path.split(".")
    current = data
    for part in parts:
        if isinstance(current, dict) and part in current:
            current = current[part]
        else:
            raise ValueError(f"Field path '{field_path}' not found")

    if not isinstance(current, list):
        raise ValueError(f"Field '{field_path}' is not an array")

    # Try to parse JSON values
    if isinstance(value, str):
        try:
            value = json.loads(value)
        except (json.JSONDecodeError, ValueError):
            pass

    current.append(value)


def add_history(state: dict, action: str, details: str = "") -> None:
    """Add a history entry."""
    if "history" not in state:
        state["history"] = []
    entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "action": action,
    }
    if details:
        entry["details"] = details
    state["history"].append(entry)


def cmd_init(path: Path) -> None:
    state = load_state(path)
    if state:
        print(f"State file already exists: {path}")
        return
    save_state(path, TEMPLATE)
    print(f"Initialized: {path}")


def cmd_show(path: Path) -> None:
    state = load_state(path)
    if not state:
        print(f"No state file found: {path}")
        return
    print(json.dumps(state, ensure_ascii=False, indent=2))


def cmd_update(path: Path, field: str, value: str) -> None:
    state = load_state(path)
    if not state:
        state = TEMPLATE.copy()

    old_value = get_nested(state, field)
    set_nested(state, field, value)
    add_history(state, "update", f"{field}: {old_value} -> {value}")
    save_state(path, state)
    print(f"Updated: {field}")


def cmd_append(path: Path, field: str, value: str) -> None:
    state = load_state(path)
    if not state:
        state = TEMPLATE.copy()

    append_nested(state, field, value)
    add_history(state, "append", f"{field}: +{value}")
    save_state(path, state)
    print(f"Appended to: {field}")


def cmd_history(path: Path) -> None:
    state = load_state(path)
    if not state:
        print(f"No state file found: {path}")
        return

    history = state.get("history", [])
    if not history:
        print("No history yet.")
        return

    for entry in history:
        ts = entry.get("timestamp", "?")
        action = entry.get("action", "?")
        details = entry.get("details", "")
        print(f"[{ts}] {action}: {details}")


def cmd_reset(path: Path) -> None:
    if path.exists():
        path.unlink()
    print(f"Reset: {path}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Resume state management tool")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("init", help="Initialize state file")
    sub.add_parser("show", help="Show current state")

    update_parser = sub.add_parser("update", help="Update a field")
    update_parser.add_argument("--field", required=True, help="Field path (e.g. user_profile.name)")
    update_parser.add_argument("--value", required=True, help="New value")

    append_parser = sub.add_parser("append", help="Append to array field")
    append_parser.add_argument("--field", required=True, help="Field path (e.g. truth_sources)")
    append_parser.add_argument("--value", required=True, help="Value to append")

    sub.add_parser("history", help="Show change history")
    sub.add_parser("reset", help="Reset state file")

    args = parser.parse_args()
    path = get_state_path()

    try:
        if args.cmd == "init":
            cmd_init(path)
        elif args.cmd == "show":
            cmd_show(path)
        elif args.cmd == "update":
            cmd_update(path, args.field, args.value)
        elif args.cmd == "append":
            cmd_append(path, args.field, args.value)
        elif args.cmd == "history":
            cmd_history(path)
        elif args.cmd == "reset":
            cmd_reset(path)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
