#!/usr/bin/env python3
import serial
import struct
import time
from typing import List
from time import sleep


class MessageData:
    def __init__(self):
        self.jointAngleError : bool = False
        self.inverseKinematicsError : bool = False
        self.joystickError : bool = False
        self.overCurrentError : bool = False
        self.underVoltageError : bool = False
        self.canError : bool = False
        self.motorOns : List[bool] = [False] * 12
        self.motorErrors : List[bool] = [False] * 12
        self.batteryVoltage : bool = 0.0

    def pack(self):        
        bools = (self.jointAngleError,
                self.inverseKinematicsError,
                self.joystickError,
                self.overCurrentError,
                self.underVoltageError,
                self.canError) + tuple(self.motorOns) + tuple(self.motorErrors)
    
        packed_bools = bytearray(int(b) for b in bools)   
        packed_voltage = struct.pack('f', self.batteryVoltage)

        return packed_bools + packed_voltage


class Aux():
    def __init__(self):         
        self.port = '/dev/ttyS0'
        self.baudrate = 115200
        self.timeout = 0.25        
        self.start_time : float = time.time()
           
           
    def send_at_rate(self, data : bytes, rate : float):
        """Sends data only when a specific amount of time has passed."""
        if (time.time() - self.start_time > rate):
            self.start_time = time.time()
            self.send(data)

           
    def send(self, data : bytes):
        start = time.time()
        try:            
            with serial.Serial(port=self.port, baudrate=self.baudrate, timeout=self.timeout) as ser:                
                if ser.is_open:               
                                
                    crc = self.crc32(data)                                        
                    bytes_to_send = data +  crc.to_bytes(4, byteorder='little')                    
                    num_bytes_written = ser.write(bytes_to_send)
                     
                    # Print data:                   
                    # decimal_values = [byte for byte in bytes_to_send]
                    # print(hex(crc), decimal_values)
                    
                    print(f"[AUX] message sent, num bytes written: {num_bytes_written}, time to send: {time.time() - start}")
             
        except Exception as e:
            print(f"[AUX] error, unable to send message on serial port: {self.port}, exception: {e}")            
      

    ###############################################################################
    # CRC
    ###############################################################################

    def crc32(self, data: bytes) -> int:     
        POLYNOMIAL = 0x04C11DB7      
        crc = 0xFFFFFFFF

        for byte in data:
            crc ^= byte << 24
            for _ in range(8):
                if crc & 0x80000000:
                    crc = (crc << 1) ^ POLYNOMIAL
                else:
                    crc <<= 1
                crc &= 0xFFFFFFFF 
     
        return crc ^ 0xFFFFFFFF


###############################################################################
# Entry
###############################################################################
if __name__ == "__main__":
    aux = Aux()
    
    while(True):
        
        message_data = MessageData()
        data = message_data.pack()
        
        test = 1
        if test == 0:            
            aux.send(data)
            sleep(1)
        elif test == 1:
            rate = 0.5
            aux.send_at_rate(data, rate) 
            sleep(0.010)
