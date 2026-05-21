#!/usr/bin/env bash
set -euo pipefail

ENV_FILE="${ENV_FILE:-/etc/prohub-bot.env}"

usage() {
  cat <<'USAGE'
Usage:
  sudo BOT_TOKEN='token' ADMIN_ID='123456789' bash deploy/write-env.sh

Optional environment variables:
  BOT_USERNAME       default: @prohub_robot
  REQUIRED_CHANNEL  default: empty
  CHANNEL_ID        default: 0
  APPS_PER_PAGE     default: 10
  API_PORT          default: 5000
  API_HOST          default: 0.0.0.0
USAGE
}

if [ "${1:-}" = "--help" ]; then
  usage
  exit 0
fi

if [ "$(id -u)" -ne 0 ]; then
  echo "Run with sudo."
  exit 1
fi

if [ -z "${BOT_TOKEN:-}" ]; then
  echo "BOT_TOKEN is required."
  usage
  exit 1
fi

cat > "$ENV_FILE" <<EOF
BOT_TOKEN=${BOT_TOKEN}
BOT_USERNAME=${BOT_USERNAME:-@prohub_robot}
REQUIRED_CHANNEL=${REQUIRED_CHANNEL:-}
CHANNEL_ID=${CHANNEL_ID:-0}
ADMIN_ID=${ADMIN_ID:-0}
APPS_PER_PAGE=${APPS_PER_PAGE:-10}
API_PORT=${API_PORT:-5000}
API_HOST=${API_HOST:-0.0.0.0}
EOF

chmod 600 "$ENV_FILE"
echo "Wrote $ENV_FILE"
