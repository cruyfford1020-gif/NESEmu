#!/usr/bin/env bash
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
chmod +x setup.sh dump-original.sh build-bin.sh
./setup.sh
python3 -m pip install --user flask
