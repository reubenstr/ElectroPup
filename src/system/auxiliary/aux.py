#!/usr/bin/env python3
import serial
import struct
import time
from typing import List
from time import sleep
from enum import Enum
from crc32 import crc32

class MessageType(Enum):
    STATUS = 0
    PLAY_SOUND = 1

class StatusMessage:
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
    
        packed_message_id = bytes([MessageType.STATUS.value])
        packed_bools = bytearray(int(b) for b in bools)   
        packed_voltage = struct.pack('f', self.batteryVoltage)
       
        packed_message = packed_message_id + packed_bools + packed_voltage                                      
        packed_crc = crc32(packed_message).to_bytes(4, byteorder='little')
        return packed_message + packed_crc
   
class PlaySoundMessage:
    def __init__(self, sound_id : int = -1):
        self.sound_id : int = sound_id
        
    def pack(self): 
        packed_message_id = bytes([MessageType.PLAY_SOUND.value])
        packed_sound_id = struct.pack('b', self.sound_id)
        
        packed_message = packed_message_id + packed_sound_id                                     
        packed_crc = crc32(packed_message).to_bytes(4, byteorder='little')
        return packed_message + packed_crc
        
        
 
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
                    num_bytes_written = ser.write(data)
                     
                    # Print data:                   
                    # decimal_values = [byte for byte in data]
                    # print(hex(crc), decimal_values)
                    
                    print(f"[AUX] message sent, num bytes written: {num_bytes_written}, time to send: {time.time() - start}")
             
        except Exception as e:
            print(f"[AUX] error, unable to send message on serial port: {self.port}, exception: {e}")            
      


###############################################################################
# Entry
###############################################################################
if __name__ == "__main__":
    aux = Aux()
    
    # Run various tests / demos.
    while(True):        
                
        test = 2
        if test == 0:    
            message_data = StatusMessage()
            data = message_data.pack()        
            aux.send(data)
            sleep(1)
            
        elif test == 1:
            message_data = StatusMessage()
            data = message_data.pack()
            rate = 0.5
            aux.send_at_rate(data, rate) 
            sleep(0.010)
            
        elif test == 2:
            message = PlaySoundMessage(1)
            data = message.pack()
            aux.send(data)
            sleep(1)
