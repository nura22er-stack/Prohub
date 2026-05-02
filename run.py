#!/usr/bin/env python3
"""
ProHub Bot - Main Entry Point
Run bot, API, and website servers
"""

import subprocess
import os
import sys
from pathlib import Path

def run_bot():
    """Run Telegram bot"""
    print("🤖 Starting ProHub Bot...")
    subprocess.Popen([sys.executable, 'bot/main.py'])

def run_api():
    """Run API server"""
    print("📡 Starting API server on port 5000...")
    subprocess.Popen([sys.executable, 'api/app.py'])

def run_website():
    """Run website server"""
    print("🌐 Starting website on port 5001...")
    subprocess.Popen([sys.executable, 'website/api_app.py'])

if __name__ == '__main__':
    # Check .env file
    if not os.path.exists('.env'):
        print("❌ Error: .env file not found!")
        print("Please copy .env.example to .env and fill in your credentials.")
        sys.exit(1)
    
    print("ProHub Bot - Starting all services...")
    print("-" * 50)
    
    # Start services
    run_bot()
    run_api()
    
    print("-" * 50)
    print("✅ All services started!")
    print("🤖 Bot: Running in background")
    print("📡 API: http://localhost:5000")
    print("🌐 Website: http://localhost:5001")
    print("\nPress Ctrl+C to stop all services")
    
    try:
        import time
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n❌ Shutting down all services...")
        sys.exit(0)
