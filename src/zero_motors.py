#!/usr/bin/env python3

"""
    Utility to zero motors and verify motor layout.
    
    Not all motors are required to be attached.
    
    Motors require a power cycle for a new zero to take effect!
"""

import os
import sys
from time import sleep
from collections import OrderedDict
import curses

# Local:
from system.motors.motors import Motors

motor_model = "MG4010E-i10v3"

motor_info = OrderedDict({       
    'FLA': {'description' : 'front left abduction'},
    'FLH': {'description' : 'front left hip'},
    'FLK': {'description' : 'front left knee'},
    'FRA': {'description' : 'front right abduction'},
    'FRH': {'description' : 'front right hip'},
    'FRK': {'description' : 'front right knee'},
    'BLA': {'description' : 'back left abduction'},
    'BLH': {'description' : 'back left hip'},
    'BLK': {'description' : 'back left knee'},
    'BRA': {'description' : 'back right abduction'},
    'BRH': {'description' : 'back right hip'},
    'BRK': {'description' : 'back right knee'}})

for key in motor_info.keys():
    motor_info[key]['angle'] = 0
    motor_info[key]['offset'] = 0
    motor_info[key]['error'] = False
    motor_info[key]['zeroed'] = False

motor_tags_front = ["FLA", "FLH", "FLK", "FRA", "FRH", "FRK"]
motor_interface_front = Motors(can_bus_id="can0", motor_tags=motor_tags_front)    
motor_interface_front.cmd_all_motors_off()

motor_tags_back = ["BLA", "BLH", "BLK", "BRA", "BRH", "BRK"]
motor_interface_back = Motors(can_bus_id="can1", motor_tags=motor_tags_back)  
motor_interface_back.cmd_all_motors_off()

def get_motor_interface_from_tag(motor_tag : str):
    if motor_tag in motor_tags_front:
        return motor_interface_front
    elif motor_tag in motor_tags_back:
        return motor_interface_back
    
def get_motor_angle_from_tag(motor_tag : str):    
    motor_interface = get_motor_interface_from_tag(motor_tag=motor_tag)   
    success = motor_interface.op_fetch_motor_angle(motor_tag=motor_tag) 
    if success: 
        angle = motor_interface.get_motor_angle(motor_tag=motor_tag)
        return angle
            
def main(stdscr):  
    row = 0
          
    curses.cbreak()
    curses.curs_set(0)
    stdscr.nodelay(True) 
    stdscr.clear()
          
    if curses.has_colors():
        curses.start_color()     
        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)     
        curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLUE)  
        curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_RED) 
          
    # Upon startup the motor driver reports angles 0 to 360
    # To prevent issues of wrong initial directions, this library
    # uses -180 to 180 conventions. Flag start up angles > 180 requiring
    # an offset to match the desired convention.
    for motor_tag in motor_tags_front:
        angle = get_motor_angle_from_tag(motor_tag=motor_tag)
        if angle and angle > 180:          
            motor_interface_front.set_apply_negative_offset_angle_flag(motor_tag=motor_tag, value=True)
    for motor_tag in motor_tags_back:
        angle = get_motor_angle_from_tag(motor_tag=motor_tag)
        if angle and angle > 180:
            motor_interface_back.set_apply_negative_offset_angle_flag(motor_tag=motor_tag, value=True)
    
    while True:
        try: 
            char = stdscr.getch()  
            if char != -1:    
                if char == curses.KEY_UP:
                    if row > 0:
                        row -= 1
                elif char == curses.KEY_DOWN:    
                    if row < len(motor_info) - 1:
                        row += 1
                elif chr(char).lower() == 'q':  # Check for 'q' to exit
                    break
                elif chr(char) == '0': # Check for '0' to zero motor
                    motor_tag =  list(motor_info.keys())[row] 
                    offset  = get_motor_angle_from_tag(motor_tag)
                    if offset:
                        motor_info[motor_tag]['offset'] = offset
                        motor_interface = get_motor_interface_from_tag(motor_tag)
                        success = motor_interface.cmd_motor_set_zero_to_current_position(motor_tag=motor_tag)
                        if success:                            
                            motor_info[motor_tag]['zeroed'] = True   
                        else:
                            motor_info[motor_tag]['error'] = True
                              
            stdscr.addstr(0, 0, " State |  Angle | Tag | Description\n")
            stdscr.addstr(1, 0, "—————————————————————————————————\n")          
            for index, motor_tag in enumerate(motor_info): 
                angle = get_motor_angle_from_tag(motor_tag)
                if angle:
                    angle -= motor_info[motor_tag]['offset']                   
                    angle = f'{angle:>6.2f}'
                else:
                    angle = '  N/A '
                
                if motor_info[motor_tag]['error']:
                    state = ' ERROR'
                elif motor_info[motor_tag]['zeroed']:
                    state = 'ZEROED'
                else:
                    state = ' STBY '
                    
                motor_interface = get_motor_interface_from_tag(motor_tag)
                if motor_interface.get_motor(motor_tag).reply_timeout_count > 0:
                    state = ' ERROR'                    
                               
                description = motor_info[motor_tag]['description']
                text = f'{state} | {angle} | {motor_tag} | {description}'
                color_pair = 2 if index == row else 1
                stdscr.addstr(index + 2, 0, text, curses.color_pair(color_pair))
                
            warning = ""
            for motor_tag, info in motor_info.items():
                if info['zeroed']:
                    warning = "Power cycle required for zero to take effect!"
                        
            stdscr.addstr(14, 0, "—————————————————————————————————")
            stdscr.addstr(15, 0, warning, curses.color_pair(3))
            stdscr.addstr(16, 0, "0 = zero, arrows = move row, q = quit")    
               
        except KeyboardInterrupt:
            break        
        
    motor_interface_front.shutdown()
    motor_interface_back.shutdown()

###############################################################################
# Entry
###############################################################################
if __name__ == "__main__":
    
    # Redirect stdout to os.devnull
    original_stdout = sys.stdout 
    sys.stdout = open(os.devnull, 'w')

    try:
        curses.wrapper(main)
    except curses.error as e: 
        sys.stdout.close() 
        sys.stdout = original_stdout              
        print(f'Error: {__file__} requires more rows in the terminal to display properly!')  
        exit()              
    finally:
        sys.stdout.close() 
        sys.stdout = original_stdout 