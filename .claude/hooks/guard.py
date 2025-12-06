#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.8"
# ///
"""
Claude Code PreToolUse Hook
Blocks dangerous commands, protects .env files, logs all actions.
Optimized for docker/docker-compose projects.
"""

import json
import sys
import re
from pathlib import Path
from datetime import datetime


def is_dangerous_rm_command(command: str) -> bool:
    """
    Comprehensive detection of dangerous rm commands.
    """
    normalized = ' '.join(command.lower().split())

    # rm -rf variations
    rm_patterns = [
        r'\brm\s+.*-[a-z]*r[a-z]*f',      # rm -rf, rm -fr, rm -Rf
        r'\brm\s+.*-[a-z]*f[a-z]*r',      # rm -fr variations
        r'\brm\s+--recursive\s+--force',   # rm --recursive --force
        r'\brm\s+--force\s+--recursive',   # rm --force --recursive
        r'\brm\s+-r\s+.*-f',               # rm -r ... -f
        r'\brm\s+-f\s+.*-r',               # rm -f ... -r
    ]

    for pattern in rm_patterns:
        if re.search(pattern, normalized):
            # Check dangerous paths
            dangerous_paths = [
                r'\s/$',              # / в конце
                r'\s/\s',             # / как аргумент
                r'\s/\*',             # /*
                r'\s~/?(\s|$)',       # ~ или ~/
                r'\s\$HOME',          # $HOME
                r'\s\.\.',            # ..
                r'\s\./?\s*$',        # . или ./
                r'\s/etc\b',          # /etc
                r'\s/var\b',          # /var
                r'\s/usr\b',          # /usr
                r'\s/home\b',         # /home
                r'\s/root\b',         # /root
            ]
            for path in dangerous_paths:
                if re.search(path, normalized):
                    return True

    return False


def is_dangerous_system_command(command: str) -> bool:
    """
    Detection of dangerous system commands.
    """
    normalized = ' '.join(command.lower().split())

    dangerous_patterns = [
        # Disk formatting and writing
        (r'\bmkfs\.', "filesystem formatting"),
        (r'\bdd\s+.*of=/dev/', "direct disk write"),
        (r'>\s*/dev/sd[a-z]', "write to block device"),
        (r'\bfdisk\b', "disk partitioning"),
        (r'\bparted\b', "disk partitioning"),

        # Download and execute
        (r'curl\s+.*\|\s*(ba)?sh', "curl pipe to shell"),
        (r'wget\s+.*\|\s*(ba)?sh', "wget pipe to shell"),
        (r'curl\s+.*\|\s*python', "curl pipe to python"),
        (r'wget\s+.*\|\s*python', "wget pipe to python"),

        # Dangerous chmod
        (r'\bchmod\s+777\s+/', "chmod 777 on system path"),
        (r'\bchmod\s+-R\s+777', "recursive chmod 777"),

        # System operations
        (r'\b:(){ :\|:& };:', "fork bomb"),
        (r'\brm\s+/etc/passwd', "remove passwd"),
        (r'\brm\s+/etc/shadow', "remove shadow"),
        (r'\bshutdown\b', "system shutdown"),
        (r'\breboot\b', "system reboot"),
        (r'\binit\s+0', "system halt"),

        # Network attacks
        (r'\bnc\s+-e\s+/bin/(ba)?sh', "reverse shell"),
        (r'\bbash\s+-i\s+>&\s+/dev/tcp/', "reverse shell"),
    ]

    for pattern, reason in dangerous_patterns:
        if re.search(pattern, normalized):
            return True, reason

    return False, None


def is_env_file_write(tool_name: str, tool_input: dict) -> bool:
    """
    Blocks only WRITING to .env files.
    Reading .env and .env.local is allowed.
    """
    # Allow reading
    if tool_name == 'Read':
        return False

    # Block writing/editing .env files
    if tool_name in ['Edit', 'MultiEdit', 'Write']:
        file_path = tool_input.get('file_path', '')
        if '.env' in file_path:
            # Allow templates
            allowed_suffixes = ('.sample', '.example', '.template', '.dist')
            if any(file_path.endswith(suffix) for suffix in allowed_suffixes):
                return False
            return True

    elif tool_name == 'Bash':
        command = tool_input.get('command', '')
        # Block only writing to .env
        write_patterns = [
            r'>\s*[^\s]*\.env\b(?!\.(sample|example|template|dist))',      # > .env
            r'>>\s*[^\s]*\.env\b(?!\.(sample|example|template|dist))',     # >> .env
            r'tee\s+[^\|]*\.env\b(?!\.(sample|example|template|dist))',    # tee .env
            r'cp\s+.*\s+[^\s]*\.env\s*$',                                   # cp ... .env
            r'mv\s+.*\s+[^\s]*\.env\s*$',                                   # mv ... .env
            r'rm\s+[^\|]*\.env\b(?!\.(sample|example|template|dist))',     # rm .env
        ]

        for pattern in write_patterns:
            if re.search(pattern, command):
                return True

    return False


