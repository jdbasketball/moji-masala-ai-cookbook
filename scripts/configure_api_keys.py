#!/usr/bin/env python3
"""Save optional API keys locally from hidden Terminal prompts. No network calls."""
from __future__ import annotations

import getpass
import os
import re
import sys
import warnings
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DESTINATION = ROOT / ".env.local"
KEY_NAMES = ("OPENAI_API_KEY", "ANTHROPIC_API_KEY")
KEY_PREFIXES = {"OPENAI_API_KEY": "sk-", "ANTHROPIC_API_KEY": "sk-ant-"}


def _normalize_double_paste(name: str, value: str) -> str:
    """Collapse exactly two identical provider-prefixed copies, and nothing else."""
    prefix = KEY_PREFIXES[name]
    if len(value) % 2 == 0 and value.startswith(prefix) and value.count(prefix) == 2:
        midpoint = len(value) // 2
        if value[:midpoint] == value[midpoint:]:
            return value[:midpoint]
    return value


def save_keys(destination: Path, keys: dict) -> None:
    """Create a private file without following links or replacing an existing file."""
    if not keys or any(name not in KEY_NAMES for name in keys):
        raise ValueError("Supply at least one recognized API key.")
    if any(not isinstance(value, str) or not re.fullmatch(r"[A-Za-z0-9_.-]+", value)
           for value in keys.values()):
        raise ValueError("A key contains unexpected characters. Copy the key itself, without quotes.")
    keys = {name: _normalize_double_paste(name, value) for name, value in keys.items()}
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
    fd = os.open(str(destination), flags, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as output:
        for name in KEY_NAMES:
            if name in keys:
                output.write(name + "=" + keys[name] + "\n")


def main() -> int:
    if not sys.stdin.isatty():
        print("Run this command directly in Terminal so key entry stays hidden.", file=sys.stderr)
        return 2
    if DESTINATION.exists():
        print("A local key file already exists; it has not been changed: " + str(DESTINATION))
        return 0
    print("Enter the API keys when prompted. Input is hidden. Press Enter to skip a provider.")
    print("Now copy the full key for the provider being prompted, paste it once, then press Enter.")
    print("Hidden input does not move the cursor or show characters; do not paste it a second time.")
    print("This only saves keys on your Mac; it does not call either API or make a purchase.")
    keys = {}
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", getpass.GetPassWarning)
            for name in KEY_NAMES:
                value = getpass.getpass(name + ": ").strip()
                if value:
                    keys[name] = value
        if not keys:
            print("No keys entered. No file was created.")
            return 0
        save_keys(DESTINATION, keys)
    except (OSError, ValueError, getpass.GetPassWarning) as exc:
        print("Keys were not saved: " + str(exc), file=sys.stderr)
        return 2
    except (EOFError, KeyboardInterrupt):
        print("\nCancelled.", file=sys.stderr)
        return 2
    print("Saved locally with owner-only file permissions: " + str(DESTINATION))
    print("This file is ignored by Git. Tell Codex 'keys saved'; do not paste the keys in chat.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
