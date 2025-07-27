#!/usr/bin/env python3

"""
    Gamepad Interface provides buttons and axis inputs from the gamepad driver as events.

    Original significantly modified from: https://github.com/piborg/Gamepad
    Key changes:
        Events only
        Non-blocking connections
        Auto reconnections
        Removes exceptions for status bool to check connection state
"""

import time
import struct
import threading
import subprocess

class GamepadInterface:
    EVENT_CODE_BUTTON = 0x01
    EVENT_CODE_AXIS = 0x02
    EVENT_CODE_INIT_BUTTON = 0x80 | EVENT_CODE_BUTTON
    EVENT_CODE_INIT_AXIS = 0x80 | EVENT_CODE_AXIS
    MIN_AXIS = -32767.0
    MAX_AXIS = +32767.0

    class UpdateThread(threading.Thread):
        """Thread used to continually run the updateState function on a Gamepad in the background"""
        def __init__(self, gamepad_interface):
            threading.Thread.__init__(self)
            if isinstance(gamepad_interface, GamepadInterface):
                self.gamepad_interface = gamepad_interface
            else:
                raise ValueError('Gamepad update thread was not created with a valid Gamepad object')
            self.running = True

        def run(self):
            try:
                while self.running:
                    self.gamepad_interface.updateState()
                self.gamepad_interface = None
            except:
                self.running = False
                self.gamepad_interface = None
                raise

    def __init__(self, joystickNumber, axisNames, buttonNames):
        self.joystickNumber = str(joystickNumber)
        self.axisNames = axisNames
        self.buttonNames = buttonNames

        self.eventSize = struct.calcsize('IhBB')
        self.pressedMap = {}
        self.wasPressedMap = {}
        self.wasReleasedMap = {}
        self.axisMap = {}
        self.axisIndex = {}
        self.buttonIndex = {}  
        self.lastTimestamp = 0
        self.updateThread = None        
        self.pressedEventMap = {}
        self.releasedEventMap = {}
        self.changedEventMap = {}
        self.movedEventMap = {}
        self.connected = False 

        for index in self.buttonNames:
            self.buttonIndex[self.buttonNames[index]] = index
        for index in self.axisNames:
            self.axisIndex[self.axisNames[index]] = index

        for index in range(len(self.axisNames)):
            self.axisMap[index] = 0
            self.movedEventMap[index] = []
        
        for index in range(len(self.buttonNames)):
            self.pressedMap[index] = False
            self.wasPressedMap[index] = False
            self.wasReleasedMap[index] = False
            self.pressedEventMap[index] = []
            self.releasedEventMap[index] = []
            self.changedEventMap[index] = []

        self.updateThread = GamepadInterface.UpdateThread(self)
        self.updateThread.start()        


    def _connect(self):
        self.joystickPath = '/dev/input/js' + self.joystickNumber       
        retryCount = 5  
        print(f"[Gamepad] attempting to connect to joystick at {self.joystickPath} ...")          
        while True:
            try:
                self.joystickFile = open(self.joystickPath, 'rb')
                self.connected = True
                print(f"[Gamepad] connected")   
                return
            except IOError as e:
                retryCount -= 1               
                if retryCount > 0:
                    time.sleep(0.5)
                else:
                    print(f"[Gamepad] error, unable to connect to joystick at {self.joystickPath}")  
                    self.connected = False
                    return                 
                  

    def __del__(self):
        try:
            self.joystickFile.close()
        except AttributeError:
            pass
       
    def _getNextEventRaw(self):
        """Returns the next raw event from the gamepad."""

        if self.connected == False:
            self._connect()
      
        if self.connected:
            try:
                rawEvent = self.joystickFile.read(self.eventSize)
                self.connected = True
                return struct.unpack('IhBB', rawEvent)                 
            except Exception as e:
                self.connected = False
                print(f"[Gamepad] error, joystick {self.joystickNumber} disconnected. Error: {str(e)}")
                self.connected = False

    def updateState(self):
        """Updates the internal button and axis states with the next pending event.

        This call waits for a new event if there are not any waiting to be processed."""

        try:
            self.lastTimestamp, value, eventType, index = self._getNextEventRaw()
        except:
            return
               
        if eventType == GamepadInterface.EVENT_CODE_BUTTON:  
            if value == 0:
                finalValue = False
                self.wasReleasedMap[index] = True
                for callback in self.releasedEventMap[index]:
                    callback()
            else:
                finalValue = True
                self.wasPressedMap[index] = True
                for callback in self.pressedEventMap[index]:
                    callback()
            self.pressedMap[index] = finalValue
            for callback in self.changedEventMap[index]:
                callback(finalValue)
        elif eventType == GamepadInterface.EVENT_CODE_AXIS:
            finalValue = value / GamepadInterface.MAX_AXIS
            self.axisMap[index] = finalValue
            for callback in self.movedEventMap[index]:
                callback(finalValue)
        elif eventType == GamepadInterface.EVENT_CODE_INIT_BUTTON:
            # This can be used to verify the buttons we expect match the actual gamepad.
            pass
        elif eventType == GamepadInterface.EVENT_CODE_INIT_AXIS:
            # This can be used to verify the axis we expect match the actual gamepad.
            pass
        else:
            print (f"[Gamepad] unprocessed even receive: {eventType}")
  

    def isPressed(self, buttonName):
        """Returns the last observed state of a gamepad button specified by name or index.
        True if pressed, False if not pressed.

        Status is updated by getNextEvent calls.

        Throws ValueError if the button name or index cannot be found."""
        try:
            if buttonName in self.buttonIndex:
                buttonIndex = self.buttonIndex[buttonName]
            else:
                buttonIndex = int(buttonName)
            return self.pressedMap[buttonIndex]
        except KeyError:
            raise ValueError('Button %i was not found' % buttonIndex)
        except ValueError:
            raise ValueError('Button name %s was not found' % buttonName)

    def beenPressed(self, buttonName):
        """Returns True if the button specified by name or index has been pressed since the last beenPressed call.
        Used in conjunction with updateState.

        Throws ValueError if the button name or index cannot be found."""
        try:
            if buttonName in self.buttonIndex:
                buttonIndex = self.buttonIndex[buttonName]
            else:
                buttonIndex = int(buttonName)
            if self.wasPressedMap[buttonIndex]:
                self.wasPressedMap[buttonIndex] = False
                return True
            else:
                return False
        except KeyError:
            raise ValueError('Button %i was not found' % buttonIndex)
        except ValueError:
            raise ValueError('Button name %s was not found' % buttonName)

    def beenReleased(self, buttonName):
        """Returns True if the button specified by name or index has been released since the last beenReleased call.
        Used in conjunction with updateState.

        Throws ValueError if the button name or index cannot be found."""
        try:
            if buttonName in self.buttonIndex:
                buttonIndex = self.buttonIndex[buttonName]
            else:
                buttonIndex = int(buttonName)
            if self.wasReleasedMap[buttonIndex]:
                self.wasReleasedMap[buttonIndex] = False
                return True
            else:
                return False
        except KeyError:
            raise ValueError('Button %i was not found' % buttonIndex)
        except ValueError:
            raise ValueError('Button name %s was not found' % buttonName)

    def axis(self, axisName):
        """Returns the last observed state of a gamepad axis specified by name or index.
        Throws a ValueError if the axis index is unavailable.

        Status is updated by getNextEvent calls.

        Throws ValueError if the button name or index cannot be found."""
        try:
            if axisName in self.axisIndex:
                axisIndex = self.axisIndex[axisName]
            else:
                axisIndex = int(axisName)
            return self.axisMap[axisIndex]
        except KeyError:
            raise ValueError('Axis %i was not found' % axisIndex)
        except ValueError:
            raise ValueError('Axis name %s was not found' % axisName)

    def availableButtonNames(self):
        """Returns a list of available button names for this gamepad.
        An empty list means that no button mapping has been provided."""
        return self.buttonIndex.keys()

    def availableAxisNames(self):
        """Returns a list of available axis names for this gamepad.
        An empty list means that no axis mapping has been provided."""
        return self.axisIndex.keys()

    def isConnected(self):
        """Returns True until reading from the device fails."""
        return self.connected

    def addButtonPressedHandler(self, buttonName, callback):
        """Adds a callback for when a specific button specified by name or index is pressed.
        This callback gets no parameters passed."""
        try:
            if buttonName in self.buttonIndex:
                buttonIndex = self.buttonIndex[buttonName]
            else:
                buttonIndex = int(buttonName)
            if callback not in self.pressedEventMap[buttonIndex]:
                self.pressedEventMap[buttonIndex].append(callback)
        except KeyError:
            raise ValueError('Button %i was not found' % buttonIndex)
        except ValueError:
            raise ValueError('Button name %s was not found' % buttonName)

    def removeButtonPressedHandler(self, buttonName, callback):
        """Removes a callback for when a specific button specified by name or index is pressed."""
        try:
            if buttonName in self.buttonIndex:
                buttonIndex = self.buttonIndex[buttonName]
            else:
                buttonIndex = int(buttonName)
            if callback in self.pressedEventMap[buttonIndex]:
                self.pressedEventMap[buttonIndex].remove(callback)
        except KeyError:
            raise ValueError('Button %i was not found' % buttonIndex)
        except ValueError:
            raise ValueError('Button name %s was not found' % buttonName)

    def addButtonReleasedHandler(self, buttonName, callback):
        """Adds a callback for when a specific button specified by name or index is released.
        This callback gets no parameters passed."""
        try:
            if buttonName in self.buttonIndex:
                buttonIndex = self.buttonIndex[buttonName]
            else:
                buttonIndex = int(buttonName)
            if callback not in self.releasedEventMap[buttonIndex]:
                self.releasedEventMap[buttonIndex].append(callback)
        except KeyError:
            raise ValueError('Button %i was not found' % buttonIndex)
        except ValueError:
            raise ValueError('Button name %s was not found' % buttonName)

    def removeButtonReleasedHandler(self, buttonName, callback):
        """Removes a callback for when a specific button specified by name or index is released."""
        try:
            if buttonName in self.buttonIndex:
                buttonIndex = self.buttonIndex[buttonName]
            else:
                buttonIndex = int(buttonName)
            if callback in self.releasedEventMap[buttonIndex]:
                self.releasedEventMap[buttonIndex].remove(callback)
        except KeyError:
            raise ValueError('Button %i was not found' % buttonIndex)
        except ValueError:
            raise ValueError('Button name %s was not found' % buttonName)

    def addButtonChangedHandler(self, buttonName, callback):
        """Adds a callback for when a specific button specified by name or index changes.
        This callback gets a boolean for the button pressed state."""
        try:
            if buttonName in self.buttonIndex:
                buttonIndex = self.buttonIndex[buttonName]
            else:
                buttonIndex = int(buttonName)
            if callback not in self.changedEventMap[buttonIndex]:
                self.changedEventMap[buttonIndex].append(callback)
        except KeyError:
            raise ValueError('Button %i was not found' % buttonIndex)
        except ValueError:
            raise ValueError('Button name %s was not found' % buttonName)

    def removeButtonChangedHandler(self, buttonName, callback):
        """Removes a callback for when a specific button specified by name or index changes."""
        try:
            if buttonName in self.buttonIndex:
                buttonIndex = self.buttonIndex[buttonName]
            else:
                buttonIndex = int(buttonName)
            if callback in self.changedEventMap[buttonIndex]:
                self.changedEventMap[buttonIndex].remove(callback)
        except KeyError:
            raise ValueError('Button %i was not found' % buttonIndex)
        except ValueError:
            raise ValueError('Button name %s was not found' % buttonName)

    def addAxisMovedHandler(self, axisName, callback):
        """Adds a callback for when a specific axis specified by name or index changes.
        This callback gets the updated position of the axis."""
        try:
            if axisName in self.axisIndex:
                axisIndex = self.axisIndex[axisName]
            else:
                axisIndex = int(axisName)
            if callback not in self.movedEventMap[axisIndex]:
                self.movedEventMap[axisIndex].append(callback)
        except KeyError:
            raise ValueError('Button %i was not found' % axisIndex)
        except ValueError:
            raise ValueError('Button name %s was not found' % axisName)

    def removeAxisMovedHandler(self, axisName, callback):
        """Removes a callback for when a specific axis specified by name or index changes."""
        try:
            if axisName in self.axisIndex:
                axisIndex = self.axisIndex[axisName]
            else:
                axisIndex = int(axisName)
            if callback in self.movedEventMap[axisIndex]:
                self.movedEventMap[axisIndex].remove(callback)
        except KeyError:
            raise ValueError('Button %i was not found' % axisIndex)
        except ValueError:
            raise ValueError('Button name %s was not found' % axisName)

    def removeAllEventHandlers(self):
        """Removes all event handlers from all axes and buttons."""
        for index in self.pressedEventMap.keys():
            self.pressedEventMap[index] = []
            self.releasedEventMap[index] = []
            self.changedEventMap[index] = []
            self.movedEventMap[index] = []

    def disconnect(self):
        """Cleanly disconnect and remove any threads and event handlers."""
        print(f"[Gamepad] disconnecting...")
        self.connected = False
        self.removeAllEventHandlers()
        self.updateThread.running = False
        self.updateThread.join()     
        print(f"[Gamepad] disconnected")  
            
    ###############################################################################
    # Battery 
    ###############################################################################        
    def get_battery_percent(self):
        try:
            output = subprocess.check_output("upower -i $(upower -e | grep battery)", shell=True, text=True)           
            for line in output.splitlines():
                if "percentage" in line:
                    percentage = line.split(":")[1].strip()
                    return int(float(percentage.rstrip('%')))                 
        except Exception as e:
            print(f"[Gamepad] error, unable to retrieve battery level from upower command: {e}")
        return None

