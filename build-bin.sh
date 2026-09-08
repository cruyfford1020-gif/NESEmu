#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
XML="${1:-work/layout.xml}"
OUT="${2:-output/game.bin}"
[ -x "$ROOT/mkpsxiso" ] || { echo "Run ./setup.sh first"; exit 1; }
[ -f "$ROOT/$XML" ] || { echo "XML layout not found: $XML"; exit 1; }
mkdir -p "$ROOT/output"
cd "$ROOT"
./mkpsxiso "$XML" -o "$OUT" -c "${OUT%.bin}.cue"
echo "Build complete: $OUT and ${OUT%.bin}.cue"
