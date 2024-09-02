#!/usr/bin/python3


import os
import can
import sys
import time
import traceback
from time import sleep
import numpy as np
import random
from rich import print

can_bus_id = 'can1'
canbus = None

###############################################################################
# Methods
###############################################################################

def can_init():
    global canbus
    print(f"[{can_bus_id.upper()}] initializing")
    os.system(f'sudo ip link set {can_bus_id} type can bitrate 1000000') 
    os.system(f'sudo ifconfig {can_bus_id} up')
    canbus = can.interface.Bus(channel = can_bus_id, bustype = 'socketcan')

def can_deinit(): 
    print(f"[{can_bus_id.upper()}] deinitializing")
    #os.system('sudo ifconfig can1 down')

def can_send_message(motor_id : int, data : list):
    global canbus
    identifier = 0x140 + motor_id
    #print(f"[{can_bus_id.upper()}] sending message, bus={can_bus_id}, motor_id={motor_id}, arbitration_id={identifier}, data={data}")
    msg = can.Message(is_extended_id=False, arbitration_id=identifier, data=data)
    canbus.send(msg)
  
def wait_for_reply():
    timeout_ms = 0.5
    # Wait required to allow sending message to complete.
    #sleep(.0005)
    
    return canbus.recv(timeout_ms / 1000.0)
    
    message = canbus.recv(timeout_ms / 1000.0)
    if message: 
        print(f"[{can_bus_id.upper()}] {message}")
    else:
        print(f"[{can_bus_id.upper()}] no reply received! timeout: {timeout_ms}ms")

    return message    

def cmd_motor_off(motor_id : int):
    can_send_message(motor_id, [0x80, 0, 0, 0, 0, 0, 0, 0])

def cmd_motor_on(motor_id : int):
    can_send_message(motor_id, [0x88, 0, 0, 0, 0, 0, 0, 0])

def cmd_motor_set_angle(motor_id: int, angle):
    can_send_message(motor_id, [0x94, 0, 0, 0, 0, 0, 0, 0])

def cmd_clear_motor_errors(motor_id: int):
    can_send_message(motor_id, [0x9B, 0, 0, 0, 0, 0, 0, 0])

def cmd_set_zero_to_current_pos(motod_id: int):
    can_send_message(motor_id, [0x91, 0, 0, 0, 0, 0, 0, 0])

def cmd_set_zero_to_value(motod_id: int, angle : float):
    # Convert angle degrees to 0-16383
    angle = int((16383.0 / 360.0) * angle)
    angle_low_byte = angle & 0x00FF
    angle_high_byte = angle >> 8 & 0x00FF
    can_send_message(motor_id, [0x91, 0, 0, 0, 0, 0, angle_low_byte, angle_high_byte])
    
def cmd_motor_single_angle(motor_id : int, spin_dir : bool, speed : int, angle : float):    
    speed_low_byte = speed & 0x00FF
    speed_high_byte = speed >> 8 & 0x00FF 
    angle_byte_0 = int(angle * 1000.0) >> 0 & 0x000000FF
    angle_byte_1 = int(angle * 1000.0) >> 8 & 0x000000FF
    angle_byte_2 = int(angle * 1000.0) >> 16 & 0x000000FF
    angle_byte_3 = int(angle * 1000.0) >> 24 & 0x000000FF
    can_send_message(motor_id, [0xA6, spin_dir, speed_low_byte, speed_high_byte, angle_byte_0, angle_byte_1, angle_byte_2, angle_byte_3])
    message = wait_for_reply()
    if message:
        reply_motor_id = message.arbitration_id - 0x140
        reply_data = message.data
        #print(f"[{can_bus_id.upper()}] cmd_motor_single_angle reply, {message}") 

def req_state_1(motor_id: int):
    can_send_message(motor_id, [0x9A, 0, 0, 0, 0, 0, 0, 0])   
    message = wait_for_reply()
    if message:
        reply_motor_id = message.arbitration_id - 0x140
        reply_data = message.data        
        temperature = reply_data[1]
        voltage = (reply_data[2] | reply_data[3] << 8) / 100.0 # Datasheet is wrong, not DATA[3] and DATA[4].  
        under_voltage_protection = bool(reply_data[7] & 0b00000001)
        over_voltage_protection = bool(reply_data[7] & 0b00000010)
        over_temperature_protection = bool(reply_data[7] & 0b00001000)
        lost_input_protection = bool(reply_data[7] & 0b10000000)
        #print(f"[{can_bus_id.upper()}][MOTOR{reply_motor_id}] req_state_1 reply, temp.: {temperature}C, voltage: {voltage}V, UVP: {under_voltage_protection}, OVP: {over_voltage_protection}, OTP: {over_temperature_protection}, LIP:{lost_input_protection}")
   
