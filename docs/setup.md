# Setup

Read the entire guide prior to beginning the setup procress as this document may not be sequential order.

# Development PC (Ubuntu)

The development PC is used to display UI, Mujoco simulation, and charts as well as remote into the Raspberry Pi for code development.

## Setup VSCode
Install VSCode along with extensions:
- Remote Explorer

Connect to the Raspberry Pi (after setup) using Remove Explorer and install these extensions:
- Python

Select the virtual environment's interpreter:

Press `Ctrl+Shift+P` → "Python: Select Interpreter"  
Look for (or similar):  

> Python 3.13.5 (3.13.5) ~/.pyenv/versions/3.13.5/bin/python

Press `Ctrl+Shift+P` → "Reload Window"

---

# Raspberry Pi

Hardware: Raspberry Pi 5  

Using Raspberry Pi Imager, select **Raspberry Pi OS Lite, Bookworm 64-bit**  
Apply custom configuration:
- hostname: `electropup`
- username: `pi`
- password: `pi`
- SSID: `<your-wifi-credentials>`
- password: `<your-wifi-credentials>`

## SSH

(If the host is not found, try scanning for the IP using a tool like *Angry IP Scanner*.) 

Copy the development PC's keys to RPI:
```bash
ssh-copy-id pi@electropup.local
```

Login (should not prompt for password if keys are copied):
```bash
ssh pi@electropup.local
```

Update:
```bash
sudo apt update
```

Generate SSH key (press enter three times for defaults):
```bash
ssh-keygen
```

Get the public key:
```bash
cat ./.ssh/id_rsa.pub
```

Optional: Add public key to GitHub/GitLab/etc.


## Source

Install git:
```bash
sudo apt install -y git
```

Clone the ElectroPup repo:
```bash
git clone git@github.com:reubenstr/ElectroPup.git
```


## Python

Install dependencies:
```bash
sudo apt update
sudo apt install -y make build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev curl libncursesw5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev git
```

Install pyenv:
```bash
curl https://pyenv.run | bash
```

Update `.bashrc`:

```bash
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
echo 'eval "$(pyenv init --path)"' >> ~/.bashrc
echo 'eval "$(pyenv init -)"' >> ~/.bashrc
```

Install Python:
```bash
pyenv install 3.13
```

Restart the terminal.  

Check version:
```bash
cd ./ElectroPup/src
python --version
```

Setup venv:
```bash
cd ./ElectroPup/src
python3.13 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
```

### Install Dependencies

```bash
sudo apt update
sudo apt install python3-gpiozero
sudo apt install upower
```
Run these commands while in the virtual environment from the above step.


```bash
cd ./ElectroPup/src
pip install -r requirements.txt
```


# CAN

