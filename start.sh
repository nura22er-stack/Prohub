#!/bin/bash

# ProHub Bot Starter Script for Linux/Mac

echo "======================================"
echo "  ProHub Bot - Starting Services"
echo "======================================"
echo ""

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "ERROR: .env file not found!"
    echo "Please copy .env.example to .env and configure it."
    echo ""
    exit 1
fi

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate venv
source venv/bin/activate

# Install requirements
pip install -q -r requirements-dev.txt

echo ""
echo "Starting ProHub Bot services..."
echo ""

# Start bot
python3 -m bot.main &
BOT_PID=$!

# Start API
python3 api/app.py &
API_PID=$!

echo ""
echo "Services started with PIDs:"
echo "- Bot PID: $BOT_PID"
echo "- API PID: $API_PID"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Wait for Ctrl+C
wait

# Cleanup
kill $BOT_PID $API_PID 2>/dev/null
echo "All services stopped."
