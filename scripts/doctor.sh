#!/usr/bin/env bash

set -u

# --------------------------------------------------
# ISP Development Environment Doctor
# --------------------------------------------------

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

PASS=0
FAIL=0
WARN=0

REQUIRED_NODE_MAJOR=22
REQUIRED_PYTHON_MAJOR=3
REQUIRED_PYTHON_MINOR=12

print_ok() {
    echo "  [✓] $1"
    PASS=$((PASS + 1))
}

print_fail() {
    echo "  [✗] $1"
    FAIL=$((FAIL + 1))
}

print_warn() {
    echo "  [!] $1"
    WARN=$((WARN + 1))
}

check_command() {
    local command_name="$1"
    local display_name="$2"

    if command -v "$command_name" >/dev/null 2>&1; then
        print_ok "$display_name"
    else
        print_fail "$display_name is not installed"
    fi
}

# --------------------------------------------------
# Load environment
# --------------------------------------------------

ENV_FILE="$PROJECT_ROOT/.env"

if [ -f "$ENV_FILE" ]; then
    set -a
    # shellcheck disable=SC1090
    source "$ENV_FILE"
    set +a
else
    print_warn ".env file not found; using defaults"
fi

POSTGRES_DB="${POSTGRES_DB:-isp}"
POSTGRES_USER="${POSTGRES_USER:-isp}"
POSTGRES_PORT="${POSTGRES_PORT:-5432}"

REDIS_PORT="${REDIS_PORT:-6379}"

MAILPIT_UI_PORT="${MAILPIT_UI_PORT:-8025}"

# --------------------------------------------------
# Header
# --------------------------------------------------

echo
echo "=============================================="
echo " ISP Development Environment Doctor"
echo "=============================================="
echo

# --------------------------------------------------
# Required CLI tools
# --------------------------------------------------

echo "== Required CLI Tools =="

check_command "git" "Git"
check_command "docker" "Docker"
check_command "node" "Node.js"
check_command "npm" "npm"
check_command "uv" "uv"
check_command "curl" "curl"

# --------------------------------------------------
# Runtime versions
# --------------------------------------------------

echo
echo "== Runtime Versions =="

if command -v node >/dev/null 2>&1; then
    NODE_VERSION="$(node --version | sed 's/^v//')"
    NODE_MAJOR="${NODE_VERSION%%.*}"

    if [ "$NODE_MAJOR" -eq "$REQUIRED_NODE_MAJOR" ]; then
        print_ok "Node.js $NODE_VERSION (required: $REQUIRED_NODE_MAJOR.x)"
    else
        print_fail "Node.js $NODE_VERSION (required: $REQUIRED_NODE_MAJOR.x)"
    fi
fi

if command -v npm >/dev/null 2>&1; then
    NPM_VERSION="$(npm --version)"
    print_ok "npm $NPM_VERSION"
fi

if command -v uv >/dev/null 2>&1; then
    UV_VERSION="$(uv --version)"
    print_ok "$UV_VERSION"
fi

# --------------------------------------------------
# Docker
# --------------------------------------------------

echo
echo "== Docker =="

if command -v docker >/dev/null 2>&1; then
    if docker info >/dev/null 2>&1; then
        print_ok "Docker daemon is running"
    else
        print_fail "Docker daemon is not running"
    fi
fi

# --------------------------------------------------
# Docker Compose
# --------------------------------------------------

echo
echo "== Docker Compose =="

if docker compose version >/dev/null 2>&1; then
    COMPOSE_VERSION="$(docker compose version --short)"
    print_ok "Docker Compose $COMPOSE_VERSION"
else
    print_fail "Docker Compose is unavailable"
fi

# --------------------------------------------------
# Infrastructure services
# --------------------------------------------------

echo
echo "== Infrastructure Services =="

