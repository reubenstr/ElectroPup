#!/usr/bin/env python3

import os
import sys
import tty
import termios
import threading
import time
import select
import queue
import traceback
from time import sleep
from collections import OrderedDict
import curses

# Local:
from motors.motors import Motors

motor_model = "MG4010E-i10v3"

motor_info = OrderedDict({       
    'FLA': {'description' : 'front left abduction'},
    'FLH': {'description' : 'front left hip'},
    'FLK': {'description' : 'front left knee'},
    'FRA': {'description' : 'front right abduction'},
    'FRH': {'description' : 'front right hip'},
    'FHK': {'description' : 'front right knee'},
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


def main(stdscr):        
    curses.cbreak()
    curses.curs_set(0)
    stdscr.nodelay(True) 
    stdscr.clear()
    
      
    if curses.has_colors():
        curses.start_color()     
        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)     
        curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLUE)  
        curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_RED) 
     
    row = 0

    motor_tags = ["FLA", "FLH", "FLK"]
    motors_front = Motors(can_bus_id="can0", motor_tags=motor_tags)    
    motors_front.motors_off()
    # TODO:   motors_front.shutdown()
    
    while True:
        try:            
            motors_front.op_fetch_all_motor_angles()
            motors = motors_front.get_motors()            
            
            char = stdscr.getch()  
            if char != -1:              
                #stdscr.refresh()  # Update the screen
                if char == curses.KEY_UP:
                    if row > 0:
                        row -= 1
                elif char == curses.KEY_DOWN:    
                    if row < len(motor_info) - 1:
                        row += 1
                elif chr(char) == 'q':  # Check for 'q' to exit
                    break
                elif chr(char) == '0': # Check for '0' to zero motor
                    motor_tag =  list(motor_info.keys())[row]  
                    success = motors_front.op_fetch_motor_angle(motor_tag=motor_tag)                     
                    if success:
                        offset = motors_front.get_motor_angle(motor_tag=motor_tag)
                        motor_info[motor_tag]['offset'] = offset
                        success = motors_front.motor_set_zero_to_current_position(motor_tag=motor_tag)
                        if success:                            
                            motor_info[motor_tag]['zeroed'] = True   
                        else:
                            motor_info[motor_tag]['error'] = True
                    else:
                        motor_info[motor_tag]['error'] = True
                                       

            stdscr.addstr(0, 0, " State |  Angle | Tag | Description\n")
            stdscr.addstr(1, 0, "—————————————————————————————————\n")          
            for index, key in enumerate(motor_info):                        
                if key in motors:
                    angle = motors[key].angle_degrees -  motor_info[key]['offset']
                    angle = f'{angle:>6.2f}'
                else:
                   angle = '  N/A '
                
                if motor_info[key]['error']:
                    state = 'ERROR'
                elif motor_info[key]['zeroed']:
                    state = 'ZEROED'
                else:
                    state = ' STBY '
                               
                description = motor_info[key]['description']
                text = f'{state} | {angle} | {key} | {description}'
                color_pair = 2 if index == row else 1
                stdscr.addstr(index + 2, 0, text, curses.color_pair(color_pair))
                
            warning = ""
            for key, info in motor_info.items():
                if info['zeroed']:
                    warning = "Power cycle required for zero to take effect!"
            
                
        
            
            stdscr.addstr(14, 0, "—————————————————————————————————")
            stdscr.addstr(15, 0, warning, curses.color_pair(3))
            stdscr.addstr(16, 0, "0 = zero, arrow = move row, q = quit")    
            
           
        
        except KeyboardInterrupt:
            break

###############################################################################
# Entry
###############################################################################
if __name__ == "__main__":

    # Redirect stdout to os.devnull
    original_stdout = sys.stdout 
    sys.stdout = open(os.devnull, 'w')

    try:
        curses.wrapper(main)
    finally:
        sys.stdout.close() 
        sys.stdout = original_stdout
    
  

    
    """  try:
        pass
             
    except KeyboardInterrupt:
        print ('Keyboard interrupt, exiting')
        
    except Exception as e:
        print(str(e))
        print(traceback.format_exc())
        
    finally:          
        motors_front.shutdown() """