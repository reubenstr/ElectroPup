#!/usr/bin/env python3
# coding: utf-8

"""
    Gamepad provides buttons and axis inputs from a gamepad.

    Original source and documentation: https://github.com/piborg/Gamepad
"""

import os
import time
import struct
import threading


def available(joystickNumber):
    """
        Check if a joystick is connected and ready to use givin the provided ID.
    """
    joystickPath = '/dev/input/js' + str(joystickNumber)
    return os.path.exists(joystickPath)

class Gamepad:
    EVENT_CODE_BUTTON = 0x01
    EVENT_CODE_AXIS = 0x02
    EVENT_CODE_INIT_BUTTON = 0x80 | EVENT_CODE_BUTTON
    EVENT_CODE_INIT_AXIS = 0x80 | EVENT_CODE_AXIS
    MIN_AXIS = -32767.0
    MAX_AXIS = +32767.0
    EVENT_BUTTON = 'BUTTON'
    EVENT_AXIS = 'AXIS'
    fullName = 'Generic (numbers only)'

    class UpdateThread(threading.Thread):
        """Thread used to continually run the updateState function on a Gamepad in the background

        One of these is created by the Gamepad startBackgroundUpdates function and closed by stopBackgroundUpdates"""
        def __init__(self, gamepad):
            threading.Thread.__init__(self)
            if isinstance(gamepad, Gamepad):
                self.gamepad = gamepad
            else:
                raise ValueError('Gamepad update thread was not created with a valid Gamepad object')
            self.running = True

        def run(self):
            try:
                while self.running:
                    self.gamepad.updateState()
                self.gamepad = None
            except:
                self.running = False
                self.gamepad = None
                raise

    def __init__(self, joystickNumber = 0):
        self.joystickNumber = str(joystickNumber)
        self.joystickPath = '/dev/input/js' + self.joystickNumber
        retryCount = 5
        while True:
            try:
                self.joystickFile = open(self.joystickPath, 'rb')
                break
            except IOError as e:
                retryCount -= 1
                if retryCount > 0:
                    time.sleep(0.5)
                else:
                    raise IOError('Could not open gamepad %s: %s' % (self.joystickNumber, str(e)))
        self.eventSize = struct.calcsize('IhBB')
        self.pressedMap = {}
        self.wasPressedMap = {}
        self.wasReleasedMap = {}
        self.axisMap = {}
        self.buttonNames = {}
        self.buttonIndex = {}
        self.axisNames = {}
        self.axisIndex = {}
        self.lastTimestamp = 0
        self.updateThread = None
        self.connected = True
        self.pressedEventMap = {}
        self.releasedEventMap = {}
        self.changedEventMap = {}
        self.movedEventMap = {}

    def __del__(self):
        try:
            self.joystickFile.close()
        except AttributeError:
            pass

    def _setupReverseMaps(self):
        for index in self.buttonNames:
            self.buttonIndex[self.buttonNames[index]] = index
        for index in self.axisNames:
            self.axisIndex[self.axisNames[index]] = index

    def _getNextEventRaw(self):
        """Returns the next raw event from the gamepad.

        The return format is:
            timestamp (ms), value, event type code, axis / button number
        Throws an IOError if the gamepad is disconnected"""
        if self.connected:
            try:
                rawEvent = self.joystickFile.read(self.eventSize)
            except IOError as e:
                self.connected = False
                raise IOError('Gamepad %s disconnected: %s' % (self.joystickNumber, str(e)))
            if rawEvent is None:
                self.connected = False
                raise IOError('Gamepad %s disconnected' % self.joystickNumber)
            else:
                return struct.unpack('IhBB', rawEvent)
        else:
            raise IOError('Gamepad has been disconnected')

    def _rawEventToDescription(self, event):
        """Decodes the raw event from getNextEventRaw into a formatted string."""
        timestamp, value, eventType, index = event
        if eventType == Gamepad.EVENT_CODE_BUTTON:
            if index in self.buttonNames:
                button = self.buttonNames[index]
            else:
                button = str(index)
            if value == 0:
                return '%010u: Button %s released' % (timestamp, button)
            elif value == 1:
                return '%010u: button %s pressed' % (timestamp, button)
            else:
                return '%010u: button %s state %i' % (timestamp, button, value)
        elif eventType == Gamepad.EVENT_CODE_AXIS:
            if index in self.axisNames:
                axis = self.axisNames[index]
            else:
                axis = str(index)
            position = value / Gamepad.MAX_AXIS
            return '%010u: Axis %s at %+06.1f %%' % (timestamp, axis, position * 100)
        elif eventType == Gamepad.EVENT_CODE_INIT_BUTTON:
            if index in self.buttonNames:
                button = self.buttonNames[index]
            else:
                button = str(index)
            if value == 0:
                return '%010u: Button %s initially released' % (timestamp, button)
            elif value == 1:
                return '%010u: button %s initially pressed' % (timestamp, button)
            else:
                return '%010u: button %s initially state %i' % (timestamp, button, value)
        elif eventType == Gamepad.EVENT_CODE_INIT_AXIS:
            if index in self.axisNames:
                axis = self.axisNames[index]
            else:
                axis = str(index)
            position = value / Gamepad.MAX_AXIS
            return '%010u: Axis %s initially at %+06.1f %%' % (timestamp, axis, position * 100)
        else:
            return '%010u: Unknown event %u, Index %u, Value %i' % (timestamp, eventType, index, value)

    def getNextEvent(self, skipInit = True):
        """Returns the next event from the gamepad.

        The return format is:
            event name, entity name, value

        For button events the event name is BUTTON and value is either True or False.
        For axis events the event name is AXIS and value is between -1.0 and +1.0.

        Names are string based when found in the button / axis decode map.
        When not available the raw index is returned as an integer instead.

        After each call the internal state used by getPressed and getAxis is updated.

        Throws an IOError if the gamepad is disconnected"""
        self.lastTimestamp, value, eventType, index = self._getNextEventRaw()
        skip = False
        eventName = None
        entityName = None
        finalValue = None
        if eventType == Gamepad.EVENT_CODE_BUTTON:
            eventName = Gamepad.EVENT_BUTTON
            if index in self.buttonNames:
                entityName = self.buttonNames[index]
            else:
                entityName = index
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
        elif eventType == Gamepad.EVENT_CODE_AXIS:
            eventName = Gamepad.EVENT_AXIS
            if index in self.axisNames:
                entityName = self.axisNames[index]
            else:
                entityName = index
            finalValue = value / Gamepad.MAX_AXIS
            self.axisMap[index] = finalValue
            for callback in self.movedEventMap[index]:
                callback(finalValue)
        elif eventType == Gamepad.EVENT_CODE_INIT_BUTTON:
            eventName = Gamepad.EVENT_BUTTON
            if index in self.buttonNames:
                entityName = self.buttonNames[index]
            else:
                entityName = index
            if value == 0:
                finalValue = False
            else:
                finalValue = True
            self.pressedMap[index] = finalValue
            self.wasPressedMap[index] = False
            self.wasReleasedMap[index] = False
            self.pressedEventMap[index] = []
            self.releasedEventMap[index] = []
            self.changedEventMap[index] = []
            skip = skipInit
        elif eventType == Gamepad.EVENT_CODE_INIT_AXIS:
            eventName = Gamepad.EVENT_AXIS
            if index in self.axisNames:
                entityName = self.axisNames[index]
            else:
                entityName = index
            finalValue = value / Gamepad.MAX_AXIS
            self.axisMap[index] = finalValue
            self.movedEventMap[index] = []
            skip = skipInit
        else:
            skip = True

        if skip:
            return self.getNextEvent()
        else:
            return eventName, entityName, finalValue

    def updateState(self):
        """Updates the internal button and axis states with the next pending event.

        This call waits for a new event if there are not any waiting to be processed."""
        self.lastTimestamp, value, eventType, index = self._getNextEventRaw()
        if eventType == Gamepad.EVENT_CODE_BUTTON:
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
        elif eventType == Gamepad.EVENT_CODE_AXIS:
            finalValue = value / Gamepad.MAX_AXIS
            self.axisMap[index] = finalValue
            for callback in self.movedEventMap[index]:
                callback(finalValue)
        elif eventType == Gamepad.EVENT_CODE_INIT_BUTTON:
            if value == 0:
                finalValue = False
            else:
                finalValue = True
            self.pressedMap[index] = finalValue
            self.wasPressedMap[index] = False
            self.wasReleasedMap[index] = False
            self.pressedEventMap[index] = []
            self.releasedEventMap[index] = []
            self.changedEventMap[index] = []
        elif eventType == Gamepad.EVENT_CODE_INIT_AXIS:
            finalValue = value / Gamepad.MAX_AXIS
            self.axisMap[index] = finalValue
            self.movedEventMap[index] = []

    def startBackgroundUpdates(self, waitForReady = True):
        """Starts a background thread which keeps the gamepad state updated automatically.
        This allows for asynchronous gamepad updates and event callback code.

        Do not use with getNextEvent"""
        if self.updateThread is not None:
            if self.updateThread.running:
                raise RuntimeError('Called startBackgroundUpdates when the update thread is already running')
        self.updateThread = Gamepad.UpdateThread(self)
        self.updateThread.start()
        if waitForReady:
            while not self.isReady() and self.connected:
                time.sleep(1.0)

    def stopBackgroundUpdates(self):
        """Stops the background thread which keeps the gamepad state updated automatically.
        This may be called even if the background thread was never started.

        The thread will stop on the next event after this call was made."""
        if self.updateThread is not None:
            self.updateThread.running = False

    def isReady(self):
        """Used with updateState to indicate that the gamepad is now ready for use.

        This is usually after the first button press or stick movement."""
        return len(self.axisMap) + len(self.pressedMap) > 1

    def waitReady(self):
        """Convenience function which waits until the isReady call is True."""
        self.updateState()
        while not self.isReady() and self.connected:
            time.sleep(1.0)
            self.updateState()

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
        self.connected = False
        self.removeAllEventHandlers()
        self.stopBackgroundUpdates()
        del self.joystickFile


