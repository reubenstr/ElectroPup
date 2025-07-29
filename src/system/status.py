from enum import Enum
from dataclasses import dataclass, field
from system.interfaces import MotionState, SystemStates, OpModes, Status, InputMode
from system.quadruped.gait_planner import Gait

@dataclass
class Canbus:
    status: Status = Status.NONE


@dataclass
class Current:
    current: str = "N/A"
    status: Status = Status.NONE


@dataclass
class Gait:
    state: Gait = Gait.NONE


@dataclass
class Gamepad:
    battery: str = "N/A"
    status: Status = Status.NONE


@dataclass
class GenericStatus:
    status: Status = Status.NONE

@dataclass
class IMU:
    roll: str = "N/A"
    pitch: str = "N/A"
    status: Status = Status.NONE


@dataclass
class Motion:
    state: MotionState = MotionState.NONE


@dataclass
class OperationMode:
    state: OpModes = OpModes.NA


@dataclass
class PowerSensor:
    status: Status = Status.NONE


@dataclass
class SMBus:
    status: Status = Status.NONE


@dataclass
class System:
    state: SystemStates = SystemStates.INIT


@dataclass
class Voltage:
    voltage: str = "N/A"
    status: Status = Status.NONE


@dataclass
class Input:
    state: InputMode = InputMode.NA


@dataclass
class Gpio:
    status: Status = Status.NONE

@dataclass
class LoopTimes:
    main: float = 0
    motion: float = 0
    can0: float = 0
    can1: float = 0


@dataclass
class SystemStatus:
    opMode: OperationMode = field(default_factory=OperationMode)
    system: System = field(default_factory=System)
    motion: Motion = field(default_factory=Motion)
    target_motion: Motion = field(default_factory=Motion)
    ik: GenericStatus = field(default_factory=GenericStatus)
    joint_angle: GenericStatus = field(default_factory=GenericStatus)
    gait: Gait = field(default_factory=Gait)
    input: Input = field(default_factory=Input)
    loopTimes: LoopTimes = field(default_factory=LoopTimes)
    
    gpio: Gpio = field(default_factory=Gpio)
    smbus: SMBus = field(default_factory=SMBus)
    power_sensor: PowerSensor = field(default_factory=PowerSensor)
    imu: IMU = field(default_factory=IMU)
    can0: Canbus = field(default_factory=Canbus)
    can1: Canbus = field(default_factory=Canbus)
    gamepad: Gamepad = field(default_factory=Gamepad)        
  
    voltage: Voltage = field(default_factory=Voltage)
    current: Current = field(default_factory=Current)
      
