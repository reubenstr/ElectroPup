#ifndef LKM_DRIVER_DEFS_HH
#define LKM_DRIVER_DEFS_HH

#define CMD_MOTOR_OFF                           0x80
#define CMD_MOTOR_ON                            0x88
#define CMD_MOTOR_STOP                          0x81
#define CMD_OPEN_LOOP_CONTROL                   0xA0
#define CMD_TORQUE_CLOSED_LOOP_CONTROL          0xA1
#define CMD_SPEED_CLOSED_LOOP_CONTROL           0xA2
#define CMD_MULTI_LOOP_ANGLE_CONTROL_1          0xA3
#define CMD_MULTI_LOOP_ANGLE_CONTROL_2          0xA4
#define CMD_SINGLE_LOOP_ANGLE_CONTROL_1         0xA5
#define CMD_SINGLE_LOOP_ANGLE_CONTROL_2         0xA6
#define CMD_INCREMENT_ANGLE_CONTROL_1           0xA7
#define CMD_INCREMENT_ANGLE_CONTROL_2           0xA8
#define CMD_READ_PID_PARAMTER                   0x30
#define CMD_WRITE_PID_PARAMTER_TO_RAM           0x31
#define CMD_WRITE_PID_PARAMTER_TO_ROM           0x32
#define CMD_READ_ACCELERATION                   0x33
#define CMD_WRITE_ACCELERATION                  0x34
#define CMD_READ_ENCODER                        0x90
#define CMD_WRITE_ENCODER_VALUE_TO_ROM_AS_THE_MOTOR_ZERO_POINT     0x91
#define CMD_WRITE_CURRENT_POSITION_TO_RON_AS_THE_MOTOR_ZERO_POINT  0x19
#define CMD_READ_MULTI_ANGLE_LOOP               0x92
#define CMD_READ_SINGLE_ANGLE_LOOP              0x94
#define CMD_CLEAR_MOTOR_ANGLE_LOOP              0x95
#define CMD_READ_MOTOR_STATE_1_AND_ERROR_STATE  0x9A
#define CMD_CLEAR_MOTOR_ERROR_STATE             0x9B
#define CMD_READ_MOTOR_STATE_2                  0x9C
#define CMD_READ_MOTOR_STATE_3                  0x9D

#define MOTOR_SERIES_MS   0x00
#define MOTOR_SERIES_MF   0x01
#define MOTOR_SERIES_MG   0x02
#define MF_SERIES_MAX_TORQUE 16.5f
#define MG_SERIES_MAX_TORQUE 33.0f
#define MS_SERIES_MAX_POWER 850
#define ENCODER_TYPE_14_BIT 0x00
#define ENCODER_TYPE_16_BIT 0x01
#define ENCODER_TYPE_18_BIT 0x02

#endif // !LKM_DRIVER_DEFS_HH
