#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
INPUT="${1:-}"
if [ -z "$INPUT" ]; then
  echo "Usage: ./dump-original.sh input/game.cue"
  exit 1
fi
[ -x "$ROOT/dumpsxiso" ] || { echo "Run ./setup.sh first"; exit 1; }
mkdir -p "$ROOT/work/files"
cd "$ROOT/work"
"$ROOT/dumpsxiso" "../$INPUT" -x files -s layout.xml
printf '\nDone. Files: work/files\nLayout: work/layout.xml\n'
