#!/usr/bin/env python3
"""
    Auxiliary Board (Raspberry Pi hat) interface.
    
    Sends status messages and commands over serial to the Auxiliary Board.
    Received commands over serial sent from the Auxiliary Board.
    
    The Auxiliary Board is optional and not required for the quadruped to operate.
"""

import os
import serial
import struct
import time
from typing import List
from time import sleep
from enum import Enum
from crc32 import crc32


# Must match auxiliary board firmware's MessageType struct.
class MessageType(Enum):
    STATUS = 0
    PLAY_SOUND = 1
    SHUTDOWN_RPI = 2


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
    def __init__(self, sequence_id : int = -1):
        self.sound_id : int = sequence_id
        
    def pack(self): 
        packed_message_id = bytes([MessageType.PLAY_SOUND.value])
        packed_sequence_id = struct.pack('b', self.sound_id)
        
        packed_message = packed_message_id + packed_sequence_id                                     
        packed_crc = crc32(packed_message).to_bytes(4, byteorder='little')
        return packed_message + packed_crc
        
 
class Aux():
    def __init__(self):         
        self.port = '/dev/ttyS0'
        self.baudrate = 115200
        self.timeout = 0.25        
        self.start_time : float = time.time()
        
        self._open()
        
    def _open(self): 
        try:
            self.ser = serial.Serial(port=self.port, baudrate=self.baudrate, timeout=self.timeout)
        except Exception as e:
            print(f"[AUX] error, unable open serial port: {self.port}, exception: {e}")            
                                        
    def send_at_rate(self, data : bytes, rate : float):
        """Sends data only when a specific amount of time has passed."""
        if (time.time() - self.start_time > rate):
            self.start_time = time.time()
            self.send(data)
           
    def send(self, data : bytes):     
        try:      
            if not self.ser.is_open: 
                self._open()
                         
            if self.ser.is_open:                                  
                num_bytes_written = self.ser.write(data)
                    
                # Print data:                       
                # print(hex(crc), [byte for byte in data])                
                print(f"[AUX] message sent, num bytes written: {num_bytes_written}")
            
        except Exception as e:
            print(f"[AUX] error, unable to send message on serial port: {self.port}, exception: {e}")            
      
      
    def tick(self):
        
        # Check for commands from Auxilary Board
        if self.ser.in_waiting > 0: 
            data = self.ser.read(self.ser.in_waiting) 
                
            try:
                message_type = MessageType(data[0])
                print(f"[Aux] message received, type: {message_type.name}")
            except ValueError:
                print(f"[Aux] error, invalid message type received, type: {data[0]}")
                return
                            
            if message_type == MessageType.SHUTDOWN_RPI:
                print(f"[Aux] Shutdown Raspberry Pi command received, shutting down...")
                sleep(1)
                os.system("sudo shutdown now") 
            
            
###############################################################################
# Entry
###############################################################################
if __name__ == "__main__":
    aux = Aux()
    
    test = 3
    print(f"[Aux] running test: {test}")
    
    # Run various tests / demos.
    while(True): 
                
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
            sequence_id = 2
            message = PlaySoundMessage(sequence_id)
            data = message.pack()
            aux.send(data)
            sleep(3)
            
        elif test == 3:
            aux.tick()
            sleep(0.010)
            
