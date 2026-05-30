#!/usr/bin/env python3
"""Render web service entry point for Telegram webhook mode."""

import logging
import os

from flask import Flask, jsonify, request
from telegram import Update

from bot.config import BOT_TOKEN
from bot.main import build_application


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

flask_app = Flask(__name__)

telegram_updater = None
telegram_error = None


def get_webhook_path() -> str:
    return os.getenv("WEBHOOK_PATH", "telegram-webhook").strip("/")


def get_webhook_url() -> str:
    configured_url = os.getenv("WEBHOOK_URL")
    if configured_url:
        return configured_url.rstrip("/")

    render_url = os.getenv("RENDER_EXTERNAL_URL")
    if render_url:
        return f"{render_url.rstrip('/')}/{get_webhook_path()}"

    hostname = os.getenv("RENDER_EXTERNAL_HOSTNAME")
    if hostname:
        return f"https://{hostname}/{get_webhook_path()}"

    return ""


def start_telegram_application():
    global telegram_updater, telegram_error

    try:
        telegram_updater = build_application()

        webhook_url = get_webhook_url()
        if webhook_url:
            telegram_updater.bot.set_webhook(
                url=webhook_url,
                drop_pending_updates=True,
            )
            logger.info("Telegram webhook set to %s", webhook_url)
        else:
            logger.warning("WEBHOOK_URL or RENDER_EXTERNAL_URL is missing; webhook was not set.")

    except Exception as exc:
        telegram_error = str(exc)
        logger.exception("Telegram application failed to start")


def ensure_telegram_started():
    if not BOT_TOKEN:
        logger.warning("BOT_TOKEN is missing; Telegram webhook is disabled.")
        return

    start_telegram_application()


ensure_telegram_started()


@flask_app.route("/", methods=["GET"])
def index():
    return jsonify({
        "service": "ProHub Bot",
        "status": "ok",
        "mode": "webhook",
        "telegram_ready": telegram_updater is not None and telegram_error is None and bool(BOT_TOKEN),
        "telegram_error": telegram_error,
        "health": "/health",
        "webhook_path": f"/{get_webhook_path()}",
    })


@flask_app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "telegram_ready": telegram_updater is not None and telegram_error is None and bool(BOT_TOKEN),
    })


@flask_app.route(f"/{get_webhook_path()}", methods=["POST"])
def telegram_webhook():
    if not BOT_TOKEN:
        return jsonify({"ok": False, "error": "BOT_TOKEN is missing"}), 503

    if telegram_error:
        return jsonify({"ok": False, "error": telegram_error}), 500

    if telegram_updater is None:
        return jsonify({"ok": False, "error": "Telegram app is not initialized"}), 500

    update = Update.de_json(request.get_json(force=True), telegram_updater.bot)
    telegram_updater.dispatcher.process_update(update)
    return jsonify({"ok": True})


if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    flask_app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)
