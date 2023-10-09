#!/bin/bash

# GitHub repository URL and script options, do not change!!
REPO_URL="https://github.com/bernardolankheet/trmm-telegram.git"
SCRIPT_NAME="telegram-trmm.py"
INSTALL_DIR="/opt/trmm-telegram" # Installation directory
INSTALL_DIR_LOG="/var/log/trmm-telegram" # log directory
SYSTEMD_DIR="/etc/systemd/system" # systemd services directory
SERVICE_NAME="trmm-telegram.service" # systemd service name
SERVICE_USER="tactical" # Tactical service user in systemd
PIP_VERSION=3.11

# Validations to check that Python3, pip and configparser are installed and that the script runs as root
if [[ $EUID -ne 0 ]]; then
    echo "This script must be run as root or with sudo privileges."
    exit 1
fi

if ! which python3 &> /dev/null; then
    echo "Python3 is not installed. Install it before proceeding."
    exit 1
fi

if ! pip"$PIP_VERSION" show configparser &> /dev/null; then
    echo "configparser is not installed. Installing..."
    pip$PIP_VERSION install configparser
fi

# Create the installation and log directory
if [ ! -d "$INSTALL_DIR" ]; then
    mkdir -p "$INSTALL_DIR"
    mkdir -p "$INSTALL_DIR_LOG"
fi

# Cloning the GitHub repository
if ! git clone "$REPO_URL" "$INSTALL_DIR"; then
    echo "Error cloning GitHub repository."
    exit 1
fi

# Creating systemd service file
cat > "$SYSTEMD_DIR/$SERVICE_NAME" <<EOF
[Unit]
Description=Script trmm-telegram

[Service]
ExecStart=/usr/bin/python3 $INSTALL_DIR/$SCRIPT_NAME
Restart=always
RestartSec=10
User=$SERVICE_USER

[Install]
WantedBy=multi-user.target
EOF

# Applying directory permissions to the tactical user
chown -R $SERVICE_USER:$SERVICE_USER $INSTALL_DIR
chown -R $SERVICE_USER:$SERVICE_USER $INSTALL_DIR_LOG

if [ -f "$SYSTEMD_DIR/$SERVICE_NAME" ]; then
    echo "Systemd Service file created successfully: $SYSTEMD_DIR/$SERVICE_NAME"
else
    echo "Error creating systemd service file."
    exit 1
fi

# Reload systemd daemon
systemctl daemon-reload

if systemctl enable "$SERVICE_NAME"; then
    echo "Service enabled: $SERVICE_NAME"
else
    echo "Error enabling systemd service."
    exit 1
fi

# Check service status
systemctl status "$SERVICE_NAME"

## 
echo "==========================================================================================================="
echo "Script trmm-telegram installed and configured as a service."
echo "Configure the configuration file with your Tactical and Telegram data. $INSTALL_DIR/configScrips.ini"
echo "To restart the service when parameters are updated, use: systemctl restart $SERVICE_NAME"
echo "To start the service: systemctl start $SERVICE_NAME"
echo "To stop the service: systemctl stop $SERVICE_NAME"
echo "To view logs: tail -f $INSTALL_DIR_LOG/trmm-telegram.log"
echo "==========================================================================================================="