def is_docker_safe(command: str) -> bool:
    """
    Checks if command is a safe docker command.
    Docker commands are generally allowed, but some require attention.
    """
    normalized = command.strip().lower()

    # Dangerous docker commands to block
    dangerous_docker = [
        r'docker\s+run\s+.*--privileged',       # privileged containers
        r'docker\s+run\s+.*-v\s+/:/host',       # mounting root
        r'docker\s+run\s+.*--pid=host',         # host PID namespace
        r'docker\s+run\s+.*--network=host',     # might be ok, but be careful
        r'docker\s+system\s+prune\s+-a',        # will delete everything
    ]

    for pattern in dangerous_docker:
        if re.search(pattern, normalized):
            return False

    return True


def log_action(log_dir: Path, input_data: dict, blocked: bool = False, reason: str = None):
    """Log actions to JSON file."""
    log_path = log_dir / 'pre_tool_use.json'

    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "tool_name": input_data.get('tool_name', ''),
        "blocked": blocked,
        "reason": reason,
        "tool_input": input_data.get('tool_input', {})
    }

    try:
        if log_path.exists():
            with open(log_path, 'r') as f:
                log_data = json.load(f)
        else:
            log_data = []
    except (json.JSONDecodeError, ValueError):
        log_data = []

    log_data.append(log_entry)

    # Keep only last 1000 entries
    if len(log_data) > 1000:
        log_data = log_data[-1000:]

    with open(log_path, 'w') as f:
        json.dump(log_data, f, indent=2, ensure_ascii=False)


def main():
    try:
        input_data = json.load(sys.stdin)

        tool_name = input_data.get('tool_name', '')
        tool_input = input_data.get('tool_input', {})

        # Define log directory
        log_dir = Path.home() / '.claude' / 'logs'
        log_dir.mkdir(parents=True, exist_ok=True)

        # === Check writing to .env files ===
        if is_env_file_write(tool_name, tool_input):
            reason = "Writing to .env files is blocked"
            log_action(log_dir, input_data, blocked=True, reason=reason)
            print(f"BLOCKED: {reason}", file=sys.stderr)
            print("Use .env.sample or .env.example for templates", file=sys.stderr)
            sys.exit(2)

        # === Check Bash commands ===
        if tool_name == 'Bash':
            command = tool_input.get('command', '')

            # Check rm -rf
            if is_dangerous_rm_command(command):
                reason = "Dangerous rm command detected"
                log_action(log_dir, input_data, blocked=True, reason=reason)
                print(f"BLOCKED: {reason}", file=sys.stderr)
                sys.exit(2)

            # Check system commands
            is_dangerous, danger_reason = is_dangerous_system_command(command)
            if is_dangerous:
                reason = f"Dangerous system command: {danger_reason}"
                log_action(log_dir, input_data, blocked=True, reason=reason)
                print(f"BLOCKED: {reason}", file=sys.stderr)
                sys.exit(2)

            # Check docker commands
            if 'docker' in command.lower() and not is_docker_safe(command):
                reason = "Potentially dangerous docker command"
                log_action(log_dir, input_data, blocked=True, reason=reason)
                print(f"BLOCKED: {reason}", file=sys.stderr)
                print("Privileged containers and root mounts are restricted", file=sys.stderr)
                sys.exit(2)

        # Log successful action
        log_action(log_dir, input_data, blocked=False)
        sys.exit(0)

    except json.JSONDecodeError:
        sys.exit(0)
    except Exception as e:
        # On hook error - allow (fail-open)
        # Change to sys.exit(2) for fail-close
        sys.exit(0)


if __name__ == '__main__':
    main()