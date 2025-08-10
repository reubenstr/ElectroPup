#!/usr/bin/env bash

# Installs a service on the Raspberry Pi that generates a heartbeat signal for the auxiliary display board.

# Check if the device is a Raspberry Pi
if grep -q "Raspberry Pi" /proc/device-tree/model; then
    echo "Installing service on a Raspberry Pi..."
else
    echo "Error, heartbeat service is only for the Raspberry Pi!"
    exit 1
fi

# Run from the directory of this script
cd "$( dirname "${BASH_SOURCE[0]}" )"

# Install a service definition
sudo tee /etc/systemd/system/heartbeat.service > /dev/null << EOF
[Unit]
Description=Heartbeat Service
After=multi-user.target         

[Service]
Type=simple
WorkingDirectory=$(pwd)
ExecStart=$HOME/ElectroPup/src/heartbeat.sh
Restart=on-failure
RestartSec=5s

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable heartbeat.service
sudo systemctl stop heartbeat.service
sudo systemctl start heartbeat.service

echo "Installation complete"

echo "To see live service logs, run: sudo journalctl -u server.service -f"