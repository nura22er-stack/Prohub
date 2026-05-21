#!/usr/bin/env bash
set -euo pipefail

APP_DIR="/opt/prohub-bot"
APP_USER="prohub"
ENV_FILE="/etc/prohub-bot.env"
ARCHIVE_PATH="${1:-/tmp/prohub-bot-release.zip}"

if [ "$(id -u)" -ne 0 ]; then
  echo "Run as root: sudo bash deploy/install.sh"
  exit 1
fi

if [ ! -f "$ARCHIVE_PATH" ]; then
  echo "Archive not found: $ARCHIVE_PATH"
  echo "Copy prohub-bot-release.zip to the server, then run:"
  echo "sudo bash install.sh /path/to/prohub-bot-release.zip"
  exit 1
fi

export DEBIAN_FRONTEND=noninteractive

if command -v apt-get >/dev/null 2>&1; then
  apt-get update
  apt-get install -y python3 python3-venv python3-pip unzip
elif command -v dnf >/dev/null 2>&1; then
  dnf install -y python3 python3-pip unzip
elif command -v yum >/dev/null 2>&1; then
  yum install -y python3 python3-pip unzip
else
  echo "Unsupported Linux package manager. Install python3, venv/pip, and unzip first."
  exit 1
fi

if ! id "$APP_USER" >/dev/null 2>&1; then
  useradd --system --create-home --shell /usr/sbin/nologin "$APP_USER"
fi

systemctl stop prohub-bot.service prohub-api.service 2>/dev/null || true

mkdir -p "$APP_DIR"
tmp_dir="$(mktemp -d)"
unzip -q "$ARCHIVE_PATH" -d "$tmp_dir"

if [ -d "$tmp_dir/ProHub-Bot" ]; then
  src_dir="$tmp_dir/ProHub-Bot"
else
  src_dir="$tmp_dir"
fi

rsync_available=0
if command -v rsync >/dev/null 2>&1; then
  rsync_available=1
fi

if [ "$rsync_available" -eq 1 ]; then
  rsync -a --delete \
    --exclude '.env' \
    --exclude 'venv' \
    --exclude '__pycache__' \
    --exclude '*.pyc' \
    "$src_dir"/ "$APP_DIR"/
else
  find "$APP_DIR" -mindepth 1 -maxdepth 1 ! -name 'venv' -exec rm -rf {} +
  cp -a "$src_dir"/. "$APP_DIR"/
  find "$APP_DIR" -type d -name '__pycache__' -prune -exec rm -rf {} +
  find "$APP_DIR" -type f -name '*.pyc' -delete
fi

rm -rf "$tmp_dir"

python3 -m venv "$APP_DIR/venv"
"$APP_DIR/venv/bin/pip" install --upgrade pip
"$APP_DIR/venv/bin/pip" install -r "$APP_DIR/requirements.txt"

if [ ! -f "$ENV_FILE" ]; then
  cp "$APP_DIR/deploy/prohub-bot.env.example" "$ENV_FILE"
  chmod 600 "$ENV_FILE"
  echo "Created $ENV_FILE. Fill BOT_TOKEN, ADMIN_ID, CHANNEL_ID before starting services."
fi

cp "$APP_DIR/deploy/prohub-bot.service" /etc/systemd/system/prohub-bot.service
cp "$APP_DIR/deploy/prohub-api.service" /etc/systemd/system/prohub-api.service

chown -R "$APP_USER:$APP_USER" "$APP_DIR"
chmod +x "$APP_DIR/start.sh" 2>/dev/null || true

systemctl daemon-reload
systemctl enable prohub-bot.service prohub-api.service

if grep -q "your_telegram_bot_token_here" "$ENV_FILE"; then
  echo "Install complete, but $ENV_FILE still needs real bot settings."
  echo "Edit it with: sudo nano $ENV_FILE"
  echo "Then start: sudo systemctl restart prohub-bot prohub-api"
else
  systemctl restart prohub-bot.service prohub-api.service
  echo "Install complete. Services started."
fi

echo "Status:"
systemctl --no-pager --full status prohub-bot.service prohub-api.service || true
