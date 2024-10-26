#!/usr/bin/env python3

"""

Generates a heartbeat signal (square wave) that allows the auxiliary board 
to determine if the Raspberry Pi is booted and operational.

Use the install_heartbeat.sh script to install this script as a service.

"""

import time
import RPi.GPIO as GPIO

pin_number = 17
rate = 0.025

try:
    print(f"[Heartbeat] starting heartbeat")
    
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(pin_number, GPIO.OUT)
    
    while True:       
        GPIO.output(pin_number, GPIO.HIGH)
        time.sleep(rate)      
        GPIO.output(pin_number, GPIO.LOW)
        time.sleep(rate)
except:
    GPIO.cleanup()