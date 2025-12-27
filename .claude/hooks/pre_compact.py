#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

"""
Pre-compact hook: backs up conversation transcript before compaction.
Triggered on both manual (/compact) and auto-compact events.
"""

import json
import shutil
import sys
from datetime import datetime
from pathlib import Path

# Backup directory relative to project root
BACKUP_DIR = Path(__file__).parent.parent / "backups"


def backup_transcript(transcript_path: str, session_id: str, trigger: str) -> str | None:
    """Create timestamped backup of the transcript."""
    try:
        src = Path(transcript_path)
        if not src.exists():
            return None

        BACKUP_DIR.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        short_session = session_id[:8] if session_id else "unknown"
        backup_name = f"{timestamp}_{trigger}_{short_session}.jsonl"
        dest = BACKUP_DIR / backup_name

        shutil.copy2(src, dest)
        return str(dest)
    except Exception as e:
        print(f"Backup failed: {e}", file=sys.stderr)
        return None


def main():
    try:
        input_data = json.loads(sys.stdin.read())

        session_id = input_data.get("session_id", "")
        transcript_path = input_data.get("transcript_path", "")
        trigger = input_data.get("trigger", "unknown")  # "manual" or "auto"

        if transcript_path:
            backup_path = backup_transcript(transcript_path, session_id, trigger)
            if backup_path:
                print(f"Transcript backed up: {backup_path}")

        sys.exit(0)

    except json.JSONDecodeError:
        sys.exit(0)
    except Exception:
        sys.exit(0)


if __name__ == "__main__":
    main()
