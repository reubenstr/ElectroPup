#!/usr/bin/env python3
import serial
import time
from time import sleep


class Aux():
    def __init__(self): 
        self.ser = serial.Serial(port='/dev/ttyS0', baudrate=115200, timeout=0.25)

    def send(self, data):  
        if self.ser.is_open:     
            
            crc = self.crc32(b'test')
            
            
            bytes_to_send = b'test' +  crc.to_bytes(4, byteorder='little')
            
            num_bytes = self.ser.write(bytes_to_send)
            
            decimal_values = [byte for byte in bytes_to_send]
            #print(num_bytes, hex(crc), decimal_values)
            
            bytes_to_send = [0, 0, 0, 0]
            byte_array = bytearray(bytes_to_send)
            crc = self.crc32(bytes_to_send)            
            decimal_values = [byte for byte in bytes_to_send]
            print(hex(crc), decimal_values)


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
        aux.send("test")
        sleep(1)
