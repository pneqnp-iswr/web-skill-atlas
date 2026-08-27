#!/usr/bin/env python3
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]

PATTERNS = {
    "OpenAI-style API key": re.compile("sk-" + r"[A-Za-z0-9_-]{20,}"),
    "GitHub token": re.compile("gh" + r"[pousr]_[A-Za-z0-9]{20,}"),
    "AWS access key": re.compile("AKIA" + r"[0-9A-Z]{16}"),
}

SKIP_DIRS = {".git", "__pycache__"}
SKIP_SUFFIXES = {
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".webp",
    ".ico",
    ".zip",
    ".gz",
    ".pdf",
}

hits = []

for path in ROOT.rglob("*"):
    if not path.is_file():
        continue

    relative = path.relative_to(ROOT)
    if any(part in SKIP_DIRS for part in relative.parts):
        continue
    if path.suffix.lower() in SKIP_SUFFIXES:
        continue

    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        continue

    for label, pattern in PATTERNS.items():
        for match in pattern.finditer(text):
            line = text.count("\n", 0, match.start()) + 1
            hits.append((relative, line, label))

if hits:
    for path, line, label in hits:
        print(f"SECRET_PATTERN {path}:{line} {label}")
    raise SystemExit(1)

print("secret_pattern_check=clean")
