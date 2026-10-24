#!/usr/bin/env sh
set -eu
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
python3.11 -m venv "$ROOT/runtime/python"
"$ROOT/runtime/python/bin/python" -m pip install --keyring-provider disabled --find-links "$ROOT/app/packages" -r "$ROOT/app/requirements.txt"
printf '%s\n' 'Runtime installed. Launch CyTools_Subtitle.sh; download models from Installation.'
