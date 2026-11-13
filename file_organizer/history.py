"""Persistent history of move operations to support undo."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

HISTORY_FILENAME = ".file_organizer_history.json"


class History:
    """Stores batches of file moves so the last run can be undone."""

    def __init__(self, base_dir: Path) -> None:
        self.path = base_dir / HISTORY_FILENAME

    def _load(self) -> list[dict]:
        if not self.path.exists():
            return []
        try:
            with self.path.open("r", encoding="utf-8") as handle:
                return json.load(handle)
        except (json.JSONDecodeError, OSError):
            return []

    def _save(self, batches: list[dict]) -> None:
        with self.path.open("w", encoding="utf-8") as handle:
            json.dump(batches, handle, indent=2)

    def record(self, moves: list[tuple[Path, Path]]) -> None:
        """Append a batch of ``(source, destination)`` moves to the history."""
        if not moves:
            return
        batches = self._load()
        batches.append(
            {
                "timestamp": datetime.now().isoformat(timespec="seconds"),
                "moves": [{"from": str(src), "to": str(dst)} for src, dst in moves],
            }
        )
        self._save(batches)

    def pop_last(self) -> dict | None:
        """Remove and return the most recent batch, or ``None`` if empty."""
        batches = self._load()
        if not batches:
            return None
        last = batches.pop()
        self._save(batches)
        return last
