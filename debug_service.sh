#!/bin/bash

# Debug script for telegram-spam-bot service

echo "=== Telegram Spam Bot Debug Information ==="
echo ""

echo "1. Service Status:"
sudo systemctl status telegram-spam-bot --no-pager
echo ""

echo "2. Recent Logs (last 20 lines):"
sudo journalctl -u telegram-spam-bot -n 20 --no-pager
echo ""

echo "3. Error Logs Only:"
sudo journalctl -u telegram-spam-bot -p err -n 10 --no-pager
echo ""

echo "4. File Permissions:"
ls -la /home/martin/projects/tmp_telegram_spam_detection/*.py
ls -la /home/martin/projects/tmp_telegram_spam_detection/*.session 2>/dev/null
ls -la /home/martin/projects/tmp_telegram_spam_detection/telegram_bot.pid 2>/dev/null
echo ""

echo "5. Python Environment Check:"
/home/martin/projects/tmp_telegram_spam_detection/venv/bin/python --version
echo ""

echo "6. Can import modules?"
cd /home/martin/projects/tmp_telegram_spam_detection
/home/martin/projects/tmp_telegram_spam_detection/venv/bin/python -c "from naive_bayes_classifier import NaiveBayesClassifier; print('✓ Imports work')" 2>&1
echo ""

echo "7. Running Processes:"
ps aux | grep -E "main.py|telegram" | grep -v grep
echo ""

echo "=== End Debug Info ==="
