#ifndef LKM_DRIVER_HH
#define LKM_DRIVER_HH

#include <cstdint>
#include <sys/types.h>
#include "mcp_can.h"
#include "lkm_driver_common.hh"

namespace lkm_m5
{
  struct MotorState
  {
    float tempareture;
    float position;
    float velocity;
    float effort;
  };

  struct MotorParameter
  {
    uint8_t angle_kp;
    uint8_t angle_ki;
    uint8_t speed_kp;
    uint8_t speed_ki;
    uint8_t iq_kp;
    uint8_t iq_ki;
  };

  struct EncoderState
  {
    float position;
    float raw_position;
    float offset;
  };

  class Driver
  {
  public:
    Driver(uint8_t master_can_id, uint8_t target_can_id, uint8_t motor_type, uint8_t encoder_type);
    virtual ~Driver();
    void init(MCP_CAN* p_can);
    bool motor_on();
    bool motor_off();
    bool stop_motor();
    bool open_loop_control(int16_t power);
    bool torque_closed_loop_control(float iq_control);
    bool speed_closed_loop_control(float speed);
    bool multi_loop_angle_control(float angle);
    bool multi_loop_angle_with_speed_control(float angle, float speed);
    bool single_loop_angle_control(uint8_t spin_dir, float angle);
    bool single_loop_angle_with_speed_control(uint8_t spin_dir, float angle, float speed);
    bool increment_angle_control(float angle);
    bool increment_angle_with_speed_control(float angle, float speed);
    bool read_pid_parameter();
    bool write_pid_parameter_to_ram(uint8_t angle_kp, uint8_t angle_ki, uint8_t speed_kp, uint8_t speed_ki, uint8_t iq_kp, uint8_t iq_ki);
    bool write_pid_parameter_to_rom(uint8_t angle_kp, uint8_t angle_ki, uint8_t speed_kp, uint8_t speed_ki, uint8_t iq_kp, uint8_t iq_ki);
    bool read_acceleration();
    bool write_acceleration_to_ram(float acc);
    bool read_encoder();
    bool write_encoder_value_to_rom_as_zero_point(uint16_t encoder_offset);
    bool write_current_position_to_rom_as_zero_point();
    bool read_multi_angle_loop();
    bool read_single_angle_loop();
    bool clear_motor_angle_loop();
    bool read_motor_state1();
    bool clear_motor_error_state();
    bool read_motor_state2();
    bool read_motor_state3();
    bool process_can_packet();
    bool process_response_packet(const Frame& frame);

    uint8_t motor_type() const { return motor_type_; }
    uint8_t encoder_type() const { return encoder_type_; }
    const MotorState & motor_state() const { return motor_state_; }
    const MotorParameter & motor_parameter() const { return motor_parameter_; }
    const EncoderState & encoder_state() const { return encoder_state_; }

  protected:
    bool send_motor_request(const Frame& packet);
    void print_can_packet(uint32_t id, uint8_t *data, uint8_t len);

  private:
    MCP_CAN* can_;                //!< can connection instance
    uint8_t master_can_id_;       //!< master can id
    uint8_t target_can_id_;       //!< target can id
    uint8_t receive_buffer_[64];  //!< receive buffer
    uint8_t motor_type_;
    uint8_t encoder_type_;
    unsigned long send_count_;
    MotorState motor_state_;
    MotorParameter motor_parameter_;
    EncoderState encoder_state_;
  };
};

#endif // !LKM_DRIVER_HH
