#!/usr/bin/env bash

# Installs live.py as a service on the Raspberry Pi.

# Check if the device is a Raspberry Pi
if grep -q "Raspberry Pi" /proc/device-tree/model; then
    echo "Installing service on a Raspberry Pi..."
else
    echo "Error, service is only for the Raspberry Pi!"
    exit 1
fi

# Run from the directory of this script
cd "$( dirname "${BASH_SOURCE[0]}" )"

# live.py is expected to be one level up
cd ..
if [ ! -f live.py ]; then
    echo "Error, live.py is expected to be one level up from the installation script!"
    exit 1
fi

# Install a service definition
sudo tee /etc/systemd/system/live.service > /dev/null << EOF
[Unit]
Description=Live Service
After=multi-user.target         

[Service]
Type=simple
WorkingDirectory=$(pwd)
ExecStart=/usr/bin/python3 -u live.py  
Restart=on-failure
RestartSec=5s

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable live.service
sudo systemctl stop live.service
sudo systemctl start live.service

echo "Installation complete"