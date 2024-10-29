#!/usr/bin/env python3

"""
    Scans for attached devices on the I2C bus.   
"""

import smbus
import time

def scan_i2c_bus(bus_number=1):
    bus = smbus.SMBus(bus_number)
    print("Scanning I2C bus...")

    devices_found = []
    for address in range(128):  # I2C addresses range from 0 to 127
        try:
            bus.write_byte(address, 0)  # Try to write to the address
            devices_found.append(hex(address))  # If successful, add to list
        except OSError:
            pass  # No device at this address

    return devices_found

###############################################################################
# Entry
###############################################################################
if __name__ == "__main__":
    found_devices = scan_i2c_bus()
    if found_devices:
        print("Devices found:")
        for device in found_devices:
            print(device)
    else:
        print("No I2C devices found.")
