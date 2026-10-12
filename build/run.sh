#!/bin/sh
set -eu
project=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
export ENAPTIC_BACKEND="$project/backend/apk_backend.py"
export ELM_ENGINE="${ELM_ENGINE:-software_x11}"
export ELM_ACCEL="${ELM_ACCEL:-none}"
export ECORE_EVAS_FORCE_SYNC_RENDER=1
exec "$project/build/out/enaptic" "$@"
