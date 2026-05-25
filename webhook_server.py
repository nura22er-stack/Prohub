#!/usr/bin/env python3
"""Render web service entry point for Telegram webhook mode."""

import asyncio
import logging
import os
import threading

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

telegram_app = None
telegram_loop = None
telegram_ready = threading.Event()
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


async def start_telegram_application():
    global telegram_app, telegram_error

    try:
        telegram_app = build_application()
        await telegram_app.initialize()
        await telegram_app.start()

        webhook_url = get_webhook_url()
        if webhook_url:
            await telegram_app.bot.set_webhook(
                url=webhook_url,
                allowed_updates=Update.ALL_TYPES,
                drop_pending_updates=True,
            )
            logger.info("Telegram webhook set to %s", webhook_url)
        else:
            logger.warning("WEBHOOK_URL or RENDER_EXTERNAL_URL is missing; webhook was not set.")

        telegram_ready.set()
    except Exception as exc:
        telegram_error = str(exc)
        logger.exception("Telegram application failed to start")
        telegram_ready.set()


def run_telegram_loop():
    global telegram_loop

    telegram_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(telegram_loop)
    telegram_loop.create_task(start_telegram_application())
    telegram_loop.run_forever()


def ensure_telegram_started():
    if not BOT_TOKEN:
        logger.warning("BOT_TOKEN is missing; Telegram webhook is disabled.")
        telegram_ready.set()
        return

    thread = threading.Thread(target=run_telegram_loop, daemon=True)
    thread.start()


ensure_telegram_started()


@flask_app.route("/", methods=["GET"])
def index():
    return jsonify({
        "service": "ProHub Bot",
        "status": "ok",
        "mode": "webhook",
        "telegram_ready": telegram_ready.is_set() and telegram_error is None and bool(BOT_TOKEN),
        "telegram_error": telegram_error,
        "health": "/health",
        "webhook_path": f"/{get_webhook_path()}",
    })


@flask_app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "telegram_ready": telegram_ready.is_set() and telegram_error is None and bool(BOT_TOKEN),
    })


@flask_app.route(f"/{get_webhook_path()}", methods=["POST"])
def telegram_webhook():
    if not BOT_TOKEN:
        return jsonify({"ok": False, "error": "BOT_TOKEN is missing"}), 503

    if not telegram_ready.wait(timeout=15):
        return jsonify({"ok": False, "error": "Telegram app is still starting"}), 503

    if telegram_error:
        return jsonify({"ok": False, "error": telegram_error}), 500

    if telegram_app is None or telegram_loop is None:
        return jsonify({"ok": False, "error": "Telegram app is not initialized"}), 500

    update = Update.de_json(request.get_json(force=True), telegram_app.bot)
    future = asyncio.run_coroutine_threadsafe(telegram_app.update_queue.put(update), telegram_loop)
    future.result(timeout=15)
    return jsonify({"ok": True})


if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    flask_app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)
