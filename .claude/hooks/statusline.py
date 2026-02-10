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


def get_context_info(transcript_path: str, context_limit: int) -> dict:
    """Parse transcript to get context usage info."""
    try:
        if not transcript_path or not Path(transcript_path).exists():
            return {}

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
            return {}

        pct = (last_input / limit) * 100
        tokens_left = limit - last_input
        return {"pct": pct, "tokens_left": tokens_left}
    except:
        return {}


def format_bar(pct: float, width: int = 20) -> str:
    """Build colored progress bar: [####--------------]"""
    filled = round(pct / 100 * width)
    filled = max(0, min(filled, width))

    # Color by usage level (with ~15% overhead for system prompt/tools)
    total_pct = pct + 15
    if total_pct < 50:
        color = "\033[32m"  # green
    elif total_pct < 80:
        color = "\033[33m"  # yellow
    else:
        color = "\033[31m"  # red

    D = "\033[2m"   # dim
    R = "\033[0m"   # reset
    bar_filled = "#" * filled
    bar_empty = "-" * (width - filled)
    return f"{color}[{bar_filled}{D}{bar_empty}{R}{color}]{R}", color


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
    session_id = data.get("session_id", "")
    branch = get_branch(project_dir)

    # Context info
    ctx = get_context_info(transcript_path, context_limit)

    # Project folder name
    folder = Path(project_dir).name if project_dir else ""

    # ANSI colors
    G = "\033[32m"  # green
    D = "\033[2m"   # dim
    R = "\033[0m"   # reset
    SEP = f" {D}>>{R} "

    CL = "\033[38;2;217;119;87m"  # claude orange

    parts = []
    if folder:
        parts.append(f"{D}{folder}{R}")
    if branch:
        parts.append(f"\033[35m{branch}{R}")

    parts.append(f"{CL}{model}{R}")

    if ctx:
        bar, color = format_bar(ctx["pct"])
        left_k = ctx["tokens_left"] / 1000
        parts.append(f"{bar} {color}~{left_k:.0f}k left{R}")

    print(SEP.join(parts))

if __name__ == "__main__":
    main()
