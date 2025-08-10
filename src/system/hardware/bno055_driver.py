#!/usr/bin/env python3

import smbus
from smbus2 import SMBus
from time import sleep

# BNO005 I2C address
BNO055_ADDR = 0x28  # Change if your address is different

# Modes
CONFIGMODE = 0b00000000
ACCONLY = 0b00000001
NDOF = 0b00001100

# Register addresses
SYS_TRIGGER = 0x3F
OPR_MODE = 0x3D
TEMPERATURE_REGISTER = 0x34
CALIB_STAT = 0x35
ST_RESULT = 0x36
ACCEL_DATA = 0x08
GYRO_DATA = 0x0C
MAG_DATA = 0x0E
EULER_H_LSB = 0x1A  # heading LSB register

class BNO055:
    def __init__(self, bus):       
        self.bus = bus

    ###############################################################################
    # Read/Write Registers
    ###############################################################################

    def write_register(self, register, value):
        self.bus.write_byte_data(BNO055_ADDR, register, value)
    
    def read_register(self, register):
        return self.bus.read_byte_data(BNO055_ADDR, register)
    
    def read_data(self, register):        
        data = self.bus.read_i2c_block_data(BNO055_ADDR, register, 6)
        return data
        
    ###############################################################################
    # Methods
    ###############################################################################

    def reset(self):
        self.write_register(SYS_TRIGGER, 0b01100000)
        sleep(1.0)
        
    def start_self_test(self):
        self.write_register(SYS_TRIGGER, 0b00000001)
        sleep(1)
        
        result = self.read_register(ST_RESULT)
        
        accel_test = (result & 0x01) != 0
        mag_test = (result & 0x02) != 0
        gyro_test = (result & 0x04) != 0
        system_test = (result & 0x08) != 0

        print("Self-Test Results:")
        print(f"  Accelerometer: {'Passed' if accel_test else 'Failed'}")
        print(f"  Magnetometer:  {'Passed' if mag_test else 'Failed'}")
        print(f"  Gyroscope:     {'Passed' if gyro_test else 'Failed'}")
        print(f"  System:        {'Passed' if system_test else 'Failed'}")

    def set_mode(self, mode):
        self.write_register(OPR_MODE, mode)
        sleep(1) 
        
    def get_calibration_status(self):
        calib = self.read_register(CALIB_STAT)
        sys = (calib >> 6) & 0x03
        gyro = (calib >> 4) & 0x03
        accel = (calib >> 2) & 0x03
        mag = calib & 0x03
        return sys, gyro, accel, mag

    
    def get_temperature(self):        
        temperature = self.read_register(TEMPERATURE_REGISTER)
        return temperature
 
    def get_acceleration(self):
        data = self.read_data(ACCEL_DATA)
        ax = self.convert_to_signed((data[1] << 8) | data[0])
        ay = self.convert_to_signed((data[3] << 8) | data[2])
        az = self.convert_to_signed((data[5] << 8) | data[4])
        return ax, ay, az

    def get_gyroscope(self):
        data = self.read_data(GYRO_DATA)
        gx = self.convert_to_signed((data[1] << 8) | data[0])
        gy = self.convert_to_signed((data[3] << 8) | data[2])
        gz = self.convert_to_signed((data[5] << 8) | data[4])
        return gx, gy, gz

    def get_magnetometer(self):
        data = self.read_data(MAG_DATA)
        mx = self.convert_to_signed((data[1] << 8) | data[0])
        my = self.convert_to_signed((data[3] << 8) | data[2])
        mz = self.convert_to_signed((data[5] << 8) | data[4])
        return mx, my, mz
    

    def get_euler_angles(self):
        data = self.read_data(EULER_H_LSB)
        heading = self.convert_to_signed(data[1] << 8 | data[0]) / 16.0
        roll = self.convert_to_signed(data[3] << 8 | data[2]) / 16.0
        pitch = self.convert_to_signed(data[5] << 8 | data[4]) / 16.0
        return heading, roll, pitch
   
    ###############################################################################
    # Helpers
    ###############################################################################
    def convert_to_signed(self, value):
         # Convert to signed 16-bit
        if value > 32767:
            value -= 65536 
        return value
###############################################################################
# Entry
###############################################################################
if __name__ == "__main__":

    SMBUS_ID = 1

    bus: SMBus = SMBus(SMBUS_ID)

    imu = BNO055(bus)
    
    imu.reset()
    
    #imu.start_self_test()

    sleep(1)
        
    # Set to CONFIG
    imu.set_mode(CONFIGMODE) 
    # Make changes to registers once in config mode 

    sleep(.05)
    
    # Set mode.
    imu.set_mode(NDOF)

    sleep(0.1)
    
    # Calibrate: requires rotation in all directions, angles, orientations, etc....
    '''while True:
        sys, gyro, accel, mag = imu.get_calibration_status()
        print(f"Calibration status - SYS:{sys} GYRO:{gyro} ACCEL:{accel} MAG:{mag}")
        if sys == 3 and gyro == 3 and accel == 3 and mag == 3:
            print("BNO055 is fully calibrated and ready.")
            break
        sleep(1)'''
    
    temperature = imu.get_temperature()
    print(f"Temperature: {temperature}C")
    print("")
    
    while True:
        accel = imu.get_acceleration()
        gyro = imu.get_gyroscope()
        mag = imu.get_magnetometer() 
        temp = imu.get_temperature()       
        print(f"Accel: {accel}, Gyro: {gyro}, Mag: {mag}, Temp: {temp}C")


        heading, roll, pitch = imu.get_euler_angles()
        print(f"heading: {heading}, roll: {roll}, pitch: {pitch}")
        sleep(1)
  
  
  