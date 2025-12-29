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


def get_context_usage(transcript_path: str, context_limit: int) -> str:
    """Parse transcript to get context usage percentage."""
    try:
        if not transcript_path or not Path(transcript_path).exists():
            return ""

        limit = context_limit or 200_000

        # Get LAST input tokens (each API call includes full message history)
        last_input = 0
        with open(transcript_path) as f:
            for line in f:
                try:
                    entry = json.loads(line)
                    usage = entry.get("message", {}).get("usage", {})
                    if usage:
                        inp = (usage.get("input_tokens", 0) +
                               usage.get("cache_read_input_tokens", 0) +
                               usage.get("cache_creation_input_tokens", 0))
                        if inp > 0:
                            last_input = inp
                except:
                    continue

        if last_input == 0:
            return ""

        pct = (last_input / limit) * 100

        # Color based on usage (system prompt + tools overhead ~15%)
        total_pct = pct + 15
        if total_pct < 50:
            color = "\033[32m"  # green
        elif total_pct < 80:
            color = "\033[33m"  # yellow
        else:
            color = "\033[31m"  # red

        R = "\033[0m"  # reset
        return f"{color}{pct:.0f}%+{R}"
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
    transcript_path = data.get("transcript_path", "")
    context_limit = data.get("context_window", {}).get("context_window_size", 200_000)
    branch = get_branch(project_dir)

    # Project folder name
    folder = Path(project_dir).name if project_dir else "?"

    # Context usage
    ctx = get_context_usage(transcript_path, context_limit)

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
