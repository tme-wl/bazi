#!/bin/bash
# Bazi Mingyi — Web Server Startup
set -a
source "$(dirname "$0")/../.env" 2>/dev/null || echo "Warning: .env not found, using existing env vars"
set +a
cd "$(dirname "$0")/.." || exit 1

# Activate virtual environment
if [ -f .venv/bin/activate ]; then
    source .venv/bin/activate
elif [ -f .venv/Scripts/activate ]; then
    source .venv/Scripts/activate
fi

PORT=${PORT:-8000}
exec uvicorn web.server:app --host 0.0.0.0 --port "${PORT}" --reload
