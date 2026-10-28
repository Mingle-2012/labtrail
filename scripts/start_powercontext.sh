#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if [ -f venv/bin/activate ]; then
  # shellcheck disable=SC1091
  source venv/bin/activate
fi

export POWERCONTEXT_HOME="${POWERCONTEXT_HOME:-$ROOT/backend/data/powercontext}"
export POWERCONTEXT_URL="${POWERCONTEXT_URL:-http://127.0.0.1:8890}"
mkdir -p "$POWERCONTEXT_HOME"

echo "Starting PowerContext Server at $POWERCONTEXT_URL"
echo "Data directory: $POWERCONTEXT_HOME"
exec powercontext server run --host 127.0.0.1 --port 8890 --no-env-file --role all
