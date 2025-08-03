#!/bin/bash


# Activate the virtual environment
if [ -f ".venv/bin/activate" ]; then
    echo "Activating virtual environment..."
else
    echo "Virtual environment activation script not found." >&2
    exit 1
fi
source .venv/bin/activate

if [ -f "./system/zero.py" ]; then
    echo "Starting zero..."
else
    echo "Zero script not found." >&2
    exit 1
fi

exec python3 system/zero.py