#!/usr/bin/env python3
"""Entrypoint for the news-image-20261120 v5 entry (harness program/v1).

The approved front-page image is stored in this repo as ``entry.png``.
All this program does is copy that file byte-for-byte into the harness
output directory. No rendering, no network access, no randomness and no
timestamps are involved, so two runs always produce identical bytes.

The output directory is taken from ``MAKEFUN_OUTPUT_DIR`` and defaults
to ``/output``.
"""

from __future__ import annotations

import hashlib
import os
import sys
from pathlib import Path

ENTRY = "entry.png"
LIMIT_BYTES = 1024 * 1024  # harness cap: image must be <= 1 MiB


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> int:
    root = Path(__file__).resolve().parent
    source = root / ENTRY
    if not source.is_file():
        print(f"error: {source} not found", file=sys.stderr)
        return 1

    data = source.read_bytes()
    if len(data) > LIMIT_BYTES:
        print(
            f"error: {ENTRY} is {len(data)} bytes, over the "
            f"{LIMIT_BYTES} byte limit",
            file=sys.stderr,
        )
        return 1

    out_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    out_dir.mkdir(parents=True, exist_ok=True)
    target = out_dir / ENTRY

    # Write to a temp file first, then rename, so a failed run can never
    # leave a half-written entry.png behind.
    tmp = target.with_suffix(".png.tmp")
    tmp.write_bytes(data)
    os.replace(tmp, target)

    copied = target.read_bytes()
    if copied != data:
        print(f"error: {target} differs from {source}", file=sys.stderr)
        return 1

    print(f"wrote {target} ({len(copied)} bytes, sha256 {digest(copied)})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
