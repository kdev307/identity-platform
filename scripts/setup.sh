#!/usr/bin/env bash

set -euo pipefail

# --------------------------------------------------
# ISP Development Environment Setup
# --------------------------------------------------

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

ENV_FILE="$PROJECT_ROOT/.env"
ENV_EXAMPLE_FILE="$PROJECT_ROOT/.env.example"

echo
echo "=============================================="
echo " ISP Development Environment Setup"
echo "=============================================="
echo

cd "$PROJECT_ROOT"

# --------------------------------------------------
# Helper functions
# --------------------------------------------------

info() {
    echo "[INFO] $1"
}

success() {
    echo "[✓] $1"
}

error() {
    echo "[✗] $1"
    exit 1
}

# --------------------------------------------------
# Check required commands
# --------------------------------------------------

info "Checking required tools..."

REQUIRED_COMMANDS=(
    git
    docker
    node
    npm
    uv
    curl
)

for command_name in "${REQUIRED_COMMANDS[@]}"; do
    if command -v "$command_name" >/dev/null 2>&1; then
        success "$command_name is available"
    else
        error "$command_name is not installed or not available in PATH"
    fi
done

# --------------------------------------------------
# Check Docker daemon
# --------------------------------------------------

info "Checking Docker daemon..."

if docker info >/dev/null 2>&1; then
    success "Docker daemon is running"
else
    error "Docker daemon is not running. Start Docker and run setup again."
fi

# --------------------------------------------------
# Environment configuration
# --------------------------------------------------

echo
info "Checking environment configuration..."

if [ -f "$ENV_FILE" ]; then
    success ".env already exists"
else
    if [ -f "$ENV_EXAMPLE_FILE" ]; then
        cp "$ENV_EXAMPLE_FILE" "$ENV_FILE"
        success ".env created from .env.example"
    else
        error ".env.example not found"
    fi
fi

# Load project environment variables
set -a
# shellcheck disable=SC1090
source "$ENV_FILE"
set +a

# --------------------------------------------------
# Start infrastructure
# --------------------------------------------------

echo
info "Starting infrastructure services..."

docker compose up -d

success "Docker infrastructure started"

echo
info "Waiting for PostgreSQL..."

POSTGRES_USER="${POSTGRES_USER:-isp}"
POSTGRES_DB="${POSTGRES_DB:-isp}"

for i in {1..30}; do
    if docker exec isp-postgres pg_isready \
        -U "$POSTGRES_USER" \
        -d "$POSTGRES_DB" >/dev/null 2>&1; then

        success "PostgreSQL is ready"
        break
    fi

    if [ "$i" -eq 30 ]; then
        error "PostgreSQL did not become ready within 30 seconds"
    fi

    sleep 1
done

# --------------------------------------------------
# Backend dependencies
# --------------------------------------------------

echo
info "Setting up backend dependencies..."

cd "$PROJECT_ROOT/backend"

uv sync

success "Backend dependencies installed"

# --------------------------------------------------
# Database migrations
# --------------------------------------------------

echo
info "Applying Django migrations..."

uv run python manage.py migrate

success "Django migrations applied"

# --------------------------------------------------
# Frontend dependencies
# --------------------------------------------------

echo
info "Setting up frontend dependencies..."

cd "$PROJECT_ROOT/frontend"

npm ci

success "Frontend dependencies installed"

# --------------------------------------------------
# Final validation
# --------------------------------------------------

cd "$PROJECT_ROOT"

echo
info "Running environment doctor..."

./scripts/doctor.sh

# --------------------------------------------------
# Complete
# --------------------------------------------------

echo
echo "=============================================="
echo " ISP setup completed successfully"
echo "=============================================="
echo
echo "Start development with:"
echo
echo "  ./scripts/dev.sh"
echo