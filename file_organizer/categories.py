"""Maps file extensions to human-friendly category folder names."""

from __future__ import annotations

from pathlib import Path

# Category -> set of lowercase extensions (including the leading dot).
CATEGORY_MAP: dict[str, set[str]] = {
    "Images": {
        ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".tif",
        ".svg", ".webp", ".heic", ".ico", ".raw",
    },
    "Documents": {
        ".pdf", ".doc", ".docx", ".txt", ".rtf", ".odt", ".md",
        ".tex", ".pages", ".epub", ".mobi",
    },
    "Spreadsheets": {".xls", ".xlsx", ".csv", ".ods", ".numbers"},
    "Presentations": {".ppt", ".pptx", ".odp", ".key"},
    "Audio": {".mp3", ".wav", ".flac", ".aac", ".ogg", ".m4a", ".wma"},
    "Video": {".mp4", ".mkv", ".mov", ".avi", ".wmv", ".flv", ".webm", ".m4v"},
    "Archives": {".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz", ".iso"},
    "Code": {
        ".py", ".js", ".ts", ".jsx", ".tsx", ".java", ".c", ".cpp", ".h",
        ".cs", ".go", ".rb", ".php", ".rs", ".swift", ".kt", ".sh", ".html",
        ".css", ".json", ".xml", ".yml", ".yaml", ".sql",
    },
    "Executables": {".exe", ".msi", ".dmg", ".pkg", ".deb", ".rpm", ".app"},
    "Fonts": {".ttf", ".otf", ".woff", ".woff2"},
}

# Folder used for files whose extension is not recognized.
OTHER_CATEGORY = "Others"

# Reverse lookup built once at import time: extension -> category.
_EXTENSION_INDEX: dict[str, str] = {
    ext: category
    for category, extensions in CATEGORY_MAP.items()
    for ext in extensions
}


def category_for(path: Path) -> str:
    """Return the category folder name for a given file path."""
    return _EXTENSION_INDEX.get(path.suffix.lower(), OTHER_CATEGORY)


def all_categories() -> list[str]:
    """Return every category name, including the fallback category."""
    return sorted(CATEGORY_MAP.keys()) + [OTHER_CATEGORY]
