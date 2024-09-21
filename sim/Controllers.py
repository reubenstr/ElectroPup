# coding: utf-8

"""
Standard gamepad mappings.

Pulled in to Gamepad.py directly.
"""



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



