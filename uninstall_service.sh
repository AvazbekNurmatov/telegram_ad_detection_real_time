#!/bin/bash

# Uninstallation script for Telegram Spam Bot service

SERVICE_NAME="telegram-spam-bot"
SYSTEMD_PATH="/etc/systemd/system/${SERVICE_NAME}.service"

echo "Uninstalling Telegram Spam Bot service..."

# Check if running as root or with sudo
if [ "$EUID" -ne 0 ]; then
  echo "Please run with sudo: sudo ./uninstall_service.sh"
  exit 1
fi

# Stop the service
if systemctl is-active --quiet $SERVICE_NAME; then
  echo "Stopping service..."
  systemctl stop $SERVICE_NAME
fi

# Disable the service
if systemctl is-enabled --quiet $SERVICE_NAME; then
  echo "Disabling service..."
  systemctl disable $SERVICE_NAME
fi

# Remove service file
if [ -f "$SYSTEMD_PATH" ]; then
  echo "Removing service file..."
  rm $SYSTEMD_PATH
fi

# Reload systemd daemon
echo "Reloading systemd daemon..."
systemctl daemon-reload
systemctl reset-failed

echo "Service uninstalled successfully!"
