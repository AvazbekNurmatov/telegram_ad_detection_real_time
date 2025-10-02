#!/bin/bash

# Installation script for Telegram Spam Bot service

SERVICE_NAME="telegram-spam-bot"
SERVICE_FILE="${SERVICE_NAME}.service"
SYSTEMD_PATH="/etc/systemd/system/${SERVICE_FILE}"

echo "Installing Telegram Spam Bot as a system service..."

# Check if running as root or with sudo
if [ "$EUID" -ne 0 ]; then
  echo "Please run with sudo: sudo ./install_service.sh"
  exit 1
fi

# Check if service file exists in current directory
if [ ! -f "$SERVICE_FILE" ]; then
  echo "Error: ${SERVICE_FILE} not found in current directory"
  exit 1
fi

# Stop service if already running
if systemctl is-active --quiet $SERVICE_NAME; then
  echo "Stopping existing service..."
  systemctl stop $SERVICE_NAME
fi

# Copy service file to systemd directory
echo "Installing service file..."
cp $SERVICE_FILE $SYSTEMD_PATH
chmod 644 $SYSTEMD_PATH

# Reload systemd daemon
echo "Reloading systemd daemon..."
systemctl daemon-reload

# Enable service to start on boot
echo "Enabling service to start on boot..."
systemctl enable $SERVICE_NAME

# Start the service
echo "Starting service..."
systemctl start $SERVICE_NAME

# Check status
echo ""
echo "Service installed successfully!"
echo ""
echo "Service status:"
systemctl status $SERVICE_NAME --no-pager

echo ""
echo "Useful commands:"
echo "  View logs:        sudo journalctl -u $SERVICE_NAME -f"
echo "  Check status:     sudo systemctl status $SERVICE_NAME"
echo "  Stop service:     sudo systemctl stop $SERVICE_NAME"
echo "  Start service:    sudo systemctl start $SERVICE_NAME"
echo "  Restart service:  sudo systemctl restart $SERVICE_NAME"
echo "  Disable autostart: sudo systemctl disable $SERVICE_NAME"
echo "  Uninstall:        sudo ./uninstall_service.sh"
