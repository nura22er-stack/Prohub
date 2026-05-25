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


processes = []


def has_render_env():
    """Render provides env vars directly instead of a local .env file."""
    return bool(os.getenv("RENDER") or os.getenv("PORT"))


def validate_config():
    """Fail early with clear messages for missing required settings."""
    if os.path.exists(".env"):
        return

    if not has_render_env():
        print("Error: .env file not found!")
        print("Local run uchun .env.example ni .env ga nusxalang va to'ldiring.")
        sys.exit(1)

    missing = [name for name in ("BOT_TOKEN", "ADMIN_ID") if not os.getenv(name)]
    if missing:
        print("Error: required Render environment variables are missing:")
        for name in missing:
            print(f"- {name}")
        sys.exit(1)


def start_process(name, command):
    print(f"Starting {name}: {' '.join(command)}", flush=True)
    process = subprocess.Popen(command)
    processes.append((name, process))


def run_bot():
    start_process("Telegram bot", [sys.executable, "-m", "bot.main"])


def run_api():
    port = os.getenv("PORT") or os.getenv("API_PORT") or "5000"
    print(f"API/health server will bind to port {port}.", flush=True)
    start_process("API/health server", [sys.executable, "api/app.py"])


def shutdown(signum=None, frame=None):
    print("Shutting down services...", flush=True)
    for _, process in processes:
        if process.poll() is None:
            process.terminate()

    for _, process in processes:
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()

    sys.exit(0)


if __name__ == "__main__":
    validate_config()
    signal.signal(signal.SIGTERM, shutdown)
    signal.signal(signal.SIGINT, shutdown)

    print("ProHub Bot - Starting services...", flush=True)
    run_bot()
    run_api()
    print("All services started.", flush=True)

    while True:
        for name, process in processes:
            code = process.poll()
            if code is not None:
                print(f"{name} exited with code {code}.", flush=True)
                shutdown()
        time.sleep(1)
