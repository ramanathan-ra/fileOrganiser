"""Command-line interface for the Smart File Organizer."""

from __future__ import annotations

import argparse
import sys

from .organizer import FileOrganizer


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="file-organizer",
        description="Automatically organize a messy folder by file type.",
    )
    parser.add_argument("directory", help="Directory to organize.")
    parser.add_argument(
        "--by-date",
        action="store_true",
        help="Also group files into Year/Month subfolders by modified date.",
    )
    parser.add_argument(
        "--duplicates",
        action="store_true",
        help="Detect duplicate files (by content) and set them aside.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview actions without moving any files.",
    )
    parser.add_argument(
        "--undo",
        action="store_true",
        help="Undo the most recent organize run for this directory.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        organizer = FileOrganizer(
            args.directory,
            by_date=args.by_date,
            detect_duplicates=args.duplicates,
            dry_run=args.dry_run,
        )
    except (NotADirectoryError, FileNotFoundError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1

    if args.undo:
        organizer.undo()
    else:
        organizer.organize()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