CAN shield: [Waveshare 2-ch CAN HAT](https://www.waveshare.com/2-ch-can-hat.htm)

### Install bcm2835
```bash
cd ~
mkdir temp
cd temp

wget http://www.airspayce.com/mikem/bcm2835/bcm2835-1.60.tar.gz
tar zxvf bcm2835-1.60.tar.gz 
cd bcm2835-1.60/
sudo ./configure
sudo make
sudo make check
sudo make install
```

### Install WiringPi
```bash
wget https://files.waveshare.com/upload/8/8c/WiringPi-master.zip
sudo apt-get install unzip
unzip WiringPi-master.zip
cd WiringPi-master/
sudo ./build
```

Add these lines to `/boot/firmware/config.txt`

```bash
dtparam=spi=on
dtoverlay=mcp2515-can1,oscillator=16000000,interrupt=25
dtoverlay=mcp2515-can0,oscillator=16000000,interrupt=23
dtoverlay=spi-bcm2835-overlay
```

### Setup CAN
```bash
sudo ip link set can0 up type can bitrate 1000000
sudo ip link set can1 up type can bitrate 1000000
sudo ifconfig can0 txqueuelen 65536
sudo ifconfig can1 txqueuelen 65536
```

Check for interfaces:
```bash
ifconfig
```

### Loopback Test

Optional: check communications by connecting can0 and can1 together and running these commands.

```bash
sudo apt-get install can-utils
```

Terminal 1:
```bash
candump can0
```

Terminal 2:
```bash
cansend can1 000#11.22.33.44
cansend can1 141#8800000000000000
cansend can1 141#8000000000000000
```


# Gamepad

Assumes a Playstation 4 controller.  

Reset the controller by powering on the controller then pressing the button inside the hole on back rightside.  

On the Raspberry Pi

```bash
sudo bluetoothctl
scan on
```

Press and hold **PS + Share** until flashing.  
Example scan output:  

> [NEW] Device 84:30:95:48:0F:3C Wireless Controller


Pair and connect:
```bash
scan off
pair <mac-address>
trust <mac-address>
connect <mac-address>
devices
```

Power cycle controller.  

Optional test:
```bash
sudo apt-get install joystick
jstest /dev/input/js0
```

# Serial 

Serial is for the Auxillary board which is optional hardware.

Append to `/boot/firmware/config.txt`:
```bash
enable_uart=1
dtoverlay=uart0
```

# IMU

Enable I2C using `raspi-config`.  

```bash
sudo raspi-config
```


Scan for attached I2C hardware:
```bash
sudo apt install i2c-tools
ls /dev/i2c-*
i2cdetect -y 1
```

Or use the scanner script:
```bash
./src/system/hardware/i2c_scanner.py
```

BNO055 address is `0x28`.

# Run in Development Mode

Since the project uses virtual environments, shell scripts are used as helpers to start the virtual environments and start the Python scripts.

```bash
cd ./ElectroPup/src/ui
```

Run the UI server
```bash
sudo ./server.sh
```

Run the Heartbeat (if the Auxilary board is being used)
```bash
sudo ./heartbeat.sh
```

Run the main application
```bash
sudo ./main.sh --dev
```

The main application requires either the `--live` or the `--dev` argument

`--dev`: does not allow motors to enable and start in a walking gait

`--live`: allows motors to enable and start in a sitting pose.

### Other arugments

These following argments can be passed to stop, start, and restart the main service as a helper during development

- --stop
- --start
- --reset

# Install Services (Live Mode)

There are three services that will automatically run the main script, the server for the UI, and the heartbeat for the auxilary board.

Install the services

```bash
cd ./ElectroPup/src/setup
./install_main.sh
./install_server.sh
./install_heartbeat.sh

```

Check the status of a service (main service as an example)
```bash
sudo systemctl status main.service 
```

Stop a service
```bash
sudo systemctl stop main.service 
```

Start a service
```bash
sudo systemctl start main.service 
```

Reset a service
```bash
sudo systemctl reset main.service 
```

View services logs live
```bash
sudo journalctl -u main.service -f
```

---

# Motor Zeroing

To zero the motors run the zeroing script

```bash
cd ./ElectroPup/src
sudo ./zero.sh
```

---

# UI

On development PC (Raspberry PI is capable of running but is slow for rapid development)

Install NVM:
```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
```

Check:
```bash
nvm --version
```

Install node.js and npm:
```bash
nvm install --lts
```

Install packages:
```bash
cd ./ElectroPup/src/ui
npm install
```

Start app in development mode:
```bash
npm expo start --web
```


Build app for web (exports to ./src/ui/dist):
```bash
npx expo export --platform web
```

---

# Simulation / Mujoco

On Desktop development PC  

Install mujoco:
```bash
pip install mujoco
```

Run viewer (no model):
```bash
python -m mujoco.viewer
```

Run viewer with ElectroPup scene:
```bash
python3 -m mujoco.viewer --mjcf=<path-to-scene>
python3 -m mujoco.viewer --mjcf=~/Desktop/projects/ElectroPup/src/model/scene.xml
```

[Mujoco API reference](https://mujoco.readthedocs.io/en/stable/APIreference/index.html)

---

# Tools

## Requirements

Create `requirements.txt`:

```bash
cd ./ElectroPup/src
```

All packages:
```bash
pip freeze > requirements.txt
```

Project-specific packages:
```bash
pip install pipreqs
pipreqs .
```