def req_state_2(motor_id: int):
    can_send_message(motor_id, [0x9C, 0, 0, 0, 0, 0, 0, 0])   
    message = wait_for_reply()
    if message:
        reply_motor_id = message.arbitration_id - 0x140
        reply_data = message.data        
        temperature = reply_data[1]
        watts = convert_twos_compliment(reply_data[2] | reply_data[3] << 8)       
        watts = map_range(float(watts), -2048.0, 2048.0, -33.0, 33.0)
        motor_speed = convert_twos_compliment(reply_data[4] | reply_data[5] << 8)
        encoder_position = reply_data[6] | reply_data[7] << 8         
        #print(f"[{can_bus_id.upper()}][MOTOR{reply_motor_id}] req_state_2 reply, temp.: {temperature}C, watts: {watts}, motor speed: {motor_speed}, encoder position: {encoder_position}")

def req_motor_single_angle(motor_id : int):
    angle_degrees = None
    can_send_message(motor_id, [0x94, 0, 0, 0, 0, 0, 0, 0])
    message = wait_for_reply()
    if message:
        reply_motor_id = message.arbitration_id - 0x140
        reply_data = message.data
        angle_degrees = ((reply_data[7] << 24) | (reply_data[6] << 16) | (reply_data[5] << 8) | reply_data[4] << 0) / 1000
        print(f"[{can_bus_id.upper()}][MOTOR{reply_motor_id}] req_motor_single_angle reply, angle: {angle_degrees} degrees")
    return angle_degrees           

###############################################################################
# Helpers
###############################################################################
def convert_twos_compliment(value):
    if value >= 0x8000:  # 0x8000 is 32768 in decimal, the value of the MSB for 16-bit
            # Convert to negative value
            return value - 0x10000  # 0x10000 is 65536, the range of 16-bit unsigned integer
    else:
        # Positive value or zero
        return value

def map_range(x, in_min, in_max, out_min, out_max):
  return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

###############################################################################
# 
###############################################################################

def loop(motor_id : int):

    #req_state_2(motor_id)
    #exit(0)
    
    startM = time.time()

    angles = np.arange(0, 90, 5) 
    while True:
        for angle in angles:
            spin_dir = 0
            speed = 5000  
          
            start = time.time()
            flag = time.time() - startM > 0.05
            flag = True
           
                  
            for i in range(6): 
                cmd_motor_single_angle(i + 1, spin_dir, speed, angle)
                if flag:           
                    req_state_2(1)
            
            if flag:
                startM = time.time() 
                
            print(f"[bold green]{int ((time.time() - start) * 1000)}ms[/bold green]")    
                       
            
            #sleep(0.02)
        for angle in angles[::-1]:
            spin_dir = 1
            speed = 5000    
            start = time.time()       
            for i in range(6): 
                cmd_motor_single_angle(i + 1, spin_dir, speed, angle)
            print(f"[bold green]{int ((time.time() - start) * 1000)}ms[/bold green]")
            #sleep(0.02)
        #exit(0)   
   
   
    while True:
        start = time.time()
        req_motor_single_angle(motor_id)

        spin_dir = 0
        speed = 5000
        angle = 0
        cmd_motor_single_angle(motor_id, spin_dir, speed, angle)
        print(time.time() - start)
        sleep(1)


###############################################################################
# Main / Entry
###############################################################################
if __name__ == "__main__":

    try:   
        can_init()

        motor_id = 1

        loop(motor_id)

        #cmd_motor_on(motor_id)
        #cmd_motor_set_angle(motor_id, 0)
        #sleep(2)
        #cmd_motor_off(motor_id)
   
    except Exception as e:
        print(e)
        print(traceback.format_exc())
    
    except KeyboardInterrupt:
        print ('Keyboard interrupted, exiting')
        
    finally:
        can_deinit()            
        sys.exit(0)
   