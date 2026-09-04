#!/usr/bin/env bash
# Install the QRAFIG skill system into a QRAFIG checkout.
#
#   ./qrafig/install.sh --dry-run /path/to/qrafig
#   ./qrafig/install.sh [--force] /path/to/qrafig
#
# Copies CLAUDE.md, .claude/skills/ and docs/ai/. Never deletes anything.
# Refuses to overwrite an existing CLAUDE.md without --force.
set -euo pipefail

PACK="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DRY=0
FORCE=0
TARGET=""

for arg in "$@"; do
  case "$arg" in
    --dry-run) DRY=1 ;;
    --force)   FORCE=1 ;;
    -h|--help) sed -n '2,9p' "$0"; exit 0 ;;
    -*)        echo "unknown option: $arg" >&2; exit 2 ;;
    *)         TARGET="$arg" ;;
  esac
done

[ -n "$TARGET" ] || { echo "usage: $0 [--dry-run] [--force] /path/to/qrafig" >&2; exit 2; }
TARGET="$(cd "$TARGET" 2>/dev/null && pwd)" || { echo "no such directory: $TARGET" >&2; exit 1; }

# Refuse to install into something that is not QRAFIG.
if [ ! -f "$TARGET/Qrafig.sln" ] || [ ! -f "$TARGET/docs/implementation-status.md" ]; then
  echo "not a QRAFIG checkout: $TARGET (expected Qrafig.sln and docs/implementation-status.md)" >&2
  exit 1
fi

say() { if [ "$DRY" = 1 ]; then echo "would $*"; else echo "$*"; fi; }
run() { if [ "$DRY" = 0 ]; then "$@"; fi; }

if [ -f "$TARGET/CLAUDE.md" ] && [ "$FORCE" = 0 ]; then
  echo "refusing to overwrite $TARGET/CLAUDE.md — read it, merge what it says, then re-run with --force" >&2
  exit 1
fi

say "write   $TARGET/CLAUDE.md"
run cp "$PACK/CLAUDE.md" "$TARGET/CLAUDE.md"

say "create  $TARGET/.claude/skills/"
run mkdir -p "$TARGET/.claude/skills"

for skill in "$PACK"/.claude/skills/*/; do
  name="$(basename "$skill")"
  say "install $TARGET/.claude/skills/$name/"
  run mkdir -p "$TARGET/.claude/skills/$name"
  run cp -R "$skill." "$TARGET/.claude/skills/$name/"
done

say "create  $TARGET/docs/ai/"
run mkdir -p "$TARGET/docs/ai"
for doc in skills.md sources.md routing-eval.md; do
  say "write   $TARGET/docs/ai/$doc"
  run cp "$PACK/docs/ai/$doc" "$TARGET/docs/ai/$doc"
done

echo
if [ "$DRY" = 1 ]; then
  echo "dry run: nothing was written."
else
  echo "installed. Next:"
  echo "  cd $TARGET && git status"
  echo "  start Claude Code at the repository root and run /qrafig-router"
fi
