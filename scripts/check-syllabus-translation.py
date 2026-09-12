#!/usr/bin/env python3
"""Check whether the reviewed English syllabus matches the Arabic source."""

from __future__ import annotations

import argparse
import hashlib
import re
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
MATERIALS_DIR = SCRIPT_DIR.parent / "materials"
ARABIC_QMD = MATERIALS_DIR / "manahij-albahth-alijtimai-fall-2026.qmd"
ENGLISH_QMD = MATERIALS_DIR / "manahij-albahth-alijtimai-fall-2026.en.qmd"
HASH_FIELD = "translation-source-sha256"
HASH_PATTERN = re.compile(
    rf'^(?P<prefix>{re.escape(HASH_FIELD)}:\s*["\']?)'
    r"(?P<hash>[0-9a-f]{64})"
    r'(?P<suffix>["\']?\s*)$',
    re.MULTILINE,
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def english_text_and_hash() -> tuple[str, re.Match[str]]:
    text = ENGLISH_QMD.read_text(encoding="utf-8")
    match = HASH_PATTERN.search(text)
    if match is None:
        raise ValueError(
            f"{ENGLISH_QMD.name} is missing a valid {HASH_FIELD} metadata field."
        )
    return text, match


def mark_reviewed(source_hash: str) -> None:
    text, match = english_text_and_hash()
    updated = (
        text[: match.start("hash")]
        + source_hash
        + text[match.end("hash") :]
    )
    ENGLISH_QMD.write_text(updated, encoding="utf-8")
    print(f"Marked {ENGLISH_QMD.name} as reviewed against the current Arabic source.")


def check(source_hash: str) -> int:
    _, match = english_text_and_hash()
    reviewed_hash = match.group("hash")
    if reviewed_hash == source_hash:
        print("English syllabus translation status: current.")
        return 0

    print(
        "English syllabus translation status: OUT OF DATE.\n"
        f"Reviewed Arabic hash: {reviewed_hash}\n"
        f"Current Arabic hash:  {source_hash}\n\n"
        "Translate and review the Arabic changes in "
        f"{ENGLISH_QMD.name}, then run:\n"
        f'  python3 "{Path(__file__).name}" --mark-reviewed',
        file=sys.stderr,
    )
    return 1


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check whether the English syllabus translation is current."
    )
    parser.add_argument(
        "--mark-reviewed",
        action="store_true",
        help="Record the current Arabic hash after the English translation is reviewed.",
    )
    args = parser.parse_args()

    try:
        source_hash = sha256(ARABIC_QMD)
        if args.mark_reviewed:
            mark_reviewed(source_hash)
            return 0
        return check(source_hash)
    except (OSError, ValueError) as error:
        print(f"Translation status check failed: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
