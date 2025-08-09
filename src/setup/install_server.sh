#!/usr/bin/env bash

# Installs a service on the Raspberry Pi that runs the server that provides data to the UI.

# Check if the device is a Raspberry Pi
if grep -q "Raspberry Pi" /proc/device-tree/model; then
    echo "Installing service on a Raspberry Pi..."
else
    echo "Error, server service is only for the Raspberry Pi!"
    exit 1
fi

# Run from the directory of this script
cd "$( dirname "${BASH_SOURCE[0]}" )"

# Install a service definition
sudo tee /etc/systemd/system/server.service > /dev/null << EOF
[Unit]
Description=Server Service
After=multi-user.target         

[Service]
Type=simple
WorkingDirectory=$HOME/ElectroPup/src
ExecStart=$HOME/ElectroPup/src/server.sh
Restart=on-failure
RestartSec=5s

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable server.service
sudo systemctl stop server.service
sudo systemctl start server.service

echo "Installation complete"