#!/usr/bin/env bash

set -euo pipefail

# ==========================================
# AI Resume Screening & Interview System
# Health Check Script
# ==========================================

APP_NAME="ai-resume-screening-interview-system"

# Configuration
API_URL="${API_URL:-http://localhost:8000}"
HEALTH_ENDPOINT="${HEALTH_ENDPOINT:-/api/health}"
TIMEOUT="${TIMEOUT:-10}"

echo "=========================================="
echo " ${APP_NAME}"
echo " Health Check"
echo "=========================================="
echo

# ------------------------------------------
# Check API
# ------------------------------------------

echo "[1/5] Checking Backend API..."

if curl \
    --silent \
    --show-error \
    --fail \
    --max-time "$TIMEOUT" \
    "${API_URL}${HEALTH_ENDPOINT}" \
    > /tmp/backend_health_response.json; then

    echo "✓ Backend API: HEALTHY"

    if command -v jq >/dev/null 2>&1; then
        cat /tmp/backend_health_response.json | jq .
    else
        cat /tmp/backend_health_response.json
    fi
else
    echo "✗ Backend API: UNHEALTHY"
    exit 1
fi

echo

# ------------------------------------------
# Check PostgreSQL
# ------------------------------------------

echo "[2/5] Checking PostgreSQL..."

POSTGRES_HOST="${POSTGRES_HOST:-localhost}"
POSTGRES_PORT="${POSTGRES_PORT:-5432}"

if command -v pg_isready >/dev/null 2>&1; then

    if pg_isready \
        -h "$POSTGRES_HOST" \
        -p "$POSTGRES_PORT" \
        >/dev/null 2>&1; then

        echo "✓ PostgreSQL: HEALTHY"
    else
        echo "✗ PostgreSQL: UNHEALTHY"
        exit 1
    fi

else
    echo "⚠ pg_isready not installed; skipping PostgreSQL check"
fi

echo

# ------------------------------------------
# Check Redis
# ------------------------------------------

echo "[3/5] Checking Redis..."

REDIS_HOST="${REDIS_HOST:-localhost}"
REDIS_PORT="${REDIS_PORT:-6379}"

if command -v redis-cli >/dev/null 2>&1; then

    REDIS_RESPONSE=$(redis-cli \
        -h "$REDIS_HOST" \
        -p "$REDIS_PORT" \
        ping 2>/dev/null || true)

    if [ "$REDIS_RESPONSE" = "PONG" ]; then
        echo "✓ Redis: HEALTHY"
    else
        echo "✗ Redis: UNHEALTHY"
        exit 1
    fi

else
    echo "⚠ redis-cli not installed; skipping Redis check"
fi

echo

# ------------------------------------------
# Check Celery Worker
# ------------------------------------------

echo "[4/5] Checking Celery Worker..."

CELERY_HEALTH_ENDPOINT="${CELERY_HEALTH_ENDPOINT:-${API_URL}/api/health/worker}"

if curl \
    --silent \
    --show-error \
    --fail \
    --max-time "$TIMEOUT" \
    "$CELERY_HEALTH_ENDPOINT" \
    >/tmp/celery_health_response.json; then

    echo "✓ Celery Worker: HEALTHY"

    if command -v jq >/dev/null 2>&1; then
        cat /tmp/celery_health_response.json | jq .
    else
        cat /tmp/celery_health_response.json
    fi

else
    echo "⚠ Celery Worker: health endpoint unavailable"
fi

echo

# ------------------------------------------
# Check S3
# ------------------------------------------

echo "[5/5] Checking S3..."

S3_BUCKET="${S3_BUCKET:-}"

if [ -n "$S3_BUCKET" ] && command -v aws >/dev/null 2>&1; then

    if aws s3api head-bucket \
        --bucket "$S3_BUCKET" \
        >/dev/null 2>&1; then

        echo "✓ S3 Bucket: HEALTHY"
    else
        echo "✗ S3 Bucket: UNHEALTHY"
        exit 1
    fi

elif [ -z "$S3_BUCKET" ]; then

    echo "⚠ S3_BUCKET not configured; skipping S3 check"

else

    echo "⚠ AWS CLI not installed; skipping S3 check"

fi

echo
echo "=========================================="
echo " Health Check Completed"
echo "=========================================="
echo "Status: HEALTHY"
echo "=========================================="

rm -f /tmp/backend_health_response.json
rm -f /tmp/celery_health_response.json

exit 0