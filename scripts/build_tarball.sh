#!/usr/bin/env bash
# Build the counted SpectralLock sdist and copy it to the Worker assets folder.
# Author: Aziel Eliab
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
python3 -m pip install -q build
python3 -m build --sdist
ASSET="spectrallock-0.3.0.tar.gz"
mkdir -p workers/download-tracker/public
cp -f "dist/${ASSET}" "workers/download-tracker/public/${ASSET}"
echo "Wrote workers/download-tracker/public/${ASSET}"
ls -l "workers/download-tracker/public/${ASSET}"
