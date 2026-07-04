"""SessionEnd hook entry: reads Claude Code's hook JSON on stdin, observes the
workspace, and distills the session transcript into workflow memory."""
import json
import sys
from pathlib import Path

from . import observer, session_memory


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return
    cwd = payload.get("cwd", "")
    if cwd and Path(cwd).is_dir():
        try:
            observer.look(Path(cwd))
        except Exception:
            pass
    transcript = payload.get("transcript_path", "")
    if transcript:
        try:
            session_memory.distill_claude_transcript(transcript, cwd)
        except Exception:
            pass


if __name__ == "__main__":
    main()
