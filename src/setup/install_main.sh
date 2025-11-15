#!/usr/bin/env bash

# Installs a service on the Raspberry Pi that runs main application.

# Check if the device is a Raspberry Pi
if grep -q "Raspberry Pi" /proc/device-tree/model; then
    echo "Installing service on a Raspberry Pi..."
else
    echo "Error, main service is only for the Raspberry Pi!"
    exit 1
fi

# Run from the directory of this script
cd "$( dirname "${BASH_SOURCE[0]}" )"

# Install a service definition
sudo tee /etc/systemd/system/main.service > /dev/null << EOF
[Unit]
Description=Main Service
After=multi-user.target         

[Service]
Type=simple
WorkingDirectory=$HOME/ElectroPup/src
ExecStart=$HOME/ElectroPup/src/main.sh --service
Restart=on-failure
RestartSec=5s

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable main.service
sudo systemctl stop main.service
sudo systemctl start main.service

echo "Installation complete"
echo "Run this command to see the service status: sudo systemctl status main.service"
echo "Run this command to see live logs: sudo journalctl -u main.service -f"