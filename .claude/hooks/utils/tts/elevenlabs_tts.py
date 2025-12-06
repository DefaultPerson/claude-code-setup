#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "httpx",
#     "python-dotenv",
# ]
# ///
"""
ElevenLabs TTS.
Cache is checked in notification.py, this script only generates audio.
"""

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import httpx
from dotenv import load_dotenv

# Load .env from project root
env_path = Path(__file__).parents[4] / ".env"
if env_path.exists():
    load_dotenv(env_path)

# Cache directory — separate folder for static MESSAGES only
CACHE_DIR = Path(__file__).parents[2] / "cache"  # .claude/hooks/cache/

# ElevenLabs voices
VOICES = {
    "laura": "5Aahq892EEb6MdNwMM3p",       # Primary voice
    "rachel": "21m00Tcm4TlvDq8ikWAM",
    "elli": "MF3mGyEYCl7XYWbV9V6O",
    "bella": "EXAVITQu4vr4xnSDxMaL",
    "freya": "jsCqWAovK2LkecY7zXl4",
}

DEFAULT_VOICE = "laura"


def play_audio_file(filepath: str) -> None:
    """Plays audio via available player."""
    players = [
        ["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet"],
        ["mpv", "--no-video", "--really-quiet"],
        ["play"],
        ["aplay"],
    ]

    for player_cmd in players:
        if shutil.which(player_cmd[0]):
            try:
                subprocess.run(player_cmd + [filepath], check=True, capture_output=True)
                return
            except subprocess.CalledProcessError:
                continue

    print("No player found: install ffmpeg, mpv or sox", file=sys.stderr)


def get_cache_path(text: str) -> Path:
    """Returns path to cache file for text."""
    # Use text as filename (like in pre-generated files)
    # Remove only slashes and null characters
    safe_name = text.replace("/", "-").replace("\x00", "")
    return CACHE_DIR / f"{safe_name}.mp3"


def speak(text: str, voice: str = DEFAULT_VOICE, save_to_cache: bool = False) -> None:
    """
    Generates and plays audio via ElevenLabs API.
    Cache is already checked in notification.py — this script only generates.
    save_to_cache=True → save to cache after generation
    """
    api_key = os.getenv("ELEVENLABS_API_KEY")
    if not api_key:
        print("Error: ELEVENLABS_API_KEY not found", file=sys.stderr)
        sys.exit(1)

    voice_id = VOICES.get(voice, VOICES[DEFAULT_VOICE])
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"

    headers = {
        "xi-api-key": api_key,
        "Content-Type": "application/json",
    }

    data = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75,
            "style": 0.3,
            "use_speaker_boost": True,
        },
    }

    try:
        with httpx.Client(timeout=30) as client:
            response = client.post(url, headers=headers, json=data)
            response.raise_for_status()
            audio_data = response.content

        # Save to cache for static messages
        if save_to_cache:
            cache_path = get_cache_path(text)
            cache_path.write_bytes(audio_data)
            play_audio_file(str(cache_path))
        else:
            # Dynamic — temp file
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
                f.write(audio_data)
                temp_path = f.name
            play_audio_file(temp_path)
            os.unlink(temp_path)

    except httpx.HTTPStatusError as e:
        print(f"ElevenLabs error: {e.response.status_code}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"TTS error: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    # Usage: ./elevenlabs_tts.py "text" [--cache]
    # --cache: save result to cache (for static MESSAGES)
    args = sys.argv[1:]
    save_cache = "--cache" in args
    args = [a for a in args if a != "--cache"]

    text = args[0] if args else "Система активирована. Добро пожаловать."
    voice = args[1] if len(args) > 1 else DEFAULT_VOICE

    speak(text, voice, save_cache)


if __name__ == "__main__":
    main()
