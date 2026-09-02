#!/usr/bin/env bash
# SpectralLock one-click install. Counted download via this project's Worker.
# Usage: curl -fsSL https://spectrallock-download-tracker.vibelock.workers.dev/install.sh | bash
set -euo pipefail

HOST="${SPECTRALLOCK_HOME_HOST:-https://spectrallock-download-tracker.vibelock.workers.dev}"
ASSET="${SPECTRALLOCK_HOME_ASSET:-spectrallock-0.2.0.tar.gz}"
WORKDIR="${SPECTRALLOCK_HOME:-$HOME/spectrallock}"

mkdir -p "$WORKDIR"
cd "$WORKDIR"

echo "Downloading counted tarball from ${HOST}/download (User-Agent Mozilla/5.0)…"
curl -fsSL -A 'Mozilla/5.0' "${HOST}/download?asset=${ASSET}" -o "${ASSET}"

tar -xzf "${ASSET}"
DIR="$(find . -maxdepth 1 -type d -name 'spectrallock-*' | head -n 1)"
if [ -n "${DIR}" ]; then
  cd "${DIR}"
fi

python3 -m venv .venv
# shellcheck disable=SC1091
. .venv/bin/activate
python -m pip install -U pip
python -m pip install -e .

echo
echo "Installed SpectralLock."
echo "Run:  spectrallock ui"
echo "Then open http://127.0.0.1:8861  (loopback only)"
echo "Author: Aziel Eliab."