###############################################################################
# Gamepad classes and mappings
###############################################################################

class PS3(GamepadInterface):
    fullName = 'PlayStation 3 controller'

    def __init__(self, joystickNumber = 0):
        GamepadInterface.__init__(self, joystickNumber)
        axisNames = {
            0: 'LEFT-X',
            1: 'LEFT-Y',
            2: 'L2',
            3: 'RIGHT-X',
            4: 'RIGHT-Y',
            5: 'R2'
        }
        buttonNames = {
            0:  'CROSS',
            1:  'CIRCLE',
            2:  'TRIANGLE',
            3:  'SQUARE',
            4:  'L1',
            5:  'R1',
            6:  'L2',
            7:  'R2',
            8:  'SELECT',
            9:  'START',
            10: 'PS',
            11: 'L3',
            12: 'R3',
            13: 'DPAD-UP',
            14: 'DPAD-DOWN',
            15: 'DPAD-LEFT',
            16: 'DPAD-RIGHT'
        }
        GamepadInterface.__init__(self, joystickNumber, axisNames, buttonNames)

class PS4(GamepadInterface):
    fullName = 'PlayStation 4 controller'

    def __init__(self, joystickNumber = 0):        
        axisNames = {
            0: 'LEFT-X',
            1: 'LEFT-Y',
            2: 'L2',
            3: 'RIGHT-X',
            4: 'RIGHT-Y',
            5: 'R2',
            6: 'DPAD-X',
            7: 'DPAD-Y'
        }
        buttonNames = {
            0:  'CROSS',
            1:  'CIRCLE',
            2:  'TRIANGLE',
            3:  'SQUARE',
            4:  'L1',
            5:  'R1',
            6:  'L2',
            7:  'R2',
            8:  'SHARE',
            9:  'OPTIONS',
            10: 'PS',
            11: 'L3',
            12: 'R3'
        }
        GamepadInterface.__init__(self, joystickNumber, axisNames, buttonNames)
      

