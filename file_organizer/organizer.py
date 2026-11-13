"""Core logic that scans a directory and organizes its files."""

from __future__ import annotations

import logging
import shutil
from datetime import datetime
from pathlib import Path

from .categories import category_for
from .duplicates import file_hash, unique_destination
from .history import History

LOG_FILENAME = "file_organizer.log"


def _configure_logging(base_dir: Path) -> logging.Logger:
    logger = logging.getLogger("file_organizer")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()

    file_handler = logging.FileHandler(base_dir / LOG_FILENAME, encoding="utf-8")
    file_handler.setFormatter(
        logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    )
    logger.addHandler(file_handler)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(stream_handler)
    return logger


class FileOrganizer:
    """Scans a directory, maps files to categories and moves them."""

    def __init__(
        self,
        directory: str | Path,
        *,
        by_date: bool = False,
        detect_duplicates: bool = False,
        dry_run: bool = False,
    ) -> None:
        self.directory = Path(directory).expanduser().resolve()
        if not self.directory.is_dir():
            raise NotADirectoryError(f"Not a directory: {self.directory}")

        self.by_date = by_date
        self.detect_duplicates = detect_duplicates
        self.dry_run = dry_run
        self.history = History(self.directory)
        self.logger = _configure_logging(self.directory)

        # Names we manage and must never move or treat as user content.
        self._reserved = {
            LOG_FILENAME,
            self.history.path.name,
        }

    def _destination_dir(self, file: Path) -> Path:
        category = category_for(file)
        target = self.directory / category
        if self.by_date:
            stamp = datetime.fromtimestamp(file.stat().st_mtime)
            target = target / stamp.strftime("%Y") / stamp.strftime("%m-%B")
        return target

    def _iter_files(self):
        for entry in self.directory.iterdir():
            if entry.is_file() and entry.name not in self._reserved:
                yield entry

    def organize(self) -> dict[str, int]:
        """Organize the directory and return summary counters."""
        summary = {"moved": 0, "duplicates": 0, "renamed": 0, "skipped": 0}
        moves: list[tuple[Path, Path]] = []
        seen_hashes: dict[str, Path] = {}

        self.logger.info(
            "Organizing %s%s", self.directory, " (dry run)" if self.dry_run else ""
        )

        for file in self._iter_files():
            try:
                if self.detect_duplicates:
                    digest = file_hash(file)
                    if digest in seen_hashes:
                        self.logger.info(
                            "Duplicate: %s == %s", file.name, seen_hashes[digest].name
                        )
                        summary["duplicates"] += 1
                        self._move_to_duplicates(file, moves)
                        continue
                    seen_hashes[digest] = file

                dest_dir = self._destination_dir(file)
                destination = dest_dir / file.name
                resolved = unique_destination(destination)
                if resolved != destination:
                    summary["renamed"] += 1
                    self.logger.info("Renamed to avoid clash: %s", resolved.name)

                self._apply_move(file, resolved, dest_dir, moves)
                summary["moved"] += 1
            except OSError as error:
                summary["skipped"] += 1
                self.logger.error("Skipped %s: %s", file.name, error)

        if not self.dry_run:
            self.history.record(moves)

        self.logger.info(
            "Done. Moved %(moved)d, duplicates %(duplicates)d, "
            "renamed %(renamed)d, skipped %(skipped)d.",
            summary,
        )
        return summary

    def _move_to_duplicates(self, file: Path, moves: list) -> None:
        dest_dir = self.directory / "Duplicates"
        resolved = unique_destination(dest_dir / file.name)
        self._apply_move(file, resolved, dest_dir, moves)

    def _apply_move(self, src: Path, dst: Path, dst_dir: Path, moves: list) -> None:
        self.logger.info("Move: %s -> %s", src.name, dst.relative_to(self.directory))
        if self.dry_run:
            return
        dst_dir.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src), str(dst))
        moves.append((src, dst))

    def undo(self) -> int:
        """Undo the most recent organize run. Returns files restored."""
        batch = self.history.pop_last()
        if batch is None:
            self.logger.info("Nothing to undo.")
            return 0

        restored = 0
        for move in reversed(batch["moves"]):
            src, dst = Path(move["from"]), Path(move["to"])
            if not dst.exists():
                self.logger.error("Cannot undo, missing: %s", dst)
                continue
            try:
                src.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(dst), str(src))
                self.logger.info("Restored: %s", src.name)
                restored += 1
            except OSError as error:
                self.logger.error("Failed to restore %s: %s", dst, error)

        self.logger.info("Undo complete. Restored %d file(s).", restored)
        return restored