###############################################################################
# Gamepad classes and mappings
###############################################################################

class PS3(Gamepad):
    fullName = 'PlayStation 3 controller'

    def __init__(self, joystickNumber = 0):
        Gamepad.__init__(self, joystickNumber)
        self.axisNames = {
            0: 'LEFT-X',
            1: 'LEFT-Y',
            2: 'L2',
            3: 'RIGHT-X',
            4: 'RIGHT-Y',
            5: 'R2'
        }
        self.buttonNames = {
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
        self._setupReverseMaps()

class PS4(Gamepad):
    fullName = 'PlayStation 4 controller'

    def __init__(self, joystickNumber = 0):
        Gamepad.__init__(self, joystickNumber)
        self.axisNames = {
            0: 'LEFT-X',
            1: 'LEFT-Y',
            2: 'L2',
            3: 'RIGHT-X',
            4: 'RIGHT-Y',
            5: 'R2',
            6: 'DPAD-X',
            7: 'DPAD-Y'
        }
        self.buttonNames = {
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
        self._setupReverseMaps()

class PS5(Gamepad):
    fullName = 'PlayStation 5 controller'

    def __init__(self, joystickNumber = 0):
        Gamepad.__init__(self, joystickNumber)
        self.axisNames = {
            0: 'LEFT-X',
            1: 'LEFT-Y',
            2: 'L2',
            3: 'RIGHT-X',
            4: 'RIGHT-Y',
            5: 'R2',
            6: 'DPAD-X',
            7: 'DPAD-Y'
        }
        self.buttonNames = {
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
        self._setupReverseMaps()       

class Xbox360(Gamepad):
    fullName = 'Xbox 360 controller'

    def __init__(self, joystickNumber = 0):
        Gamepad.__init__(self, joystickNumber)
        self.axisNames = {
            0: 'LEFT-X',
            1: 'LEFT-Y',
            2: 'LT',
            3: 'RIGHT-X',
            4: 'RIGHT-Y',
            5: 'RT'
        }
        self.buttonNames = {
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
        self._setupReverseMaps()


class MMP1251(Gamepad):
    fullName = "ModMyPi Raspberry Pi Wireless USB Gamepad"

    def __init__(self, joystickNumber = 0):
        Gamepad.__init__(self, joystickNumber)
        self.axisNames = {
            0: 'LEFT-X',
            1: 'LEFT-Y',
            2: 'L2',
            3: 'RIGHT-X',
            4: 'RIGHT-Y',
            5: 'R2',
            6: 'DPAD-X',
            7: 'DPAD-Y'
        }
        self.buttonNames = {
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
        self._setupReverseMaps()

