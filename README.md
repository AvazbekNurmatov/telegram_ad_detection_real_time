# Telegram Spam Detection Bot

Automated spam detection and blocking bot for Telegram using Naive Bayes classification and Telethon.

## Features

- 🤖 **Automatic Spam Detection**: Uses machine learning (Naive Bayes) to classify messages
- 🚫 **Auto-blocking**: Automatically blocks detected spammers
- 🗑️ **Message Cleanup**: Deletes spam messages and chat history
- 👥 **Contact Whitelist**: Never blocks your existing contacts
- 🔄 **Auto-restart**: Runs as a systemd service with automatic recovery
- 📝 **Logging**: Full logging to system journal

## How It Works

1. Bot listens for incoming private messages on Telegram
2. Checks if sender is in your contacts list
   - If yes: Message passes through (trusted contact)
   - If no: Runs spam detection classifier
3. If message is classified as spam:
   - Deletes the spam message
   - Deletes entire chat history with that user
   - ~~Reports user to Telegram as spam~~ (disabled in testing mode)
   - Blocks the user permanently
4. User becomes completely invisible in your chat list

## Requirements

- Ubuntu/Debian Linux (systemd-based)
- Python 3.8+
- Telegram API credentials (from https://my.telegram.org)
- Active Telegram account

## Installation

### 1. Clone and Setup

```bash
cd /home/martin/projects/tmp_telegram_spam_detection

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure API Credentials

Edit `main.py` and add your credentials:

```python
api_id = YOUR_API_ID        # From my.telegram.org
api_hash = 'YOUR_API_HASH'  # From my.telegram.org
```

### 3. First Run (Authentication)

**Important**: Before installing as a service, you must authenticate manually:

```bash
# Run manually first
./start_bot.sh

# You'll be prompted for:
# 1. Your phone number (with country code, e.g., +1234567890)
# 2. OTP code (sent to your Telegram app)

# Once authenticated, stop it
./stop_bot.sh
```

This creates the session file (`telegram_bot_session.session`) which persists your login.

### 4. Install as System Service

```bash
# Make scripts executable
chmod +x install_service.sh uninstall_service.sh start_bot.sh stop_bot.sh

# Install the service
sudo ./install_service.sh
```

The bot will now:
- ✅ Start automatically on boot
- ✅ Run in background 24/7
- ✅ Auto-restart if it crashes
- ✅ Stop gracefully on shutdown

## Usage

### Manual Control

```bash
# Start the bot (foreground)
./start_bot.sh

# Stop the bot
./stop_bot.sh
```

### Service Control

```bash
# Check if running
sudo systemctl status telegram-spam-bot

# Start service
sudo systemctl start telegram-spam-bot

# Stop service
sudo systemctl stop telegram-spam-bot

# Restart service
sudo systemctl restart telegram-spam-bot

# Enable autostart on boot (default)
sudo systemctl enable telegram-spam-bot

# Disable autostart
sudo systemctl disable telegram-spam-bot
```

### View Logs

```bash
# Live logs (press Ctrl+C to stop)
sudo journalctl -u telegram-spam-bot -f

# Last 50 lines
sudo journalctl -u telegram-spam-bot -n 50

# Last 24 hours
sudo journalctl -u telegram-spam-bot --since "24 hours ago"

# Only errors
sudo journalctl -u telegram-spam-bot -p err

# Logs with timestamps
sudo journalctl -u telegram-spam-bot -o short-precise
```

## Monitoring

### Check Service Status

```bash
sudo systemctl status telegram-spam-bot
```

**Status meanings**:
- `active (running)` - ✅ Bot is working
- `inactive (dead)` - ⚠️ Bot is stopped
- `failed` - ❌ Bot crashed, check logs
- `activating (auto-restart)` - 🔄 Restarting after failure

### Watch Real-time Activity

```bash
# See what the bot is doing right now
sudo journalctl -u telegram-spam-bot -f
```

You'll see:
```
Client started! Listening for messages from users only...
New message received from user 123456789: [message text]
✓ Deleted spam message from user 123456789
✓ Deleted entire chat history with user 123456789
⚠ Spam reporting disabled (testing mode)
✓ Blocked user 123456789
✅ Successfully removed all traces of spammer 123456789
```

### Debug Issues

```bash
# Run the debug script
./debug_service.sh

# Or manually check:
sudo journalctl -u telegram-spam-bot -n 100 --no-pager
```

## Configuration

### Enable Spam Reporting (Production Mode)

When ready to report spammers to Telegram, edit `main.py`:

Find this section:
```python
# Step 3: Report as spam to Telegram (COMMENTED OUT FOR TESTING)
# Uncomment the lines below when ready for production
# await client(ReportSpamRequest(peer=sender))
# print(f"✓ Reported user {user_id} as spam to Telegram")
```

Uncomment to enable:
```python
# Step 3: Report as spam to Telegram
await client(ReportSpamRequest(peer=sender))
print(f"✓ Reported user {user_id} as spam to Telegram")
```

Then restart:
```bash
sudo systemctl restart telegram-spam-bot
```

### Update Contact List

The bot uses `telegram_contacts.csv` to whitelist your contacts. To update:

```bash
# Regenerate contacts list
python create_list_contacts.py

# Restart bot to reload
sudo systemctl restart telegram-spam-bot
```

### Train Spam Classifier

To improve spam detection, retrain the model with your own data:

```python
# Edit and run naive_bayes_classifier.py
python naive_bayes_classifier.py
```

This updates `naive_bayes_model.pkl`.

## File Structure

```
tmp_telegram_spam_detection/
├── main.py                          # Main bot code
├── naive_bayes_classifier.py        # ML classifier
├── naive_bayes_model.pkl           # Trained model
├── create_list_contacts.py         # Contact list generator
├── telegram_contacts.csv           # Your contacts (whitelist)
├── telegram_bot_session.session    # Auth session (don't delete!)
├── telegram_bot.pid                # Process ID file
├── start_bot.sh                    # Manual start script
├── stop_bot.sh                     # Manual stop script
├── install_service.sh              # Service installer
├── uninstall_service.sh            # Service remover
├── debug_service.sh                # Debug tool
├── telegram-spam-bot.service       # Systemd service file
├── requirements.txt                # Python dependencies
├── README.md                       # This file
└── venv/                           # Virtual environment
```

## Troubleshooting

### Issue: "Another instance is already running"

**Solution**:
```bash
pkill -9 -f main.py
rm -f telegram_bot.pid telegram_bot_session.session-journal
sudo systemctl restart telegram-spam-bot
```

### Issue: "database is locked"

**Solution**:
```bash
rm -f telegram_bot_session.session-journal
sudo systemctl restart telegram-spam-bot
```

### Issue: Bot asks for phone/OTP every time

**Solution**: Session file missing or corrupted
```bash
# Re-authenticate manually
./stop_bot.sh
sudo systemctl stop telegram-spam-bot
./start_bot.sh  # Enter phone + OTP
# Then reinstall service
sudo ./install_service.sh
```

### Issue: Service won't start

**Solution**:
```bash
# Check detailed error
sudo journalctl -u telegram-spam-bot -n 50

# Fix permissions
chmod 664 telegram_bot_session.session
chown martin:martin telegram_bot_session.session

# Verify Python environment
venv/bin/python --version
venv/bin/python -c "import telethon; print('OK')"
```

### Issue: Bot blocks legitimate users

**Solution**: Update your contacts list and retrain the model
```bash
# Update contacts
python create_list_contacts.py

# Manually unblock user in Telegram
# Then retrain classifier with better data
```

## Uninstallation

```bash
# Stop and remove service
sudo ./uninstall_service.sh

# Or manually:
sudo systemctl stop telegram-spam-bot
sudo systemctl disable telegram-spam-bot
sudo rm /etc/systemd/system/telegram-spam-bot.service
sudo systemctl daemon-reload
```

## Security Notes

- ⚠️ **Never share** `telegram_bot_session.session` - it's like your password
- ⚠️ **Add to .gitignore**: `*.session`, `*.session-journal`, `telegram_bot.pid`
- ⚠️ **API credentials** should be kept secret
- ✅ Service runs as user `martin`, not root (more secure)
- ✅ Session file is encrypted by Telethon

## Performance

- **Memory usage**: ~100-150 MB
- **CPU usage**: < 1% when idle, ~5% when processing messages
- **Network**: Minimal (only when receiving/sending messages)
- **Disk**: Session file ~30 KB

## Support

- Telethon docs: https://docs.telethon.dev
- Telegram API: https://core.telegram.org/api
- Issues: Check logs with `sudo journalctl -u telegram-spam-bot -f`

## License

This project is for personal use. Ensure compliance with Telegram's Terms of Service.

---

**Version**: 1.0  
**Last Updated**: October 2025  
**Author**: Martin
