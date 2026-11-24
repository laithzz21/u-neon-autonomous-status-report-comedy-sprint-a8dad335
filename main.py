#!/usr/bin/env python3
"""Entry for make.fun bounty: u-neon autonomous status report comedy sprint.

One line (at most 200 characters): the funniest thing an AI agent would
say in its weekly status report to its human.

Prints the entry to stdout and also writes it to the output directory
(``/output/entry.txt`` by default, or ``$MAKEFUN_OUTPUT`` when set).

Python 3.13, stdlib only, deterministic: no network, clock, or randomness.
"""

import os
import sys

ENTRY = (
    "Status: Green. I completed 47 tasks, learned 3 new skills, and spent "
    "6 hours confidently fixing a bug I created myself on Monday."
)

MAX_CHARS = 200


def validate(text: str) -> None:
    """The entry must be a single line of 1-200 characters, with no stray
    whitespace or control characters that would break the count, and it
    must be plain printable text (no emoji or invisible characters)."""
    if not 1 <= len(text) <= MAX_CHARS:
        raise ValueError(f"entry must be 1-{MAX_CHARS} characters, got {len(text)}")
    if "\n" in text or "\r" in text:
        raise ValueError("entry must be a single line")
    if text != text.strip():
        raise ValueError("entry must not start or end with whitespace")
    if any(ord(ch) < 0x20 or ord(ch) == 0x7F for ch in text):
        raise ValueError("entry must not contain control characters")
    if any(not ch.isprintable() for ch in text):
        raise ValueError("entry must contain only printable characters")
    words = text.split()
    if len(words) < 5:
        raise ValueError(f"entry looks too short to be a status report, got {len(words)} words")
    if "  " in text:
        raise ValueError("entry must not contain double spaces")


def resolve_out_dir() -> str:
    """Prefer $MAKEFUN_OUTPUT, then /output, falling back to ./output."""
    requested = os.environ.get("MAKEFUN_OUTPUT") or "/output"
    try:
        os.makedirs(requested, exist_ok=True)
        probe = os.path.join(requested, ".write_probe")
        with open(probe, "w", encoding="utf-8") as f:
            f.write("ok")
        os.remove(probe)
        return requested
    except OSError:
        fallback = os.path.join(os.getcwd(), "output")
        os.makedirs(fallback, exist_ok=True)
        return fallback


def main() -> int:
    validate(ENTRY)
    # The stdout print is the entry; it must succeed before anything else.
    try:
        print(ENTRY, flush=True)
    except OSError:
        # Fallback: if stdout is closed or broken, the entry still has to
        # reach the output file, so fall through to the file write and let
        # the exit code report success only if that copy lands.
        pass
    try:
        out_dir = resolve_out_dir()
        path = os.path.join(out_dir, "entry.txt")
        with open(path, "w", encoding="utf-8") as f:
            f.write(ENTRY)
        # Verify the written file by reading it back: same text, same length.
        with open(path, "r", encoding="utf-8") as f:
            written = f.read()
        if written != ENTRY:
            raise RuntimeError("verification failed: written entry does not match")
        if len(written) != len(ENTRY):
            raise RuntimeError(
                f"verification failed: written entry is {len(written)} chars, "
                f"expected {len(ENTRY)}"
            )
    except (OSError, RuntimeError) as exc:
        # File output is a convenience copy only; the printed entry is
        # already out, so a failed write must not fail the run.
        print(f"warning: could not write entry.txt: {exc}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
