
/* Messages sent from the UI received by the robot */

export enum Command {
    NO_UPDATE = 'no_update',
    E_STOP = 'e_stop',
    SIT = 'sit',
    STAND = 'stand',
    POSE = 'pose',
    WALK = 'walk',
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


/* Messages sent by the robot received by the UI */

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
    body: CoordinateSeries;
    legs: CoordinateSeries[];
    support: CoordinateSeries;
}

export interface PlotDataExtras {
    trajectories: CoordinateSeries[];
    transitions: CoordinateSeries[];
    rings: CoordinateSeries[];
    holdTrajectories: CoordinateSeries[];
}

export interface MotorValues {
    temperature: number;
    voltage: number;
    current: number;
    motorSpeed: number;
    encoderPosition: number;
    positionDegrees: number;
}

export interface MotorFaults {
    underVoltageProtection: boolean;
    overVoltageProtection: boolean;
    overTemperatureProtection: boolean;
    lostInputProtection: boolean;
}

export interface MotorState {
    id: number;
    minAngle: number;
    maxAngle: number;
    inverseRotation: boolean;
    allowComms: boolean;
    allowMotion: boolean;
    canChannel: string;
    enabled: boolean;
    commsError: boolean;
    values: MotorValues;
    faults: MotorFaults;
}


export enum Status {
    None = 'none',
    Standby = 'standby',
    Active = 'active',
    Warning = 'warning',
    Critical = 'critical',
    Error = 'error',
}

interface SystemStatus {
    opMode: {
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
        main: number;
        motion: number;
        can0: number;
        can1: number;
    };
    motor: {
        status: Status
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
    rightBack: boolean;
    leftFront: boolean;
    leftBack: boolean;
}


interface IkParameters {
    forwardTranslation: number;
    sideTranslation: number;
    heightTranslation: number;
    roll: number;
    pitch: number;
    yaw: number;
    forwardTranslationMin: number;
    forwardTranslationMax: number;
    sideTranslationMin: number;
    sideTranslationMax: number;
    heightTranslationMin: number;
    heightTranslationMax: number;
    rollMin: number;
    rollMax: number;
    pitchMin: number;
    pitchMax: number;
    yawMin: number;
    yawMax: number;
}

interface MotionParameters {
    forwardVelocity: number;
    lateralVelocity: number;
    angularVelocity: number;
}

export interface Data {
    timestamp: number;
    plotSim: PlotData;
    plotLive: PlotData;
    plotExtras: PlotDataExtras;
    status: SystemStatus;
    contacts: Contacts;
    motors: {
        [key: string]: MotorState;
    };
    ikParameters: IkParameters;
    motionParameters: MotionParameters;
}
