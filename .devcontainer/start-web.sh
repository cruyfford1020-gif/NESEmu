#!/usr/bin/env bash
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
mkdir -p input work output
nohup python3 webapp.py >/tmp/ps1-builder.log 2>&1 &
