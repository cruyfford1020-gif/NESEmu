#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
TOOLS="$ROOT/tools"
mkdir -p "$TOOLS" "$ROOT/input" "$ROOT/work" "$ROOT/output"

sudo apt-get update
sudo apt-get install -y git cmake build-essential ninja-build

if [ ! -d "$TOOLS/mkpsxiso/.git" ]; then
  git clone --recursive https://github.com/Lameguy64/mkpsxiso.git "$TOOLS/mkpsxiso"
else
  git -C "$TOOLS/mkpsxiso" pull --ff-only
  git -C "$TOOLS/mkpsxiso" submodule update --init --recursive
fi

cmake -S "$TOOLS/mkpsxiso" -B "$TOOLS/mkpsxiso/build" -G Ninja -DCMAKE_BUILD_TYPE=Release
cmake --build "$TOOLS/mkpsxiso/build" -j2

MK=$(find "$TOOLS/mkpsxiso/build" -type f -name mkpsxiso -perm -111 | head -n1 || true)
DUMP=$(find "$TOOLS/mkpsxiso/build" -type f -name dumpsxiso -perm -111 | head -n1 || true)

[ -n "$MK" ] || { echo "mkpsxiso executable was not found after build."; exit 1; }
[ -n "$DUMP" ] || { echo "dumpsxiso executable was not found after build."; exit 1; }

ln -sf "$MK" "$ROOT/mkpsxiso"
ln -sf "$DUMP" "$ROOT/dumpsxiso"

echo "Ready. mkpsxiso and dumpsxiso are installed."
