import os
import can
from rich import print
from can.interface import Bus
from typing import Optional

from .interfaces import MotorName

"""
    Motor:
        mg4010e-i10-v3

    Info link:
        https://wiki.openelab.io/lkmtech/mg4010e-i10-v3-dual-encoder-robot-motor

    Docs:
        See docs directory for datasheets, drawings, etc.

    Basic specs:
        Rated torque: 2.5Nm
        Rated speed: 260rpm
        Rated voltage: 24V
        Rated current: 3.5A
        Communication: CAN
        Encoders: Dual (motor shaft and output shaft)
        Gearbox: 1:10 reduction ratio
        Weight: 250g

    Hardware driver notes:
        Does not contain a min and max position, there software is required to check for physical limits.
        
        CAN is not able to set the torque limit, speed limit, etc. Only the UART interface is capable
        of setting these parameters. The torque limit is used to create 'compliance'. A best guess is implemented.
    
    Software driver iver Notes:
        Upon startup the motor driver reports angles 0 to 360 degrees.
        To prevent issues of wrong initial directions, this library
        uses a -180 to 180 convention.
        Start up angles > 180 flag an offset to match the desired convention.

        Pid params are saved in RAM and must be applied after each power cycle.  
"""


class Motor:
    def __init__(
        self,
        name: MotorName,
        motor_id: int,
        min_angle: float,
        max_angle: float,
        inverse_rotation: bool,
        allow_comms: bool,
        allow_motion: bool,
        can_channel: str,
        bus: Bus,
    ):
        self.name: MotorName = name
        self.motor_id: int = motor_id
        self.min_angle: float = min_angle
        self.max_angle: float = max_angle
        self.inverse_rotation: bool = inverse_rotation
        self.allow_comms: bool = allow_comms
        self.allow_motion: bool = allow_motion
        self.can_channel: str = can_channel
        self.bus: Bus = bus

        self.tag = f"[Motor][{name}]"
        self.prints_enabled: bool = False

        # Motor states (from motor driver):
        self.temperature: int = 0
        self.voltage: float = 0
        self.current: float = 0
        self.motor_speed: int = 0
        self.encoder_position: int = 0
        self.position_degrees: float = 0

        # Motor fault states (from motor driver):
        self.under_voltage_protection: bool = False
        self.over_voltage_protection: bool = False
        self.over_temperature_protection: bool = False
        self.lost_input_protection: bool = False

        # Motor states:
        self.enabled: bool = False
        self.angle_limit_breached = False

        # Communication states:
        self.send_error: bool = False
        self.reply_timeout_seconds: float = 0.050
        self.reply_timeout_count: int = 0

        # Driver config:
        self.angle_pid_kp: int = 5  # Position loop, default: 100
        self.angle_pid_ki: int = 5  # Position loop, default: 100
        self.speed_pid_kp: int = 50  # Speed loop, default: 50
        self.speed_pid_ki: int = 40  # Speed loop, default: 40
        self.iq_pid_kp: int = 50  # Torque loop, default: 50
        self.iq_pid_ki: int = 50  # Torque loop, default: 50

        # Other config:
        self.apply_position_offset: bool = False
        self.max_reply_timeouts_allow: int = 3

        self.ARBRITATION_BASE_OFFSET: int = 0x140

    ###############################################################################
    # Operations
    ###############################################################################

    def op_can_send_message(self, motor_id: int, data: list):
        try:
            identifier = self.ARBRITATION_BASE_OFFSET + motor_id
            if self.prints_enabled:
                print(f"{self.tag} sending message, bus={self.bus.channel_info}, motor_id={motor_id}, arbitration_id=0x{identifier:X}, data={data}")
            msg = can.Message(is_extended_id=False, arbitration_id=identifier, data=data)
            self.bus.send(msg)
            self.send_error = False
            return True
        except Exception as e:
            self.send_error = True
            if self.prints_enabled:
                print(f"{self.tag}[op_can_send_message] {type(e).__name__} {e}")
            return False

    def op_wait_for_reply(self) -> Optional[can.Message]:
        reply = self.bus.recv(self.reply_timeout_seconds)
        if reply == None:
            self.reply_timeout_count += 1
        return reply

    ###############################################################################
    # Commands
    ###############################################################################

    def cmd_motor_on(self):
        if not self.op_can_send_message(self.motor_id, [0x88, 0, 0, 0, 0, 0, 0, 0]):
            return False
        reply = self.op_wait_for_reply()
        success = reply and self.motor_id == reply.arbitration_id - self.ARBRITATION_BASE_OFFSET
        if success:
            self.enabled = True
        return success

    def cmd_motor_off(self):
        if not self.op_can_send_message(self.motor_id, [0x80, 0, 0, 0, 0, 0, 0, 0]):
            return False
        reply = self.op_wait_for_reply()
        success = reply and self.motor_id == reply.arbitration_id - self.ARBRITATION_BASE_OFFSET
        if success:
            self.enabled = False
        return success

    def cmd_clear_motor_errors(self):
        if not self.op_can_send_message(self.motor_id, [0x9B, 0, 0, 0, 0, 0, 0, 0]):
            return False
        reply = self.op_wait_for_reply()
        return reply and self.motor_id == reply.arbitration_id - self.ARBRITATION_BASE_OFFSET

    def cmd_set_zero_to_current_pos(self):
        if not self.op_can_send_message(self.motor_id, [0x19, 0, 0, 0, 0, 0, 0, 0]):
            return False
        reply = self.op_wait_for_reply()
        return reply and self.motor_id == reply.arbitration_id - self.ARBRITATION_BASE_OFFSET

    def cmd_set_pid_to_ram(self, angle_kp: int, angle_ki: int, speed_kp: int, speed_ki: int, iq_kp: int, iq_ki: int):
        """
        Sets PID parameters to RAM; invalid upon power cycle.
        """
        if not self.op_can_send_message(self.motor_id, [0x31, 0, angle_kp, angle_ki, speed_kp, speed_ki, iq_kp, iq_ki]):
            return False
        reply = self.op_wait_for_reply()
        return reply and self.motor_id == reply.arbitration_id - self.ARBRITATION_BASE_OFFSET

    def cmd_set_angle_and_speed(
        self,
        angle: float,
        speed: int,
    ):
        """
        Sets speed and angle of the motor.
        Datasheet named as: cmd_motor_multi_angle_2
        """

        angle = angle * -1.0 if self.inverse_rotation else angle

        speed_low_byte = speed & 0x00FF
        speed_high_byte = speed >> 8 & 0x00FF
        angle_byte_0 = int(angle * 1000.0) >> 0 & 0x000000FF
        angle_byte_1 = int(angle * 1000.0) >> 8 & 0x000000FF
        angle_byte_2 = int(angle * 1000.0) >> 16 & 0x000000FF
        angle_byte_3 = int(angle * 1000.0) >> 24 & 0x000000FF
        if not self.op_can_send_message(self.motor_id, [0xA4, 0, speed_low_byte, speed_high_byte, angle_byte_0, angle_byte_1, angle_byte_2, angle_byte_3]):
            return False
        reply = self.op_wait_for_reply()
        return reply and self.motor_id == reply.arbitration_id - self.ARBRITATION_BASE_OFFSET

    ###############################################################################
    # Requests
    ###############################################################################

    def req_pid(self):
        if self.op_can_send_message(self.motor_id, [0x30, 0, 0, 0, 0, 0, 0, 0]):
            reply = self.op_wait_for_reply()
            if reply:
                reply_motor_id = reply.arbitration_id - self.ARBRITATION_BASE_OFFSET
                if self.motor_id == reply_motor_id and reply.data:
                    self.angle_kp = reply.data[2]
                    self.angle_ki = reply.data[3]
                    self.speed_kp = reply.data[4]
                    self.speed_ki = reply.data[5]
                    self.iq_kp = reply.data[6]
                    self.iq_ki = reply.data[7]
                    if self.prints_enabled:
                        print(
                            f"{self.tag }[M{reply_motor_id}] angle_kp: {self.angle_kp}, angle_ki: {self.angle_ki}, speed_kp: {self.speed_kp}, speed_ki: {self.speed_ki}, iq_kp: {self.iq_kp}, iq_ki: {self.iq_ki}"
                        )

    def req_state_1(self):
        if self.op_can_send_message(self.motor_id, [0x9A, 0, 0, 0, 0, 0, 0, 0]):
            reply = self.op_wait_for_reply()
            if reply:
                reply_motor_id = reply.arbitration_id - self.ARBRITATION_BASE_OFFSET
                if self.motor_id == reply_motor_id and reply.data:
                    self.temperature = reply.data[1]
                    self.voltage = (reply.data[2] | reply.data[3] << 8) / 100.0  # Datasheet is wrong, not DATA[3] and DATA[4].
                    self.under_voltage_protection = bool(reply.data[7] & 0b00000001)
                    self.over_voltage_protection = bool(reply.data[7] & 0b00000010)
                    self.over_temperature_protection = bool(reply.data[7] & 0b00001000)
                    self.lost_input_protection = bool(reply.data[7] & 0b10000000)
                    if self.prints_enabled:
                        print(
                            f"{self.tag }[M{reply_motor_id}] req_state_1 reply, temp.: {self.temperature}C, voltage: {self.voltage}V, UVP: {self.under_voltage_protection}, OVP: {self.over_voltage_protection}, OTP: {self.over_temperature_protection}, LIP:{self.lost_input_protection}"
                        )

    def req_state_2(self):
        if self.op_can_send_message(self.motor_id, [0x9C, 0, 0, 0, 0, 0, 0, 0]):
            reply = self.op_wait_for_reply()
            if reply:
                reply_motor_id = reply.arbitration_id - self.ARBRITATION_BASE_OFFSET
                if self.motor_id == reply_motor_id and reply.data:
                    self.temperature = reply.data[1]
                    current_raw = self.convert_twos_compliment(reply.data[2] | reply.data[3] << 8)
                    self.current = self.map_range(float(current_raw), -2000.0, 2000.0, -33.0, 33.0)
                    self.motor_speed = self.convert_twos_compliment(reply.data[4] | reply.data[5] << 8)
                    self.encoder_position = reply.data[6] | reply.data[7] << 8
                    if self.prints_enabled:
                        print(
                            f"{self.tag }[M{reply_motor_id}] req_state_2 reply, temp.: {self.temperature}C, current: {self.current}, motor speed: {self.motor_speed}, encoder position: {self.encoder_position}"
                        )

    def req_position(self):
        """
        Datasheet named as: req_motor_multi_angle
        """
        if not self.op_can_send_message(self.motor_id, [0x92, 0, 0, 0, 0, 0, 0, 0]):
            return None
        reply = self.op_wait_for_reply()
        if reply:
            reply_motor_id = reply.arbitration_id - self.ARBRITATION_BASE_OFFSET
            if self.motor_id == reply_motor_id:
                reply_data = reply.data

                # The data appears to be shifted right by 8 bits which breaks int64 twos compliment convention.
                raw_position: int = (
                    (reply_data[1] << 8)  # Low byte
                    | (reply_data[2] << 16)  # Byte 2
                    | (reply_data[3] << 24)  # Byte 3
                    | (reply_data[4] << 32)  # Byte 4
                    | (reply_data[5] << 40)  # Byte 5
                    | (reply_data[6] << 48)  # Byte 6
                    | (reply_data[7] << 56)
                )  # Byte 7

                converted_position_degrees = (self.convert_twos_compliment_64(raw_position) >> 8) / 1000.0
                offset_position_degrees = converted_position_degrees - 360.0 if self.apply_position_offset else converted_position_degrees
                self.position_degrees = offset_position_degrees * -1.0 if self.inverse_rotation else offset_position_degrees

                if self.prints_enabled:
                    print(f"{self.tag }[M{reply_motor_id}] req_motor_multi_angle reply, position: {self.position_degrees} degrees")

    ###############################################################################
    # Methods
    ###############################################################################

    def is_enabled(self) -> bool:
        return self.enabled

    def set_apply_position_offset(self, value: bool):
        self.apply_position_offset = value

    def is_error(self) -> bool:
        return self.is_hardware_error() or self.is_comms_error()

    def is_hardware_error(self) -> bool:
        return any([self.under_voltage_protection, self.over_voltage_protection, self.over_temperature_protection, self.lost_input_protection])

    def is_comms_error(self) -> bool:
        return self.send_error or self.reply_timeout_count > self.max_reply_timeouts_allow

    def clear_all_errors(self):
        self.under_voltage_protection = False
        self.over_voltage_protection = False
        self.over_temperature_protection = False
        self.lost_input_protection = False
        self.reply_timeout_count = 0

    ###############################################################################
    # Helpers
    ###############################################################################
    @staticmethod
    def convert_twos_compliment(value):
        if value >= 0x8000:  # 0x8000 is 32768 in decimal, the value of the MSB for 16-bit
            return value - 0x10000  # 0x10000 is 65536, the range of 16-bit unsigned integer
        return value

    @staticmethod
    def convert_twos_compliment_64(value):
        max_int64 = 2**63 - 1
        if value > max_int64:
            value -= 2**64
        return value

    @staticmethod
    def twos_complement_to_float_64(value):
        # Define the max value for signed 64-bit integer
        max_int64 = 2**63 - 1
        min_int64 = -(2**63)

        # Check if the value is negative in two's complement representation
        if value > max_int64:
            # Convert to negative equivalent
            value -= 2**64

        # Now value is a signed integer
        return float(value)

    @staticmethod
    def map_range(x, in_min, in_max, out_min, out_max):
        return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min
