#!/usr/bin/env python3
from time import sleep
import gpiod
from gpiod import request_lines, LineSettings
from gpiod.line import  Direction, Value

"""

Generates a heartbeat signal (square wave) that allows the auxiliary board 
to determine if the Raspberry Pi is booted.

Use the install_heartbeat.sh script to install this script as a service.

"""

HEARTBEAT_PIN = 17
RATE_SECONDS = 0.025

try:
    print(f"[Heartbeat] starting squarewave signal on pin {HEARTBEAT_PIN} at a rate of {1/RATE_SECONDS}Hz")
       
    gpio_lines = request_lines(
        "/dev/gpiochip0",
        consumer="gpio-controller",
        config={
            HEARTBEAT_PIN: LineSettings(
                direction=Direction.OUTPUT,
                output_value=Value.ACTIVE
            ),           
        }
    )     
    
    state = True
    while True:       
        state = not state
        gpio_lines.set_value(HEARTBEAT_PIN, Value.ACTIVE if state == 1 else Value.INACTIVE)
        sleep(RATE_SECONDS)
        
except Exception as e:
    print(f"Exception occurred: {e}")
    exit()