#!/usr/bin/env python3
"""Claude Code status line: dir >> branch >> model >> context%"""
import json
import os
import subprocess
import sys
from pathlib import Path


def get_branch(project_dir: str) -> str:
    try:
        result = subprocess.run(
            ["git", "-C", project_dir, "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True, text=True, timeout=1
        )
        return result.stdout.strip() if result.returncode == 0 else ""
    except:
        return ""


def get_context_usage(data: dict) -> str:
    """Get context usage from native context_window.used_percentage field."""
    try:
        pct = data.get("context_window", {}).get("used_percentage")
        if pct is None:
            return ""

        # Color based on usage
        if pct < 50:
            color = "\033[32m"  # green
        elif pct < 80:
            color = "\033[33m"  # yellow
        else:
            color = "\033[31m"  # red

        R = "\033[0m"  # reset
        return f"{color}{pct:.0f}%{R}"
    except:
        return ""


def main():
    try:
        raw = sys.stdin.read()
        data = json.loads(raw)
    except:
        print("⚠ parse error")
        return

    # Debug: dump input to file (set DEBUG_STATUSLINE=1)
    if os.getenv("DEBUG_STATUSLINE"):
        debug_path = Path("/tmp/claude-statusline-debug.json")
        debug_path.write_text(json.dumps(data, indent=2, default=str))

    project_dir = data.get("workspace", {}).get("project_dir", "")
    model = data.get("model", {}).get("display_name", "?")
    branch = get_branch(project_dir)

    # Project folder name
    folder = Path(project_dir).name if project_dir else "?"

    # Context usage (native API field)
    ctx = get_context_usage(data)

    # ANSI colors
    C = "\033[36m"  # cyan
    M = "\033[35m"  # magenta
    D = "\033[2m"   # dim
    R = "\033[0m"   # reset

    parts = [f"{D}{folder}{R}"]
    if branch:
        parts.append(f"{M}{branch}{R}")
    parts.append(f"{C}{model}{R}")
    if ctx:
        parts.append(ctx)

    print(" >> ".join(parts))

if __name__ == "__main__":
    main()
