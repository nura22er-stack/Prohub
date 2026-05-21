#!/usr/bin/env bash
set -euo pipefail

REPO_URL="${REPO_URL:-https://github.com/nura22er-stack/Prohub.git}"
BRANCH="${BRANCH:-main}"
APP_DIR="${APP_DIR:-/opt/prohub-bot}"
APP_USER="${APP_USER:-prohub}"
ENV_FILE="${ENV_FILE:-/etc/prohub-bot.env}"

if [ "$(id -u)" -ne 0 ]; then
  echo "Run as root: sudo bash deploy/install-from-git.sh"
  exit 1
fi

export DEBIAN_FRONTEND=noninteractive

if command -v apt-get >/dev/null 2>&1; then
  apt-get update
  apt-get install -y git python3 python3-venv python3-pip
elif command -v dnf >/dev/null 2>&1; then
  dnf install -y git python3 python3-pip
elif command -v yum >/dev/null 2>&1; then
  yum install -y git python3 python3-pip
else
  echo "Unsupported Linux package manager. Install git, python3, venv/pip first."
  exit 1
fi

if ! id "$APP_USER" >/dev/null 2>&1; then
  useradd --system --create-home --shell /usr/sbin/nologin "$APP_USER"
fi

systemctl stop prohub-bot.service prohub-api.service 2>/dev/null || true

if [ -d "$APP_DIR/.git" ]; then
  git -C "$APP_DIR" fetch --all --prune
  git -C "$APP_DIR" checkout "$BRANCH"
  git -C "$APP_DIR" pull --ff-only origin "$BRANCH"
else
  rm -rf "$APP_DIR"
  git clone --branch "$BRANCH" "$REPO_URL" "$APP_DIR"
fi

python3 -m venv "$APP_DIR/venv"
"$APP_DIR/venv/bin/pip" install --upgrade pip
"$APP_DIR/venv/bin/pip" install -r "$APP_DIR/requirements.txt"

if [ ! -f "$ENV_FILE" ]; then
  cp "$APP_DIR/deploy/prohub-bot.env.example" "$ENV_FILE"
  chmod 600 "$ENV_FILE"
  echo "Created $ENV_FILE. Fill BOT_TOKEN and ADMIN_ID before starting services."
fi

cp "$APP_DIR/deploy/prohub-bot.service" /etc/systemd/system/prohub-bot.service
cp "$APP_DIR/deploy/prohub-api.service" /etc/systemd/system/prohub-api.service

chown -R "$APP_USER:$APP_USER" "$APP_DIR"
systemctl daemon-reload
systemctl enable prohub-bot.service prohub-api.service

if grep -q "your_telegram_bot_token_here" "$ENV_FILE" || grep -q "^ADMIN_ID=0$" "$ENV_FILE"; then
  echo "Install complete, but $ENV_FILE still needs real settings."
  echo "Use deploy/write-env.sh or edit it manually."
else
  systemctl restart prohub-bot.service prohub-api.service
  echo "Install complete. Services started."
fi

systemctl --no-pager --full status prohub-bot.service prohub-api.service || true
