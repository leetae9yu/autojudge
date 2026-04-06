#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND_DIR="$ROOT_DIR/backend"
FRONTEND_DIR="$ROOT_DIR/frontend"
BACKEND_HOST="${BACKEND_HOST:-0.0.0.0}"
BACKEND_PORT="${BACKEND_PORT:-8000}"
FRONTEND_HOST="${FRONTEND_HOST:-0.0.0.0}"
FRONTEND_PORT="${FRONTEND_PORT:-3000}"

if [[ ! -x "$BACKEND_DIR/venv/bin/python" ]]; then
  printf 'Error: backend virtualenv not found at %s\n' "$BACKEND_DIR/venv/bin/python" >&2
  printf 'Run: cd backend && python -m venv venv && source venv/bin/activate && pip install -r requirements.txt\n' >&2
  exit 1
fi

if [[ ! -d "$FRONTEND_DIR/node_modules" ]]; then
  printf 'Error: frontend dependencies are not installed.\n' >&2
  printf 'Run: cd frontend && npm install\n' >&2
  exit 1
fi

backend_pid=''
frontend_pid=''

cleanup() {
  local exit_code=$?

  if [[ -n "$backend_pid" ]] && kill -0 "$backend_pid" 2>/dev/null; then
    kill "$backend_pid" 2>/dev/null || true
  fi

  if [[ -n "$frontend_pid" ]] && kill -0 "$frontend_pid" 2>/dev/null; then
    kill "$frontend_pid" 2>/dev/null || true
  fi

  wait "$backend_pid" 2>/dev/null || true
  wait "$frontend_pid" 2>/dev/null || true

  exit "$exit_code"
}

trap cleanup INT TERM EXIT

printf '\n[AutoJudge] Starting backend on http://localhost:%s\n' "$BACKEND_PORT"
(
  cd "$BACKEND_DIR"
  exec ./venv/bin/python -m uvicorn main:app --reload --host "$BACKEND_HOST" --port "$BACKEND_PORT"
) &
backend_pid=$!

printf '[AutoJudge] Starting frontend on http://localhost:%s\n\n' "$FRONTEND_PORT"
(
  cd "$FRONTEND_DIR"
  exec npm run dev -- --host "$FRONTEND_HOST" --port "$FRONTEND_PORT"
) &
frontend_pid=$!

printf '[AutoJudge] Backend PID: %s\n' "$backend_pid"
printf '[AutoJudge] Frontend PID: %s\n' "$frontend_pid"
printf '[AutoJudge] Press Ctrl+C to stop both servers.\n\n'

wait -n "$backend_pid" "$frontend_pid"
