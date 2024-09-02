#!/usr/bin/python3

import os
import can
import sys

os.system('sudo ip link set can0 type can bitrate 1000000')
os.system('sudo ifconfig can0 up')

can0 = can.interface.Bus(channel = 'can0', bustype = 'socketcan')

#msg = can.Message(arbitration_id=0x123, data=[0, 1, 2, 3, 4, 5, 6, 7], extended_id=False)

print("can0 waiting for message....")

try:
    while True:
        msg = can0.recv(0.25)
        if msg: 
            print (msg)

except Exception as e:
        print(e)

except KeyboardInterrupt:
    print ('Keyboard interrupted, exiting')
    
finally:
    os.system('sudo ifconfig can0 down')              
    sys.exit(0)
