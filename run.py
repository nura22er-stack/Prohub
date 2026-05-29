#!/usr/bin/env python3
"""
ProHub Bot - Render-friendly entry point.

Locally it can still use a .env file. On Render, configuration must come from
Environment Variables, so this file must not require a physical .env file.
"""

import os
import signal
import subprocess
import sys
import time


processes = {}


def has_render_env():
    """Render provides env vars directly instead of a local .env file."""
    return bool(os.getenv("RENDER") or os.getenv("PORT"))


def validate_config():
    """Warn clearly for missing settings without killing the web health server."""
    if os.path.exists(".env"):
        return True

    if not has_render_env():
        print("Error: .env file not found!")
        print("Local run uchun .env.example ni .env ga nusxalang va to'ldiring.")
        sys.exit(1)

    missing = [name for name in ("BOT_TOKEN",) if not os.getenv(name)]
    if missing:
        print("Warning: required Render environment variables are missing:")
        for name in missing:
            print(f"- {name}")
        print("Web health server will still start, but the Telegram bot is paused.")
        return False

    if not os.getenv("ADMIN_ID"):
        print("Warning: ADMIN_ID is not set. Bot will start, but admin access is disabled.", flush=True)

    return True


def start_process(name, command):
    print(f"Starting {name}: {' '.join(command)}", flush=True)
    process = subprocess.Popen(command)
    processes[name] = process


def run_bot():
    if not os.getenv("BOT_TOKEN"):
        print("Telegram bot skipped: BOT_TOKEN is not set.", flush=True)
        return
    start_process("Telegram bot", [sys.executable, "-m", "bot.main"])


def run_api():
    port = os.getenv("PORT") or os.getenv("API_PORT") or "5000"
    print(f"API/health server will bind to port {port}.", flush=True)
    start_process(
        "API/health server",
        [
            sys.executable,
            "-m",
            "gunicorn",
            "api.app:app",
            "--bind",
            f"0.0.0.0:{port}",
            "--workers",
            "1",
            "--threads",
            "8",
            "--timeout",
            "120",
        ],
    )


def shutdown(signum=None, frame=None):
    print("Shutting down services...", flush=True)
    for process in processes.values():
        if process.poll() is None:
            process.terminate()

    for process in processes.values():
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()

    sys.exit(0)


def restart_bot_if_needed():
    process = processes.get("Telegram bot")
    if process is None:
        return

    code = process.poll()
    if code is None:
        return

    print(f"Telegram bot exited with code {code}. Restarting in 30 seconds...", flush=True)
    time.sleep(30)
    run_bot()


if __name__ == "__main__":
    bot_configured = validate_config()
    signal.signal(signal.SIGTERM, shutdown)
    signal.signal(signal.SIGINT, shutdown)

    print("ProHub Bot - Starting services...", flush=True)
    run_api()
    if bot_configured:
        run_bot()
    print("All services started.", flush=True)

    while True:
        api_process = processes.get("API/health server")
        if api_process is not None:
            api_code = api_process.poll()
            if api_code is not None:
                print(f"API/health server exited with code {api_code}.", flush=True)
                shutdown()
        restart_bot_if_needed()
        time.sleep(1)
