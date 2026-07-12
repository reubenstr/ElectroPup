#!/bin/bash

# Run from the directory of this script
cd "$( dirname "${BASH_SOURCE[0]}" )"

# Activate the virtual environment
if [ -f ".venv/bin/activate" ]; then
    echo "Activating virtual environment..."
else
    echo "Virtual environment activation script not found." >&2
    exit 1
fi
source .venv/bin/activate

if [ -f "./system/auxiliary/heartbeat/heartbeat.py" ]; then
    echo "Starting heartbeat..."
else
    echo "Heartbeat script not found." >&2
    exit 1
fi

exec python3 -u system/auxiliary/heartbeat/heartbeat.py
