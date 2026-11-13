"""Duplicate detection and conflict-free file naming helpers."""

from __future__ import annotations

import hashlib
from pathlib import Path

_CHUNK_SIZE = 65536  # 64 KB read blocks keep memory flat for large files.


def file_hash(path: Path) -> str:
    """Return the SHA-256 hex digest of a file's contents."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(_CHUNK_SIZE), b""):
            digest.update(chunk)
    return digest.hexdigest()


def unique_destination(destination: Path) -> Path:
    """Return a path that does not collide with an existing file.

    If ``destination`` is free it is returned unchanged; otherwise a numeric
    suffix is appended before the extension, e.g. ``report (1).pdf``.
    """
    if not destination.exists():
        return destination

    stem, suffix, parent = destination.stem, destination.suffix, destination.parent
    counter = 1
    while True:
        candidate = parent / f"{stem} ({counter}){suffix}"
        if not candidate.exists():
            return candidate
        counter += 1
