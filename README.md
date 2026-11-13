# Smart File Organizer

A Python automation tool that organizes messy folders by identifying files and
moving them into appropriate category directories.

## Features

- **Automatic folder creation** – category folders are created on demand.
- **File-type detection** – extensions are mapped to categories (Images,
  Documents, Video, Code, ...).
- **Organize by date** – optionally nest files into `Year/Month` subfolders.
- **Duplicate detection** – identical files (by SHA-256) are set aside in a
  `Duplicates/` folder.
- **Rename conflicting files** – name clashes get a ` (1)`, ` (2)` suffix.
- **Activity logs** – every action is written to `file_organizer.log`.
- **Undo last operation** – revert the most recent run.

## Usage

```bash
# Preview what would happen (no changes)
python main.py /path/to/folder --dry-run

# Organize by file type
python main.py /path/to/folder

# Organize and also group by date, and set duplicates aside
python main.py /path/to/folder --by-date --duplicates

# Undo the most recent run for that folder
python main.py /path/to/folder --undo
```

## Project structure

```
fileOrganiser/
├── main.py                     # CLI entry point
└── file_organizer/
    ├── categories.py           # extension -> category mapping
    ├── duplicates.py           # hashing + conflict-free naming
    ├── history.py              # undo history store
    ├── organizer.py            # core scan/move logic + logging
    └── cli.py                  # argument parsing
```

Requires Python 3.9+ (standard library only: `pathlib`, `os`, `shutil`,
`hashlib`, `logging`).
