#!/usr/bin/env python3
"""Give clean Quarto sources the timestamp of their latest Git commit.

Quarto's ``date: last-modified`` reads filesystem timestamps. A GitHub Actions
checkout gives every file the checkout time, so unchanged pages would otherwise
look newly updated on every deployment. Dirty and untracked local files keep
their current timestamps so previews still reflect active edits.
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def git(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=check,
        capture_output=True,
        text=True,
    )


def is_dirty(relative_path: str) -> bool:
    working_tree = git("diff", "--quiet", "--", relative_path, check=False)
    index = git("diff", "--cached", "--quiet", "--", relative_path, check=False)
    return working_tree.returncode != 0 or index.returncode != 0


def main() -> int:
    try:
        tracked = git("ls-files", "-z", "--", "*.qmd").stdout.split("\0")
    except (OSError, subprocess.CalledProcessError):
        # Quarto can still use ordinary filesystem modification times outside Git.
        return 0

    for relative_path in filter(None, tracked):
        if is_dirty(relative_path):
            continue

        result = git(
            "log",
            "-1",
            "--format=%ct",
            "--",
            relative_path,
            check=False,
        )
        timestamp = result.stdout.strip()
        if result.returncode != 0 or not timestamp:
            continue

        source = ROOT / relative_path
        if source.is_file():
            committed_at = int(timestamp)
            os.utime(source, (committed_at, committed_at))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
