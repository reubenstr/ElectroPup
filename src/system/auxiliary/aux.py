#!/usr/bin/env python3
import os
import serial
import struct
import time
from typing import List
from time import sleep
from enum import Enum

from .crc32 import crc32

"""
    Auxiliary Board (Raspberry Pi hat) interface.
    
    Sends status messages and commands over serial to the Auxiliary Board.
    Received commands over serial sent from the Auxiliary Board.
    
    The Auxiliary Board is optional and not required for the quadruped to operate.

    TODO: aux controller can be migrated to use threading to prevent main thread delays.
"""



# Must match auxiliary board firmware's MessageType struct.
class MessageType(Enum):
    STATUS = 0
    PLAY_SOUND = 1
    SHUTDOWN_RPI = 2

# Must match auxiliary board firmware's Sequence struct.
class Sequence(Enum):
    NONE = -1
    MCU_STARTUP = 0
    RPI_ON = 1
    RPI_OFF = 2
    MOTORS_ON = 3
    MOTORS_OFF = 4
    LOW_BATTERY = 5
    ERROR = 6
    SHUTDOWN = 7
    BTN_BEEP_SHORT = 8

class AuxMessage:
    def __init__(self):
        self.joystick_error : bool = False
        self.physical_limit_error : bool = False
        self.joint_angle_error : bool = False
        self.inverse_kinematics_error : bool = False        
        self.can_error : bool = False
        self.over_temperature_error : bool = False
        self.under_voltage_error : bool = False  
        self.motor_communication_error : bool = False 
        self.imu_error : bool = False     
        self.low_battery : bool = False     
        self.motor_ons : List[bool] = [False] * 12
        self.motor_errors : List[bool] = [False] * 12
        self.battery_voltage : float = 0.0
        self.gamepad_battery_percent : float = 0.0

    def pack(self):        
        bools = (
            self.joystick_error,
            self.physical_limit_error,
            self.joint_angle_error,
            self.inverse_kinematics_error,
            self.can_error,
            self.over_temperature_error,
            self.under_voltage_error,
            self.motor_communication_error,
            self.imu_error,
            self.low_battery) + tuple(self.motor_ons) + tuple(self.motor_errors)
    
        packed_message_id = bytes([MessageType.STATUS.value])
        packed_bools = bytearray(bool(b) for b in bools)   
        packed_voltage = struct.pack('f', self.battery_voltage)   
        packed_gamepad = struct.pack('f', self.gamepad_battery_percent)                       
        packed_message = packed_message_id + packed_bools + packed_voltage + packed_gamepad                                      
        packed_crc = crc32(packed_message).to_bytes(4, byteorder='little')
        return packed_message + packed_crc
   
   
class PlaySoundMessage:
    def __init__(self, sequence : int = -1):
        self.sound_id : int = sequence
        
    def pack(self): 
        packed_message_id = bytes([MessageType.PLAY_SOUND.value])
        packed_sequence_id = struct.pack('b', self.sound_id)
        
        packed_message = packed_message_id + packed_sequence_id                                     
        packed_crc = crc32(packed_message).to_bytes(4, byteorder='little')
        return packed_message + packed_crc
        
 
class Aux():
    def __init__(self):
        self.port = '/dev/serial0'
        self.baudrate = 115200
        self.timeout = 0.25
        self.start_time : float = time.time()
        self.send_message_rate_seconds: float = 0.1
        self.ser : serial.Serial = None
        self.available : bool = False
        self.init()

    def init(self):
        """Open the serial port. A missing or unopenable port is not an error, the
           Auxiliary Board is optional and absent when developing off target."""
        self.available = False

        if not os.path.exists(self.port):
            print(f"[Aux] serial port not found: {self.port}, Auxiliary Board disabled.")
            return

        try:
            self.ser = serial.Serial(port=self.port, baudrate=self.baudrate, timeout=self.timeout)
            self.available = True
            print(f"[Aux] serial port opened. Port: {self.port}, baud: {self.baudrate}, timeout: {self.timeout}")
        except Exception as e:
            print(f"[Aux] unable to open serial port: {self.port}, Auxiliary Board disabled, exception: {e}")

    def send_at_rate(self, data : bytes):
        """Sends data only when a specific amount of time has passed."""
        if (time.time() - self.start_time > self.send_message_rate_seconds):
            self.start_time = time.time()
            self.send(data)

    def send(self, data : bytes):
        """Send data to the Auxiliary Board"""
        if not self.available:
            return

        try:
            if self.ser.is_open:
                num_bytes_written = self.ser.write(data)

                # print([byte for byte in data])
                # print(f"[Aux] message sent, num bytes written: {num_bytes_written}")

        except Exception as e:
            print(f"[Aux] error, unable to send message on serial port: {self.port}, exception: {e}")


    def play_sound(self, sequence: Sequence):
        psm = PlaySoundMessage(sequence.value)
        self.send(psm.pack())


    def check_for_commands(self):
        """Check for commands from Auxilary Board"""

        if not self.available:
            return

        try:
            if self.ser.in_waiting == 0:
                return

            data = self.ser.read(self.ser.in_waiting)
        except Exception as e:
            print(f"[Aux] error, unable to read from serial port: {self.port}, exception: {e}")
            return

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
            message_data = AuxMessage()
            data = message_data.pack()        
            aux.send(data)
            sleep(1)
                
        elif test == 1:
            sequence_id = 2
            message = PlaySoundMessage(sequence_id)
            data = message.pack()
            aux.send(data)
            sleep(3)
            
        elif test == 2:
            aux.check_for_commands()
            sleep(0.010)
            
