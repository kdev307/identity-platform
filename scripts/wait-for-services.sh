#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

cd "$ROOT_DIR"


wait_for_service() {
    local service="$1"
    local max_attempts="${2:-30}"
    local attempt=1

    echo "Waiting for $service..."

    while true; do
        if docker compose ps "$service" --format '{{.Health}}' | grep -q "healthy"; then
            echo "$service is ready."
            return 0
        fi

        if [ "$attempt" -ge "$max_attempts" ]; then
            echo "ERROR: $service did not become ready."
            docker compose ps "$service"
            return 1
        fi

        printf "."
        sleep 2

        attempt=$((attempt + 1))
    done
}


wait_for_service "postgres"
wait_for_service "redis"
wait_for_service "mailpit"

echo
echo "All infrastructure services are ready."