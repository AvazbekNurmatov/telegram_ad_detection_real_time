#!/bin/bash

# Stop the Telegram bot gracefully

PID_FILE="telegram_bot.pid"

# Kill any suspended jobs
jobs -p | xargs -r kill -9 2>/dev/null

if [ -f "$PID_FILE" ]; then
  PID=$(cat "$PID_FILE")

  if ps -p $PID >/dev/null 2>&1; then
    echo "Stopping bot (PID: $PID)..."
    kill -TERM $PID

    # Wait up to 5 seconds for graceful shutdown
    for i in {1..5}; do
      if ! ps -p $PID >/dev/null 2>&1; then
        echo "Bot stopped gracefully."
        rm -f "$PID_FILE"
        break
      fi
      sleep 1
    done

    # Force kill if still running
    if ps -p $PID >/dev/null 2>&1; then
      echo "Force killing bot..."
      kill -9 $PID 2>/dev/null
      rm -f "$PID_FILE"
      echo "Bot force stopped."
    fi
  else
    echo "Process $PID not found. Removing stale PID file."
    rm -f "$PID_FILE"
  fi
else
  echo "No PID file found. Bot may not be running."
  # Clean up any potential orphaned processes
  pkill -9 -f "python.*main.py"
fi

# Clean up lock files
rm -f telegram_bot_session.session-journal

# Fix session permissions
if [ -f "telegram_bot_session.session" ]; then
  chmod 664 telegram_bot_session.session
  echo "Fixed session file permissions."
fi

echo "Cleanup complete."
