from smbus2 import SMBus
from time import time, sleep
from math import atan2, degrees, sqrt
from threading import Thread, Event, Lock

from quadruped.interfaces import Status
from hardware.ina228_driver import INA228
from hardware.bno055_driver import BNO055, NDOF, CONFIGMODE
from hardware.interfaces import ImuData


"""
    Interfaces for hardware attached to RPI.

    Note:
        INA228 current sensor not physically installed in this early revision of the quadruped.
"""

###############################################################################
# Hardware Configuration
###############################################################################

SMBUS_ID = 1

# INA228 config:
POWER_SENSOR_I2C_ADDRESS = 0x40
POWER_SENSOR_SHUNT_RESISTANCE_OHMS = 0.005
POWER_SENSOR_MANUFACTURER_ID = 0x5449

# Battery:
# volts per cell * 6 LiPo cells
LOW_VOLTAGE_WARNING = 3.3 * 6
LOW_VOLTAGE_CRITICAL = 3.1 * 6


class Hardware:
    def __init__(self):

        self.tag = "Hardware"

        self.smbus_status: Status = Status.STANDBY
        self.imu_status: Status = Status.STANDBY

        self.loop_rate_seconds = 0.050

        self._init_smbus()
        self._init_imu()
        # self._init_power_sensor()

        self._start()

    ###############################################################################
    # SMBus
    ###############################################################################

    def _init_smbus(self):
        self.smbus_lock = Lock()

        print(f"[{self.tag}] initializing smbus (I2C)")
        try:
            self.bus: SMBus = SMBus(SMBUS_ID)
            self.smbus_status = Status.ACTIVE
        except Exception:
            print(f"[{self.tag}] error, smbus failed to init! Check connections and check if I2C is activated using raspi-config.")
            self.smbus_status = Status.ERROR

    def get_smbus_status(self) -> Status:
        return self.smbus_status

    ###############################################################################
    # Voltage / Current Sensor
    ###############################################################################

    def _init_power_sensor(self):
        self.voltage: float = 0
        self.current: float = 0
        self.power: float = 0
        self.power_lock = Lock()
        self.first_reading_complete: bool = False

        print(f"[{self.tag}] initializing INA228 power sensor")
        try:
            self.ina228 = INA228(
                bus=self.bus,
                address=POWER_SENSOR_I2C_ADDRESS,
                shunt_ohms=POWER_SENSOR_SHUNT_RESISTANCE_OHMS,
            )
            self.ina228.configure()

            id = self.ina228.get_manufacturer_id()
            if id == POWER_SENSOR_MANUFACTURER_ID:
                self.power_sensor_status = Status.ACTIVE
            else:
                print(f"[{self.tag}] error, INA228 power sensor failed to initialize! Manufacturer received id: {id}, expected: {POWER_SENSOR_MANUFACTURER_ID}")
                self.power_sensor_status = Status.ERROR
        except Exception:
            print(f"[{self.tag}] error, INA228 power sensor failed to initialize!")
            self.power_sensor_status = Status.ERROR

    def _process_power_sensor(self):
        if self.power_sensor_status is Status.ACTIVE:
            with self.smbus_lock:
                voltage = self.ina228.get_vbus_voltage()
            with self.smbus_lock:
                current = self.ina228.get_current()
            with self.smbus_lock:
                power = self.ina228.get_power()

            with self.power_lock:
                self.voltage = voltage
                self.current = current
                self.power = power

            if voltage > 0:
                self.first_reading_complete = True

    def get_voltage_status(self) -> Status:
        if self.first_reading_complete == False:
            return Status.STANDBY
        elif self.power_sensor_status is Status.ERROR:
            return Status.ERROR
        elif self.voltage < LOW_VOLTAGE_CRITICAL:
            return Status.CRITICAL
        elif self.voltage < LOW_VOLTAGE_WARNING:
            return Status.WARNING
        else:
            return Status.ACTIVE

    def get_current_status(self) -> Status:
        if self.power_sensor_status is Status.ERROR:
            return Status.ERROR
        else:
            return Status.ACTIVE

    def get_voltage(self) -> float:
        if self.power_sensor_status is Status.ERROR:
            return 0
        else:
            with self.power_lock:
                return self.voltage

    def get_current(self) -> float:
        if self.power_sensor_status is Status.ERROR:
            return 0
        else:
            with self.power_lock:
                return self.current

    def get_power(self) -> float:
        if self.power_sensor_status is Status.ERROR:
            return 0
        else:
            with self.power_lock:
                return self.power

    def get_power_sensor_status(self) -> Status:
        return self.power_sensor_status

    ###############################################################################
    # IMU
    ###############################################################################

    def _init_imu(self):
        self.imu_data = {"x": 0, "y": 0, "z": 0}

        print(f"[{self.tag}][IMU] initializing")
        try:
            with self.smbus_lock:
                self.imu = BNO055(self.bus)
                self.imu.set_mode(CONFIGMODE)
                sleep(0.05)
                self.imu.set_mode(NDOF)
                sleep(0.05)
                self.imu_status = Status.ACTIVE

        except Exception:
            self.imu_status = Status.ERROR
            print(f"[{self.tag}][IMU] error, IMU failed to initialize!")

    def _process_imu(self):
        if self.imu_status == Status.ACTIVE:
            with self.smbus_lock:
                try:
                    heading, roll, pitch = self.imu.get_euler_angles()

                    # Correct for physical IMU placement.
                    pitch += 180
                    if pitch > 180:
                        pitch -= 360


                    self.imu_data = ImuData(
                        roll=roll,
                        pitch=pitch,
                    )
                except Exception:
                    self.imu_status = Status.ERROR

    def get_imu_data(self) -> ImuData:
        if self.imu_status == Status.ACTIVE:
            return self.imu_data
        else:
            return ImuData(
                roll=0,
                pitch=0,
            )

    def get_imu_status(self) -> Status:
        return self.imu_status

    ###############################################################################
    # Worker
    ###############################################################################

    def _start(self):
        print(f"[{self.tag}] worker thread starting")
        self.loop_time: float = time()
        self.loop_completion_time_ms: float = 0
        self.exit_event: Event = Event()
        self.thread_handle = Thread(target=self._worker)
        self.thread_handle.start()

    def _stop(self):
        print(f"[{self.tag}] worker thread stoping")
        if self.thread_handle and self.thread_handle.is_alive():
            self.exit_event.set()
            self.thread_handle.join()

    def _worker(self):
        self.exit_event.clear()

        while not self.exit_event.is_set():

            # self._process_power_sensor()
            self._process_imu()

            delta = time() - self.loop_time

            sleep_time = self.loop_rate_seconds - delta
            if sleep_time > 0:
                sleep(sleep_time)

            if delta > self.loop_rate_seconds:
                print(f"[{self.tag}] Warning, loop time exceeded set rate! Loop time: {delta:0.3f}, set rate: {self.loop_rate_seconds:0.3f}")

            # print(f"[Loop] time to complete a loop: {delta:.3f}, sleep time: {sleep_time:.3f}")
            self.loop_completion_time_ms = delta * 1000
            self.loop_time = time()

        print(f"[{self.tag}] worker thread exiting")

    ###############################################################################
    # Other Methods
    ###############################################################################

    def shutdown(self):
        self._stop()