class PS5(GamepadInterface):
    fullName = 'PlayStation 5 controller'

    def __init__(self, joystickNumber = 0):
        GamepadInterface.__init__(self, joystickNumber)
        axisNames = {
            0: 'LEFT-X',
            1: 'LEFT-Y',
            2: 'L2',
            3: 'RIGHT-X',
            4: 'RIGHT-Y',
            5: 'R2',
            6: 'DPAD-X',
            7: 'DPAD-Y'
        }
        buttonNames = {
            0:  'CROSS',
            1:  'CIRCLE',
            2:  'TRIANGLE',
            3:  'SQUARE',
            4:  'L1',
            5:  'R1',
            6:  'L2',
            7:  'R2',
            8:  'SHARE',
            9:  'OPTIONS',
            10: 'PS',
            11: 'L3',
            12: 'R3'
        }
        GamepadInterface.__init__(self, joystickNumber, axisNames, buttonNames)    

class Xbox360(GamepadInterface):
    fullName = 'Xbox 360 controller'

    def __init__(self, joystickNumber = 0):
        GamepadInterface.__init__(self, joystickNumber)
        axisNames = {
            0: 'LEFT-X',
            1: 'LEFT-Y',
            2: 'LT',
            3: 'RIGHT-X',
            4: 'RIGHT-Y',
            5: 'RT'
        }
        buttonNames = {
            0:  'A',
            1:  'B',
            2:  'X',
            3:  'Y',
            4:  'LB',
            5:  'RB',
            6:  'BACK',
            7:  'START',
            8:  'XBOX',
            9:  'LA',
            10: 'RA'
        }
        GamepadInterface.__init__(self, joystickNumber, axisNames, buttonNames)


class MMP1251(GamepadInterface):
    fullName = "ModMyPi Raspberry Pi Wireless USB Gamepad"

    def __init__(self, joystickNumber = 0):
        GamepadInterface.__init__(self, joystickNumber)
        axisNames = {
            0: 'LEFT-X',
            1: 'LEFT-Y',
            2: 'L2',
            3: 'RIGHT-X',
            4: 'RIGHT-Y',
            5: 'R2',
            6: 'DPAD-X',
            7: 'DPAD-Y'
        }
        buttonNames = {
            0:  'A',
            1:  'B',
            2:  'X',
            3:  'Y',
            4:  'L1',
            5:  'R1',
            6:  'SELECT',
            7:  'START',
            8:  'HOME',
            9:  'L3',
            10: 'R3'
        }
        GamepadInterface.__init__(self, joystickNumber, axisNames, buttonNames)