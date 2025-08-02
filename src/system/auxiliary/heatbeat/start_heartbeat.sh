#!/bin/bash

# Set up pyenv
export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init --path)"
eval "$(pyenv init -)"

# Use pyenv to set the correct Python version
pyenv shell 3.13.5

# Activate the local virtual environment (.venv)
source /home/pi/ElectroPup/src/.venv/bin/activate

# Navigate to your working directory
cd /home/pi/ElectroPup/src/system/auxiliary/heatbeat

# Run your script
python -u heartbeat.py