#!/bin/bash
PYTHON_VERSION="3.13.5"

# Set up pyenv
export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init --path)"
eval "$(pyenv init -)"

# Check if the correct Python version is installed
if ! pyenv versions --bare | grep -q "^${PYTHON_VERSION}$"; then
    echo "Python version ${PYTHON_VERSION} is not installed via pyenv."
    exit 1
fi

# Set and activate Python version
pyenv shell "$PYTHON_VERSION"

# Activate the local virtual environment (.venv)
source /home/pi/ElectroPup/src/.venv/bin/activate

# Navigate to your working directory
cd /home/pi/ElectroPup/src/system/auxiliary/heatbeat

# Run your script
python -u heartbeat.py