# PostgreSQL
if docker ps --format '{{.Names}}' | grep -q '^isp-postgres$'; then
    if docker exec isp-postgres pg_isready \
        -U "$POSTGRES_USER" \
        -d "$POSTGRES_DB" >/dev/null 2>&1; then

        print_ok "PostgreSQL is accepting connections"
    else
        print_fail "PostgreSQL is not accepting connections"
    fi
else
    print_fail "PostgreSQL container is not running"
fi

# Redis
if docker ps --format '{{.Names}}' | grep -q '^isp-redis$'; then
    if [ "$(docker exec isp-redis redis-cli ping 2>/dev/null)" = "PONG" ]; then
        print_ok "Redis is responding"
    else
        print_fail "Redis is not responding"
    fi
else
    print_fail "Redis container is not running"
fi

# Mailpit
if curl -fsS \
    "http://localhost:${MAILPIT_UI_PORT}" \
    >/dev/null 2>&1; then

    print_ok "Mailpit is reachable"
else
    print_fail "Mailpit is not reachable"
fi

# --------------------------------------------------
# Python / Django
# --------------------------------------------------

echo
echo "== Python / Django =="

if [ -d "$PROJECT_ROOT/backend" ]; then

    cd "$PROJECT_ROOT/backend" || exit 1

    PYTHON_VERSION="$(
        uv run python --version 2>/dev/null |
        awk '{print $2}'
    )"

    if [ -n "$PYTHON_VERSION" ]; then

        PYTHON_MAJOR="$(echo "$PYTHON_VERSION" | cut -d. -f1)"
        PYTHON_MINOR="$(echo "$PYTHON_VERSION" | cut -d. -f2)"

        if [ "$PYTHON_MAJOR" -eq "$REQUIRED_PYTHON_MAJOR" ] &&
           [ "$PYTHON_MINOR" -eq "$REQUIRED_PYTHON_MINOR" ]; then

            print_ok \
                "Python $PYTHON_VERSION (required: $REQUIRED_PYTHON_MAJOR.$REQUIRED_PYTHON_MINOR.x)"
        else
            print_fail \
                "Python $PYTHON_VERSION (required: $REQUIRED_PYTHON_MAJOR.$REQUIRED_PYTHON_MINOR.x)"
        fi

        if uv run python manage.py check >/dev/null 2>&1; then
            print_ok "Django configuration"
        else
            print_fail "Django configuration check failed"
        fi

    else
        print_fail "Unable to determine Python version"
    fi

    cd "$PROJECT_ROOT" || exit 1

else
    print_fail "backend directory not found"
fi

# --------------------------------------------------
# Frontend
# --------------------------------------------------

echo
echo "== Frontend =="

FRONTEND_DIR="$PROJECT_ROOT/frontend"

if [ -d "$FRONTEND_DIR" ]; then

    if [ -f "$FRONTEND_DIR/package.json" ]; then
        print_ok "Frontend package.json"

        if [ -d "$FRONTEND_DIR/node_modules" ]; then
            print_ok "Frontend dependencies installed"
        else
            print_fail "Frontend dependencies are not installed"
        fi

        cd "$FRONTEND_DIR" || exit 1

        if npm run lint >/dev/null 2>&1; then
            print_ok "Frontend lint"
        else
            print_fail "Frontend lint failed"
        fi

        if npm run build >/dev/null 2>&1; then
            print_ok "Frontend production build"
        else
            print_fail "Frontend production build failed"
        fi

        cd "$PROJECT_ROOT" || exit 1

    else
        print_fail "Frontend package.json not found"
    fi

else
    print_fail "frontend directory not found"
fi

# --------------------------------------------------
# Summary
# --------------------------------------------------

echo
echo "== Summary =="

echo "  Passed  : $PASS"
echo "  Failed  : $FAIL"
echo "  Warnings: $WARN"

echo

if [ "$FAIL" -gt 0 ]; then
    echo "Environment check failed."
    exit 1
fi

echo "Environment check passed."
exit 0