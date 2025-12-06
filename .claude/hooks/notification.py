#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "python-dotenv",
#     "openai>=1.0.0",
# ]
# ///
"""
Claude Code Notification Hook
Announces notifications when Claude is waiting for user input.
Used as a Stop (post-response) hook.
"""

import json
import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

# Load .env from project root
PROJECT_ROOT = Path(__file__).parents[2]
env_path = PROJECT_ROOT / ".env"
if env_path.exists():
    load_dotenv(env_path)

HOOKS_DIR = Path(__file__).parent
LOGS_DIR = HOOKS_DIR / "logs"
TTS_DIR = HOOKS_DIR / "utils" / "tts"
CACHE_DIR = HOOKS_DIR / "cache"

# Messages — correspond to cache files in .claude/hooks/cache/
MESSAGES = {
    "ru": {
        "ready": "Задача выполнена. Жду ваших указаний.",
        "permission": "Требуется ваше внимание.",
        "idle": "Ожидаю ваших указаний.",
    },
    "en": {
        "ready": "The AI Agent has finished its work. Awaiting your instructions.",
        "permission": "Your attention is required.",
        "idle": "Awaiting your instructions.",
    },
}


def get_language() -> str:
    """Returns language from TTS_LANGUAGE or 'ru' by default."""
    lang = os.getenv("TTS_LANGUAGE", "ru").lower()
    return lang if lang in MESSAGES else "ru"


def get_mode() -> str:
    """Returns mode: static (default) or dynamic."""
    return os.getenv("TTS_MODE", "static").lower()


# === Cache functions ===


def get_cache_path(text: str) -> Path:
    """Path to cache file for text."""
    safe_name = text.replace("/", "-").replace("\x00", "")
    return CACHE_DIR / f"{safe_name}.mp3"


def play_audio_file(filepath: Path) -> bool:
    """Play mp3 directly. Returns True if successful."""
    players = [
        ["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet"],
        ["mpv", "--no-video", "--really-quiet"],
    ]
    for cmd in players:
        if shutil.which(cmd[0]):
            try:
                subprocess.run(cmd + [str(filepath)], check=True, capture_output=True)
                return True
            except subprocess.CalledProcessError:
                continue
    return False


def check_and_play_cache(text: str) -> bool:
    """Check cache and play if exists. Returns True if played."""
    cache_path = get_cache_path(text)
    if cache_path.exists():
        return play_audio_file(cache_path)
    return False


def read_last_response(transcript_path: str) -> str | None:
    """
    Reads the last text response from assistant in JSONL transcript.
    Returns response text or None.
    """
    try:
        path = Path(transcript_path)
        if not path.exists():
            return None

        lines = path.read_text().strip().split("\n")

        # Search from the end for the last assistant response with text
        for line in reversed(lines[-50:]):
            try:
                entry = json.loads(line)
                if entry.get("type") == "assistant":
                    message = entry.get("message", {})
                    content = message.get("content", [])

                    # Collect only text blocks
                    text_parts = []
                    for item in content:
                        if isinstance(item, dict) and item.get("type") == "text":
                            text_parts.append(item.get("text", ""))
                        elif isinstance(item, str):
                            text_parts.append(item)

                    if text_parts:
                        return "\n".join(text_parts)
            except json.JSONDecodeError:
                continue

        return None
    except Exception:
        return None


