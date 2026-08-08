#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

BACKEND_SCRIPT="$ROOT_DIR/scripts/backend.sh"
FRONTEND_SCRIPT="$ROOT_DIR/scripts/frontend.sh"

PIDS=()


cleanup() {
    echo
    echo "Stopping ISP development services..."

    for pid in "${PIDS[@]:-}"; do
        if kill -0 "$pid" 2>/dev/null; then
            kill "$pid" 2>/dev/null || true
        fi
    done

    wait 2>/dev/null || true

    echo "ISP development services stopped."
}


trap cleanup SIGINT SIGTERM EXIT


echo "======================================"
echo "        ISP Development Environment"
echo "======================================"
echo


echo "Starting infrastructure..."

"$ROOT_DIR/scripts/infra.sh"

echo
echo "Checking infrastructure readiness..."

"$ROOT_DIR/scripts/wait-for-services.sh"

echo
echo "Infrastructure is ready."

echo "Starting backend..."

"$BACKEND_SCRIPT" &
BACKEND_PID=$!

PIDS+=("$BACKEND_PID")


echo "Starting frontend..."

"$FRONTEND_SCRIPT" &
FRONTEND_PID=$!

PIDS+=("$FRONTEND_PID")


echo
echo "======================================"
echo "       ISP Development Environment"
echo "              Running"
echo "======================================"
echo
echo "Backend:  http://127.0.0.1:8000"
echo "Frontend: http://localhost:5173"
echo
echo "Press Ctrl+C to stop."
echo


wait -n "${PIDS[@]}"