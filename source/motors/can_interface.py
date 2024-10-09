"""
    Interfaces with MG4010E-i10v3 actuators over CAN bus.

    Not all possible commands and requests are implemeted.
"""

import os
import sys 
import can
from rich import print

class CanInterface():
    
    ###############################################################################
    # Class Initialization
    ###############################################################################
    
    def __init__(self, can_bus_id : str):
        self.can_bus_id = can_bus_id   
        self.tag = self.can_bus_id.upper() 
        
        # How long the interface waits for a reply from a motor.
        self.timeout_ms = 30.0  
        
        self.prints_enabled = False

    ###############################################################################
    # CAN Methods
    ###############################################################################

    def can_init(self):
        if self.prints_enabled:
            print(f"[{self.tag}] initializing")
        os.system(f'sudo ip link set {self.can_bus_id} type can bitrate 1000000') 
        os.system(f'sudo ifconfig {self.can_bus_id} up')
        self.canbus = can.interface.Bus(channel = self.can_bus_id, bustype = 'socketcan')

    def can_deinit(self):     
        if self.prints_enabled:  
         print(f"[{self.tag}] deinitializing")
        os.system(f'sudo ifconfig {self.can_bus_id} down')

    def can_send_message(self, motor_id : int, data : list):       
        identifier = 0x140 + motor_id
        #if self.prints_enabled:
        #print(f"[{self.tag}] sending message, bus={can_bus_id}, motor_id={motor_id}, arbitration_id={identifier}, data={data}")
        msg = can.Message(is_extended_id=False, arbitration_id=identifier, data=data)
        self.canbus.send(msg)
    
    def wait_for_reply(self):  
        return self.canbus.recv(self.timeout_ms / 1000.0)
   
    ###############################################################################
    # Motor Commands
    ###############################################################################

    def cmd_motor_off(self, motor_id: int):      
        self.can_send_message(motor_id, [0x80, 0, 0, 0, 0, 0, 0, 0])
        message = self.wait_for_reply()
        return message and motor_id == message.arbitration_id - 0x140            

    def cmd_motor_on(self, motor_id : int):  
        self.can_send_message(motor_id, [0x88, 0, 0, 0, 0, 0, 0, 0])
        message = self.wait_for_reply()
        return message and motor_id == message.arbitration_id - 0x140
               
    def cmd_clear_motor_errors(self, motor_id : int):        
        self.can_send_message(motor_id, [0x9B, 0, 0, 0, 0, 0, 0, 0])
        message = self.wait_for_reply()
        return message and motor_id == message.arbitration_id - 0x140    
        
    def cmd_set_zero_to_current_pos(self, motor_id : int):      
        self.can_send_message(motor_id, [0x19, 0, 0, 0, 0, 0, 0, 0])
        message = self.wait_for_reply()
        return message and motor_id == message.arbitration_id - 0x140    
                              
    def cmd_motor_multi_angle_2(self, motor_id : int, direction : bool, speed : int, angle : float):    
        '''        
            Sets speed and angle of the motor.
        '''       
        
        # temp:
        if motor_id == 3:
            print(angle)
        
        
        speed_low_byte = speed & 0x00FF
        speed_high_byte = speed >> 8 & 0x00FF 
        angle_byte_0 = int(angle * 1000.0) >> 0 & 0x000000FF
        angle_byte_1 = int(angle * 1000.0) >> 8 & 0x000000FF
        angle_byte_2 = int(angle * 1000.0) >> 16 & 0x000000FF
        angle_byte_3 = int(angle * 1000.0) >> 24 & 0x000000FF
        self.can_send_message(motor_id, [0xA4, direction, speed_low_byte, speed_high_byte, angle_byte_0, angle_byte_1, angle_byte_2, angle_byte_3])
        message = self.wait_for_reply()        
        return message and motor_id == message.arbitration_id - 0x140      
      
    def cmd_motor_increment_angle(self, motor_id : int, speed : int, angle : float):    
        '''        
            Sets speed and angle of the motor.
        '''       
        speed_low_byte = speed & 0x00FF
        speed_high_byte = speed >> 8 & 0x00FF 
        angle_byte_0 = int(angle * 1000.0) >> 0 & 0x000000FF
        angle_byte_1 = int(angle * 1000.0) >> 8 & 0x000000FF
        angle_byte_2 = int(angle * 1000.0) >> 16 & 0x000000FF
        angle_byte_3 = int(angle * 1000.0) >> 24 & 0x000000FF
        self.can_send_message(motor_id, [0xA8, 0, speed_low_byte, speed_high_byte, angle_byte_0, angle_byte_1, angle_byte_2, angle_byte_3])
        message = self.wait_for_reply()
        return message and motor_id == message.arbitration_id - 0x140      

    ###############################################################################
    # Motor Requests
    ###############################################################################

    def req_state_1(self, motor_id: int):          
        self.can_send_message(motor_id, [0x9A, 0, 0, 0, 0, 0, 0, 0])   
        message = self.wait_for_reply()
        if message:
             reply_motor_id = message.arbitration_id - 0x140
             if motor_id == reply_motor_id:                     
                reply_data = message.data        
                temperature = reply_data[1]
                voltage = (reply_data[2] | reply_data[3] << 8) / 100.0 # Datasheet is wrong, not DATA[3] and DATA[4].  
                under_voltage_protection = bool(reply_data[7] & 0b00000001)
                over_voltage_protection = bool(reply_data[7] & 0b00000010)
                over_temperature_protection = bool(reply_data[7] & 0b00001000)
                lost_input_protection = bool(reply_data[7] & 0b10000000)
                if self.prints_enabled:
                    print(f"[{self.tag }][M{reply_motor_id}] req_state_1 reply, temp.: {temperature}C, voltage: {voltage}V, UVP: {under_voltage_protection}, OVP: {over_voltage_protection}, OTP: {over_temperature_protection}, LIP:{lost_input_protection}")
                return {'temperature' : temperature, 
                        'voltage' : voltage,
                        'under_voltage_protection' : under_voltage_protection,
                        'over_voltage_protection' : over_voltage_protection,
                        'over_temperature_protection' : over_temperature_protection,
                        'lost_input_protection' : lost_input_protection}
                 
    def req_state_2(self, motor_id: int):           
        self.can_send_message(motor_id, [0x9C, 0, 0, 0, 0, 0, 0, 0])   
        message = self.wait_for_reply()
        if message:
            reply_motor_id = message.arbitration_id - 0x140
            if motor_id == reply_motor_id:         
                reply_data = message.data        
                temperature = reply_data[1]
                watts_raw = self.convert_twos_compliment(reply_data[2] | reply_data[3] << 8)       
                watts = self.map_range(float(watts_raw), -2048.0, 2048.0, -33.0, 33.0)
                motor_speed = self.convert_twos_compliment(reply_data[4] | reply_data[5] << 8)
                encoder_position = reply_data[6] | reply_data[7] << 8         
                if self.prints_enabled:
                    print(f"[{self.tag }][M{reply_motor_id}] req_state_2 reply, temp.: {temperature}C, watts: {watts}, motor speed: {motor_speed}, encoder position: {encoder_position}")
                return {'temperature' : temperature, 
                        'watts' : watts,
                        'motor_speed' : motor_speed,
                        'encoder_position' : encoder_position}
            
            
    def req_motor_single_angle(self, motor_id: int):   
        self.can_send_message(motor_id, [0x94, 0, 0, 0, 0, 0, 0, 0])
        message =self. wait_for_reply()
        if message:
            reply_motor_id = message.arbitration_id - 0x140
            if motor_id == reply_motor_id:                      
                reply_data = message.data
                angle_degrees = ((reply_data[7] << 24) | (reply_data[6] << 16) | (reply_data[5] << 8) | reply_data[4] << 0) / 1000                
                if self.prints_enabled:
                    print(f"[{self.tag }][M{reply_motor_id}] req_motor_single_angle reply, angle: {angle_degrees} degrees")
                return angle_degrees
    
    ###############################################################################
    # Helpers
    ###############################################################################
    @staticmethod
    def convert_twos_compliment(value):
        if value >= 0x8000:  # 0x8000 is 32768 in decimal, the value of the MSB for 16-bit
                # Convert to negative value
                return value - 0x10000  # 0x10000 is 65536, the range of 16-bit unsigned integer
        else:
            # Positive value or zero
            return value
    
    @staticmethod
    def map_range(x, in_min, in_max, out_min, out_max):
        return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min
    

    def enable_prints(self, flag : bool):
        self.prints_enabled = flag