def generate_summary(last_response: str, language: str) -> str | None:
    """
    Generates a brief voice summary based on Claude's last response.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or not last_response:
        return None

    try:
        from openai import OpenAI

        client = OpenAI(api_key=api_key, timeout=10.0)

        # Limit input length
        truncated = last_response[:2000] if len(last_response) > 2000 else last_response

        if language == "ru":
            prompt = (
                "Сделай очень краткую озвучку (2 коротких предложения) что было сделано. "
                "Начни с 'Задача выполнена.' Упоминай конкретику (файлы, модули) без расширений. "
                "Никаких приветствий и лишних слов.\n\n"
                f"Ответ ассистента:\n{truncated}"
            )
        else:
            prompt = (
                "Create a very brief voice summary (2 short sentences) of what was done. "
                "Start with 'Task completed.' Mention specifics (files, modules) without extensions. "
                "No greetings or filler words.\n\n"
                f"Assistant response:\n{truncated}"
            )

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150,
        )

        content = response.choices[0].message.content
        if content:
            return content.strip()
        return None

    except Exception as e:
        debug_log = LOGS_DIR / "summary_error.log"
        debug_log.write_text(f"{datetime.now().isoformat()}: {type(e).__name__}: {e}\n")
        return None


def get_tts_script_path() -> Path | None:
    """
    Selects TTS script by priority:
    1. ElevenLabs (best quality, sci-fi voices)
    2. OpenAI (good quality)
    3. pyttsx3 (fallback, works offline)
    """
    # ElevenLabs TTS (priority — best voices)
    if os.getenv("ELEVENLABS_API_KEY"):
        elevenlabs_script = TTS_DIR / "elevenlabs_tts.py"
        if elevenlabs_script.exists():
            return elevenlabs_script

    # OpenAI TTS (fallback)
    if os.getenv("OPENAI_API_KEY"):
        openai_script = TTS_DIR / "openai_tts.py"
        if openai_script.exists():
            return openai_script

    # Fallback: pyttsx3 (offline)
    pyttsx3_script = TTS_DIR / "pyttsx3_tts.py"
    if pyttsx3_script.exists():
        return pyttsx3_script

    return None


def announce_notification(message: str, is_static: bool = True) -> None:
    """
    Announces a message via TTS.
    is_static=True → checks cache first, saves to cache
    is_static=False → no caching (dynamic summary)
    """
    # 1. For static messages — check cache first
    if is_static and check_and_play_cache(message):
        return  # Played from cache

    # 2. Not in cache — need TTS provider
    tts_script = get_tts_script_path()
    if not tts_script:
        return  # No TTS and no cache — exit silently

    # 3. Call TTS with cache flag for static messages
    cmd = ["uv", "run", str(tts_script), message]
    if is_static:
        cmd.append("--cache")

    try:
        subprocess.run(
            cmd,
            timeout=15,
            capture_output=True,
            cwd=HOOKS_DIR,
        )
    except subprocess.TimeoutExpired:
        pass
    except Exception:
        pass


def log_notification(data: dict) -> None:
    """Logs notification to JSON file."""
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    log_path = LOGS_DIR / "notification.json"

    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "data": data,
    }

    try:
        if log_path.exists():
            with open(log_path, "r") as f:
                logs = json.load(f)
        else:
            logs = []
    except (json.JSONDecodeError, ValueError):
        logs = []

    logs.append(log_entry)

    # Keep only last 500 entries
    if len(logs) > 500:
        logs = logs[-500:]

    with open(log_path, "w") as f:
        json.dump(logs, f, indent=2, ensure_ascii=False)


def main():
    notify = "--notify" in sys.argv
    permission = "--permission" in sys.argv

    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError:
        input_data = {}

    # Log all notifications
    log_notification(input_data)

    # Debug: log which hook was called
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    debug_log = LOGS_DIR / "hook_debug.log"
    with open(debug_log, "a") as f:
        f.write(f"{datetime.now().isoformat()} notify={notify} permission={permission} event={input_data.get('hook_event_name', 'unknown')}\n")

    lang = get_language()
    mode = get_mode()
    msgs = MESSAGES[lang]

    # Notification hook
    if permission:
        notification_type = input_data.get("notification_type", "")
        if notification_type == "idle_prompt":
            # Idle — Claude is just waiting for input
            announce_notification(msgs["idle"], is_static=True)
            sys.exit(0)
        # Actual permission request
        announce_notification(msgs["permission"], is_static=True)
        sys.exit(0)

    # Stop hook — Claude finished response
    if notify:
        hook_event = input_data.get("hook_event_name", "")

        if hook_event == "Stop":
            if mode == "dynamic":
                # Dynamic mode — try to generate summary via LLM
                transcript_path = input_data.get("transcript_path")
                message = None

                if transcript_path:
                    last_response = read_last_response(transcript_path)
                    if last_response:
                        message = generate_summary(last_response, lang)

                if message:
                    announce_notification(message, is_static=False)
                else:
                    # Fallback to static phrase
                    announce_notification(msgs["ready"], is_static=True)
            else:
                # Static mode (default) — only MESSAGES, no LLM
                announce_notification(msgs["ready"], is_static=True)

    sys.exit(0)


if __name__ == "__main__":
    main()
