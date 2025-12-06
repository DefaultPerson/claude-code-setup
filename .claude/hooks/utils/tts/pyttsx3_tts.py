#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "pyttsx3",
# ]
# ///
"""
Local TTS via pyttsx3 (fallback without API keys).
Works offline, but quality is lower than OpenAI.
"""

import sys


def speak(text: str) -> None:
    """Plays text via pyttsx3."""
    try:
        import pyttsx3
    except ImportError:
        print("Error: install pyttsx3", file=sys.stderr)
        print("  uv pip install pyttsx3", file=sys.stderr)
        sys.exit(1)

    try:
        engine = pyttsx3.init()

        # Try to find Russian voice
        voices = engine.getProperty("voices")
        russian_voice = None
        for voice in voices:
            if "ru" in voice.id.lower() or "russian" in voice.name.lower():
                russian_voice = voice.id
                break

        if russian_voice:
            engine.setProperty("voice", russian_voice)

        # Speed settings
        engine.setProperty("rate", 150)
        engine.setProperty("volume", 0.9)

        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        print(f"TTS error: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    if len(sys.argv) > 1:
        text = " ".join(sys.argv[1:])
    else:
        text = "Привет! Это тестовое сообщение."

    speak(text)


if __name__ == "__main__":
    main()
