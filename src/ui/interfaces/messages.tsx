
/* Messages sent from the UI received by the Hexapod */

export enum Command {
    NO_UPDATE = 'no_update',
    E_STOP = 'e_stop',
    SIT = 'sit',
    STAND = 'stand',
    POSE = 'pose',
    BIAS_WALK = 'bias_walk',
    VECTOR_WALK = 'vector_walk',
    GAMEPAD_INPUT = 'gamepad_input',
    TOUCH_INPUT = 'touch_input'
}

export interface ControlMessage {
    leftX: number;
    leftY: number;
    rightX: number;
    rightY: number;
    command: Command;
}


/* Messages sent by the Hexapod received by the UI */

interface Coordinate {
    x: number;
    y: number;
    z: number;
}

interface CoordinateSeries {
    name: string;
    x: number[];
    y: number[];
    z: number[];
}

export interface PlotData {
    cog: Coordinate;
    body: CoordinateSeries;
    legs: CoordinateSeries[];
    mesh: CoordinateSeries;
    trajectories: CoordinateSeries[];
    softTrajectories: CoordinateSeries[];
    rings: CoordinateSeries[];
}

interface MotorFaults {
    notCalibrated: boolean;
    hallEncoderFailure: boolean;
    magEncoderFailure: boolean;
    overTemperature: boolean;
    overCurrent: boolean;
    underVoltage: boolean;
}

interface MotorErrors {
    communications: boolean;
    position: boolean;
    fault: boolean;
}

interface MotorValues {
    enabled: boolean;
    position: number | null;
    velocity: number;
    torque: number;
    temperature: number;
}

interface MotorTargets {
    position: number | null;
    speed: number | null;
}

interface MotorState {
    targets: MotorTargets;
    values: MotorValues;
    errors: MotorErrors;
    faults: MotorFaults;
}

export enum Status {
    None = 'none',
    Standby = 'standy',
    Active = 'active',
    Warning = 'warning',
    Critical = 'critical',
    Error = 'error',
}

interface SystemStatus {
    opMode: {
        state: string;
    };
    system: {
        state: string;
    };
    motion: {
        state: string;
    };
    targetMotion: {
        state: string;
    };
    ik: {
        status: Status;
    };
    jointAngle: {
        status: Status;
    };
    gait: {
        state: string;
    };
    input: {
        state: string;
    };
    loopTimes: {
        mainLoop: number;
        can0: number;
        can1: number;
    };

    gpio: {
        status: Status;
    };
    smbus: {
        status: Status;
    };
    powerSensor: {
        status: Status;
    };
    imu: {
        roll: string;
        pitch: string;
        status: Status;
    };
    expander: {
        status: Status;
    };
    can0: {
        status: Status;
    };
    can1: {
        status: Status;
    };
    gamepad: {
        battery: string;
        status: Status;
    };
    motorPower: {
        status: Status;
    };
    voltage: {
        voltage: string;
        status: Status;
    };
    current: {
        current: string;
        status: Status;
    };
}


interface Contacts {
    error: boolean;
    rightFront: boolean;
    rightMiddle: boolean;
    rightBack: boolean;
    leftFront: boolean;
    leftMiddle: boolean;
    leftBack: boolean;
}


interface IkParameters {
    translateX: number;
    translateY: number;
    translateZ: number;
    rotateX: number;
    rotateY: number;
    rotateZ: number;
    translateXMin: number;
    translateXMax: number;
    translateYMin: number;
    translateYMax: number;
    translateZMin: number;
    translateZMax: number;
    rotateXMin: number;
    rotateXMax: number;
    rotateYMin: number;
    rotateYMax: number;
    rotateZMin: number;
    rotateZMax: number;
}

export interface QuadData {
    timestamp: number;
    plotSim: PlotData;
    plotLive: PlotData;
    status: SystemStatus;
    contacts: Contacts;
    motors: {
        [key: string]: MotorState;
    };
    ikParameters: IkParameters;
}
