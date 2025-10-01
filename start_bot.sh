#!/bin/bash

# Start the Telegram bot with proper cleanup

PID_FILE="telegram_bot.pid"

# Function to cleanup on exit
cleanup() {
  echo "Cleaning up..."
  rm -f "$PID_FILE"
  rm -f telegram_bot_session.session-journal
}

# Register cleanup on script exit
trap cleanup EXIT INT TERM

# Check if already running
if [ -f "$PID_FILE" ]; then
  OLD_PID=$(cat "$PID_FILE")
  if ps -p $OLD_PID >/dev/null 2>&1; then
    echo "Bot is already running (PID: $OLD_PID)"
    echo "Stop it first with: ./stop_bot.sh"
    exit 1
  else
    echo "Removing stale PID file..."
    rm -f "$PID_FILE"
  fi
fi

# Start the bot
echo "Starting Telegram bot..."
venv/bin/python main.py
