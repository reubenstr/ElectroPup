# Main PC (Ubuntu)

pip install mujoco
python -m mujoco.viewer

python3 -m mujoco.viewer --mjcf=./electropup.xml 
python3 -m mujoco.viewer --mjcf=./scene.xml 

https://mujoco.readthedocs.io/en/stable/APIreference/index.html


Setup VSCode
Install these extensions:
Remote Explorer

Connect to the Raspberry Pi
Install these extensions
Python

Press Ctrl+Shift+P → "Python: Select Interpreter"
Look for Python 3.13.5 (3.13.5) ~/.pyenv/versions/3.13.5/bin/python

Press Ctrl+Shift+P → "Reload Window"

# Raspberry Pi

Hardware: Rasperry Pi 5 

Using Raspberry Pi Imager, select Raspberry Pi OS Lite, Bookworm 64-bit
Apply custom configuration:
hostname: electropup
username: pi
password: pi
SSID: <your-wifi-credentials>
password: <your-wifi-credentials>

## SSH

If the host is not found, try scanning for the IP using a tool like 'Angry IP Scanner'

Copy development PC's keys to RPI: 
ssh-copy-id pi@electropup.local

Login (should not prompt for password if keys are copied):
ssh pi@electropup.local


Update:
sudo apt update

Generate SSH key (press enter three times (default file location, blank passphrase)):
ssh-keygen 

Get the public key: 
cat ./.ssh/id_rsa.pub

Add public key to your github/gitlab/etc.


## Source

Install git:
sudo apt install -y git

Clone the ElectroPup repo:
git clone git@github.com:reubenstr/ElectroPup.git

## Python

sudo apt update
sudo apt install -y make build-essential libssl-dev zlib1g-dev \
libbz2-dev libreadline-dev libsqlite3-dev curl libncursesw5-dev \
xz-utils tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev git

curl https://pyenv.run | bash

These commands will add the required lines to .bashrc
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
echo 'eval "$(pyenv init --path)"' >> ~/.bashrc
echo 'eval "$(pyenv init -)"' >> ~/.bashrc

pyenv install 3.13

restart the terminal

Check for correct version:
cd ./ElectroPup/src
python --version

Setup venv
cd ./ElectroPup/src
python3.13 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip

### Dependancies



sudo apt update
sudo apt install python3-gpiozero
sudo apt install upower

cd ./ElectroPup/src
pip install -r requirements.txt


# CAN

CAN sheild: https://www.waveshare.com/2-ch-can-hat.htm

Installation and setup for Raspberry Pi:

Create temp directory for downloads:
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
# For More info: http://www.airspayce.com/mikem/bcm2835/

wget https://files.waveshare.com/upload/8/8c/WiringPi-master.zip
sudo apt-get install unzip
unzip WiringPi-master.zip
cd WiringPi-master/
sudo ./build 

Append these statements to /boot/firmware/config.txt:
dtparam=spi=on
dtoverlay=mcp2515-can1,oscillator=16000000,interrupt=25
dtoverlay=mcp2515-can0,oscillator=16000000,interrupt=23
dtoverlay=spi-bcm2835-overlay

Set up CAN:
sudo ip link set can0 up type can bitrate 1000000
sudo ip link set can1 up type can bitrate 1000000
sudo ifconfig can0 txqueuelen 65536
sudo ifconfig can1 txqueuelen 65536

Check for interfaces:
ifconfig

Loopback test, connect H to H, L to L:
sudo apt-get install can-utils
1st terminal:
	candump can0
2nd terminal:
	cansend can1 000#11.22.33.44
	cansend can1 141#8800000000000000
	cansend can1 141#8000000000000000

# UI

Install NVM:
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash

Test if installed:
nvm --version

Install node.js and npm:
nvm install --lts

Install packages:
cd ./ElectroPup/src/ui
npm install

Start app in development mode:
npm expo start --web



# Gamepad

Assumes the gamepad is a Playstation 4 controller.
The gamepad interface is setup for a PS4 controller but can be modified to accept any standard gamepad.

Reset the controller:
Power on the controller and press the button inside the hole on back rightside

sudo bluetoothctl
scan on

press and hold PS and Share button until controller flashes
wait for scan to show Wireless Controller and copy gamepad's MAC address
Example output: 
[NEW] Device 84:30:95:48:0F:3C Wireless Controller

scan off
pair  <mac-address> 
trust <mac-address>
connect <mac-address>

devices 
power cycle controller

Optional, check functionality, will show a stream of axis and button values:
sudo apt-get install joystick
jstest /dev/input/js0



# Serial 

Serial is for the Auxillary board which is optional hardware.

Append these statements to /boot/firmware/config.txt:
enable_uart=1
dtoverlay=uart0



## IMU

Enable I2C on the Raspberry Pi:
sudo raspi-config



# Manual Testing (or Development)

cd ./ElectroPup/src


# Tools

Create requirements.txt

cd ./ElectroPup/src

All packages
pip freeze > requirements.txt

Packages specific to project:
pip install pipreqs
pipreqs .




# TEMP: TO BE REMOVED OR ADDED
sudo apt-get update
sudo apt-get install python3-pil
sudo apt-get install python3-numpy
sudo apt-get install python3-RPi.GPIO
sudo apt-get install python3-spidev 
sudo apt-get install python3-python-can
sudo apt-get install can-utils

Kernal CAN docs: https://www.kernel.org/doc/Documentation/networking/can.txt



###############################################################################
# aux-board
###############################################################################

sudo nano /etc/udev/rules.d/99-dfu.rules
SUBSYSTEM=="usb", ATTR{idVendor}=="0483", ATTR{idProduct}=="df11", MODE="0666"
sudo udevadm control --reload-rules
sudo udevadm trigger
ls -l /dev/bus/usb/002/038  # Adjust the path based on your system's output

https://github.com/VermontCoder/read_sbus
https://www.digikey.com/en/products/detail/texas-instruments/SN74LVC1G14DBVT/1592006

https://github.com/riuson/lcd-image-converter
