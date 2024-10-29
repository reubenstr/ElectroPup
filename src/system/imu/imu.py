#!/usr/bin/env python3

import smbus
from time import sleep

# BNO005 I2C address
BNO055_ADDR = 0x28  # Change if your address is different

# Register addresses
SYS_TRIGGER = 0x3F
OPR_MODE = 0x3D
TEMPERATURE_REGISTER = 0x34
CALIB_STAT = 0x35
ST_RESULT = 0x36
ACCEL_DATA = 0x08
GYRO_DATA = 0x0C
MAG_DATA = 0x0E

class IMU:
    def __init__(self):  
        bus_number = 1 # Raspberry Pi default I2C bus
        self.bus = smbus.SMBus(bus_number)

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
        return self.read_register(CALIB_STAT)    
    
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
    imu = IMU()
    
    imu.reset()
    
    #imu.start_self_test()
        
    # Set to CONFIG
    CONFIGMODE = 0b00000000
    imu.set_mode(CONFIGMODE) 
    # Make changes to registers once in config mode 
    
    # Set mode.
    ACCONLY = 0b00000001
    NDOF = 0b00001100
    imu.set_mode(ACCONLY)
    
    while True:
        calibration_status = imu.get_calibration_status()
        print(f"Calibration status: {calibration_status}")
        if calibration_status > 0: 
            print("BNO055 is calibrated and ready.")
            break
        sleep(1)
    
    temperature = imu.get_temperature()
    print(f"Temperature: {temperature}C")
    print("")
    
    while True:
        accel = imu.get_acceleration()
        gyro = imu.get_gyroscope()
        mag = imu.get_magnetometer()        
        print(f"Acceleration: {accel}")
        print(f"Gyroscope:    {gyro}")
        print(f"Magnetometer: {mag}")
        sleep(1)
  
  
  