#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "openai>=1.0.0",
#     "python-dotenv",
# ]
# ///
"""
OpenAI TTS script for Claude Code notifications.
Plays text via OpenAI API.
"""

import asyncio
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from dotenv import load_dotenv

# Load .env from project root
env_path = Path(__file__).parents[4] / ".env"
if env_path.exists():
    load_dotenv(env_path)


def play_audio_file(filepath: str) -> None:
    """Plays audio via available player."""
    players = [
        ["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet"],
        ["mpv", "--no-video", "--really-quiet"],
        ["play"],  # sox
        ["aplay"],  # alsa
    ]

    for player_cmd in players:
        if shutil.which(player_cmd[0]):
            try:
                subprocess.run(
                    player_cmd + [filepath],
                    check=True,
                    capture_output=True,
                )
                return
            except subprocess.CalledProcessError:
                continue

    print("No player found: install ffmpeg, mpv or sox", file=sys.stderr)


async def speak(text: str) -> None:
    """Plays text via OpenAI TTS API."""
    try:
        from openai import AsyncOpenAI
    except ImportError:
        print("Error: install openai", file=sys.stderr)
        print("  uv pip install openai", file=sys.stderr)
        sys.exit(1)

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY not found in environment", file=sys.stderr)
        sys.exit(1)

    client = AsyncOpenAI(api_key=api_key)

    try:
        response = await client.audio.speech.create(
            model="tts-1-hd",  # HD quality
            voice="nova",      # female, energetic
            input=text,
            response_format="mp3",
        )

        # Save to temp file and play
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
            f.write(response.content)
            tmp_path = f.name

        play_audio_file(tmp_path)
        os.unlink(tmp_path)

    except Exception as e:
        print(f"TTS error: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    if len(sys.argv) > 1:
        text = " ".join(sys.argv[1:])
    else:
        text = "Hello! This is a test message."

    asyncio.run(speak(text))


if __name__ == "__main__":
    main()
