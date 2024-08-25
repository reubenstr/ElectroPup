#ifndef LKM_PACKET_HH
#define LKM_PACKET_HH

#include "lkm_driver_common.hh"
#include "lkm_driver_defs.hh"

#include <M5Stack.h>
#undef min
#undef max

#include <cmath>
#include <algorithm>
#include <cstdint>
#include <cstring>
#include <sys/select.h>

namespace lkm_m5 {

  class Packet
  {
  public:
    Packet(uint8_t type, uint8_t len) : type_(type), frame_(len) {}
    Packet(uint8_t type, const Frame& frame) : type_(type), frame_(frame) {}
    virtual ~Packet() {}
    uint8_t type() const { return type_; }
    const Frame & frame() const {return frame_;}

  protected:
    Frame frame_;

  private:
    uint8_t type_;
  };

  class RequestPacket : public Packet
  {
  public:
    RequestPacket(uint8_t type, uint8_t len) : Packet(type, len) {}
    virtual ~RequestPacket() {}
    virtual bool pack() {
      frame_[0] = type();
      return true;
    }
  };

  class ResponsePacket : public Packet
  {
  public:
    ResponsePacket(uint8_t type, const Frame & frame) : Packet(type, frame) {}
    virtual ~ResponsePacket() {}
    virtual bool unpack() {
      if (frame_[0] != type()) return false;
      return true;
    }
  };

  class MotorStateResponsePacket : public ResponsePacket
  {
  public:
    MotorStateResponsePacket(uint8_t type, const Frame& frame, uint8_t motor_type, uint8_t encoder_type)
      : ResponsePacket(type, frame)
      , motor_type_(motor_type)
      , encoder_type_(encoder_type)
      , tempareture_(0.0f)
      , torque_current_(0.0f)
      , speed_(0.0f)
      , position_(0.0f)
    {}

    virtual ~MotorStateResponsePacket() {}
    virtual bool unpack() {
      if (!ResponsePacket::unpack()) return false;
      tempareture_ = frame_[1];

      // set torque current
      int16_t current = 0.0f;
      std::memcpy(&current, frame_.data() + 2, sizeof(current));
      if (motor_type_ == MOTOR_SERIES_MS) {
        torque_current_ = current;
      } else if (motor_type_ == MOTOR_SERIES_MF) {
        torque_current_ = MF_SERIES_MAX_TORQUE * current / 2048.0f;
      } else if (motor_type_ == MOTOR_SERIES_MG) {
        torque_current_ = MG_SERIES_MAX_TORQUE * current / 2048.0f;
      }

      // set speed
      int16_t speed_dps = 0;
      std::memcpy(&speed_dps, frame_.data() + 4, sizeof(speed_dps));
      speed_ = speed_dps / 180.0f * M_PI;

      // set position
      uint16_t position_step = 0;
      std::memcpy(&position_step, frame_.data() + 6, sizeof(position_step));

      if (encoder_type_ == ENCODER_TYPE_14_BIT) {
        position_ = position_step / 16383.0f * 2.0f * M_PI;
      } else if (encoder_type_ == ENCODER_TYPE_16_BIT) {
        position_ = position_step / 32767.0f * 2.0f * M_PI;
      } else if (encoder_type_ == ENCODER_TYPE_18_BIT) {
        position_ = position_step / 65535.0f * 2.0f * M_PI;
      } else {
        // error
        position_ = 0.0f;
      }
      return true;
    }

    // accessor
    float tempareture() const { return tempareture_; }
    float torque_current() const { return torque_current_; }
    float speed() const { return speed_; }
    float position() const { return position_; }

  private:
    uint8_t motor_type_;
    uint8_t encoder_type_;
    float tempareture_;
    float torque_current_;
    float speed_;
    float position_;
  };

  class PIDResponsePacket : public ResponsePacket
  {
  public:
    PIDResponsePacket(uint8_t type, const Frame& frame)
      : ResponsePacket(type, frame)
    {}

    virtual ~PIDResponsePacket() {}

    virtual bool unpack() {
      if (!ResponsePacket::unpack()) return false;
      angle_kp_ = frame_[2];
      angle_ki_ = frame_[3];
      speed_kp_ = frame_[4];
      speed_ki_ = frame_[5];
      iq_kp_ = frame_[6];
      iq_ki_ = frame_[7];
      return true;
    }

    uint8_t angle_kp() const { return angle_kp_; }
    uint8_t angle_ki() const { return angle_ki_; }
    uint8_t speed_kp() const { return speed_kp_; }
    uint8_t speed_ki() const { return speed_ki_; }
    uint8_t iq_kp() const { return iq_kp_; }
    uint8_t iq_ki() const { return iq_ki_; }

  private:
    uint8_t angle_kp_;
    uint8_t angle_ki_;
    uint8_t speed_kp_;
    uint8_t speed_ki_;
    uint8_t iq_kp_;
    uint8_t iq_ki_;
  };

  class ReadEncoderResponsePacket: public ResponsePacket
  {
  public:
    ReadEncoderResponsePacket(const Frame& frame, uint8_t encoder_type)
      : ResponsePacket(CMD_READ_ENCODER, frame)
      , encoder_type_(encoder_type)
    {}

    virtual ~ReadEncoderResponsePacket() {}

    virtual bool unpack() {
      if (!ResponsePacket::unpack()) return false;

      uint16_t position_step;
      std::memcpy(&position_step, frame_.data() + 2, sizeof(position_step));

      uint16_t raw_position_step;
      std::memcpy(&raw_position_step, frame_.data() + 4, sizeof(raw_position_step));

      uint16_t offset;
      std::memcpy(&offset, frame_.data() + 6, sizeof(offset));

      if (encoder_type_ == ENCODER_TYPE_14_BIT) {
        encoder_position_ = position_step / 16383.0f * 2.0f * M_PI;
        encoder_raw_position_ = raw_position_step / 16383.0f * 2.0f * M_PI;
        encoder_offset_ = offset / 16383.0f * 2.0f * M_PI;
      } else if (encoder_type_ == ENCODER_TYPE_16_BIT) {
        encoder_position_ = position_step / 32767.0f * 2.0f * M_PI;
        encoder_raw_position_ = raw_position_step / 32767.0f * 2.0f * M_PI;
        encoder_offset_ = offset / 32767.0f * 2.0f * M_PI;
      } else if (encoder_type_ == ENCODER_TYPE_18_BIT) {
        encoder_position_ = position_step / 65535.0f * 2.0f * M_PI;
        encoder_raw_position_ = raw_position_step / 65535.0f * 2.0f * M_PI;
        encoder_offset_ = offset / 65535.0f * 2.0f * M_PI;
      } else {
        // error
        encoder_position_ = 0.0f;
        encoder_raw_position_ = 0.0f;
        encoder_offset_ = 0.0f;
      }
      return true;
    }

    float encoder_position() const { return encoder_position_; }
    float encoder_raw_position() const { return encoder_raw_position_; }
    float encoder_offset() const { return encoder_offset_; }

  private:
    uint8_t encoder_type_;
    float encoder_position_;
    float encoder_raw_position_;
    float encoder_offset_;
  };

  class OpenLoopControlRequestPacket : public RequestPacket
  {
  public:
    explicit OpenLoopControlRequestPacket(int16_t power_control)
      : RequestPacket(CMD_OPEN_LOOP_CONTROL, 8)
    {
      power_control_ = std::max(std::min(power_control, static_cast<int16_t>(MS_SERIES_MAX_POWER)), static_cast<int16_t>(-MS_SERIES_MAX_POWER));
    }

    int16_t power_control() const { return power_control_; };

    virtual bool pack() {
      if (!RequestPacket::pack()) return false;
      std::memcpy(frame_.data() + 4, &power_control_, sizeof(power_control_));
      return true;
    }

  private:
    int16_t power_control_;
  };

  class TorqueClosedLoopControlRequestPacket : public RequestPacket
  {
  public:
    TorqueClosedLoopControlRequestPacket(float iq_control, uint8_t motor_type)
      : RequestPacket(CMD_TORQUE_CLOSED_LOOP_CONTROL, 8)
      , motor_type_(motor_type)
    {
      if (motor_type == MOTOR_SERIES_MF) {
        iq_control_ = std::max(std::min(iq_control, MF_SERIES_MAX_TORQUE), -MF_SERIES_MAX_TORQUE);

      } else if (motor_type == MOTOR_SERIES_MG) {
        iq_control_ = std::max(std::min(iq_control, MG_SERIES_MAX_TORQUE), -MG_SERIES_MAX_TORQUE);

      } else {
        // unknown motor type
        iq_control_ = 0.0f;
      }
    }

    virtual bool pack() {
      if (!RequestPacket::pack()) return false;

      int16_t control = 0;
      if (motor_type_ == MOTOR_SERIES_MF) {
        control = static_cast<int16_t>(iq_control_ / MF_SERIES_MAX_TORQUE * 2048);

      } else if (motor_type_ == MOTOR_SERIES_MG) {
        control = static_cast<int16_t>(iq_control_ / MG_SERIES_MAX_TORQUE * 2048);
      }
      std::memcpy(frame_.data() + 4, &control, sizeof(control));
      return true;
    }

  private:
    float iq_control_;
    uint8_t motor_type_;
  };

  class SpeedClosedLoopControlRequestPacket: public RequestPacket
  {
  public:
    explicit SpeedClosedLoopControlRequestPacket(float speed)
      : RequestPacket(CMD_SPEED_CLOSED_LOOP_CONTROL, 8)
      , speed_(speed)
    {}

    virtual bool pack() {
      if (!RequestPacket::pack()) return false;
      int32_t speed_dps = static_cast<int32_t>(speed_ * 180.0f / M_PI * 100.0f);
      std::memcpy(frame_.data() + 4, &speed_dps, sizeof(int32_t));
      return true;
    }

  private:
    float speed_;
  };

  class MultiLoopAngleControlRequestPacket: public RequestPacket
  {
  public:
    explicit MultiLoopAngleControlRequestPacket(float angle)
      : RequestPacket(CMD_MULTI_LOOP_ANGLE_CONTROL_1, 8)
      , angle_(angle)
    {}

    virtual bool pack() {
      if (!RequestPacket::pack()) return false;
      int32_t angle_deg = static_cast<int32_t>(angle_ * 180.0f / M_PI * 100.0);
      std::memcpy(frame_.data() + 4, &angle_deg, sizeof(int32_t));
      return true;
    }

  private:
    float angle_;
  };

  class MultiLoopAngleControlWithSpeedRequestPacket: public RequestPacket
  {
  public:
    MultiLoopAngleControlWithSpeedRequestPacket(float angle, float speed)
      : RequestPacket(CMD_MULTI_LOOP_ANGLE_CONTROL_2, 8)
      , angle_(angle)
      , speed_(speed)
    {}

    virtual bool pack() {
      if (!RequestPacket::pack()) return false;
      uint16_t speed_dps = static_cast<uint16_t>(std::abs(speed_dps) * 180.0f / M_PI * 100.0);
      std::memcpy(frame_.data() + 2, &speed_dps, sizeof(speed_dps));

      int32_t angle_deg = static_cast<int32_t>(angle_ * 180.0f / M_PI * 100.0);
      std::memcpy(frame_.data() + 4, &angle_deg, sizeof(int32_t));
      return true;
    }

  private:
    float angle_;
    float speed_;
  };

  class SingleLoopAngleControlRequestPacket: public RequestPacket
  {
  public:
    SingleLoopAngleControlRequestPacket(uint8_t spin_dir, float angle)
      : RequestPacket(CMD_SINGLE_LOOP_ANGLE_CONTROL_1, 8)
      , spin_dir_(spin_dir)
      , angle_(angle)
    {}

    virtual bool pack() {
      if (!RequestPacket::pack()) return false;
      frame_[1] = spin_dir_;
      uint32_t angle_deg = static_cast<uint32_t>(angle_ * 180.0f / M_PI * 100.0);
      std::memcpy(frame_.data() + 4, &angle_deg, sizeof(uint32_t));
      return true;
    }

  private:
    uint8_t spin_dir_;
    float angle_;
  };

  class SingleLoopAngleControlWithSpeedRequestPacket: public RequestPacket
  {
  public:
    SingleLoopAngleControlWithSpeedRequestPacket(uint8_t spin_dir, float angle, float speed)
      : RequestPacket(CMD_SINGLE_LOOP_ANGLE_CONTROL_2, 8)
      , spin_dir_(spin_dir)
      , angle_(angle)
      , speed_(speed)
    {}

    virtual bool pack() {
      if (!RequestPacket::pack()) return false;
      frame_[1] = spin_dir_;
      uint16_t speed_dps = static_cast<uint16_t>(speed_ * 180.0f / M_PI);
      std::memcpy(frame_.data() + 2, &speed_dps, sizeof(uint16_t));

      uint32_t angle_deg = static_cast<uint32_t>(angle_ * 180.0f / M_PI * 100.0f);
      std::memcpy(frame_.data() + 4, &angle_deg, sizeof(uint32_t));
      return true;
    }

  private:
    uint8_t spin_dir_;
    float angle_;
    float speed_;
  };

  class IncrementAngleControlRequestPacket: public RequestPacket
  {
  public:
    IncrementAngleControlRequestPacket(float angle)
      : RequestPacket(CMD_INCREMENT_ANGLE_CONTROL_1, 8)
      , angle_(angle)
    {}

    virtual bool pack() {
      if (!RequestPacket::pack()) return false;
      int32_t angle_deg = static_cast<int32_t>(angle_ * 180.0f / M_PI * 100.0f);
      std::memcpy(frame_.data() + 4, &angle_deg, sizeof(int32_t));
      return true;
    }

  private:
    float angle_;
  };

  class IncrementAngleControlWithSpeedRequestPacket: public RequestPacket
  {
  public:
    IncrementAngleControlWithSpeedRequestPacket(float angle, float speed)
      : RequestPacket(CMD_INCREMENT_ANGLE_CONTROL_2, 8)
      , angle_(angle)
      , speed_(speed)
    {}

    virtual bool pack() {
      if (!RequestPacket::pack()) return false;
      uint16_t speed_dps = static_cast<uint16_t>(speed_ * 180.0f / M_PI);
      std::memcpy(frame_.data() + 2, &speed_dps, sizeof(uint16_t));

      int32_t angle_deg = static_cast<int32_t>(angle_ * 180.0f / M_PI * 100.0f);
      std::memcpy(frame_.data() + 4, &angle_deg, sizeof(int32_t));
      return true;
    }

  private:
    float angle_;
    float speed_;
  };

  class WritePIDParameterToRAMRequestPacket: public RequestPacket
  {
  public:
    WritePIDParameterToRAMRequestPacket(uint8_t angle_kp, uint8_t angle_ki, uint8_t speed_kp, uint8_t speed_ki, uint8_t iq_kp, uint8_t iq_ki)
      : RequestPacket(CMD_WRITE_PID_PARAMTER_TO_RAM, 8)
      , angle_kp_(angle_kp), angle_ki_(angle_ki), speed_kp_(speed_kp), speed_ki_(speed_ki), iq_kp_(iq_kp), iq_ki_(iq_ki)
    {}

    virtual bool pack() {
      if (!RequestPacket::pack()) return false;
      frame_[2] = angle_kp_;
      frame_[3] = angle_ki_;
      frame_[4] = speed_kp_;
      frame_[5] = speed_ki_;
      frame_[6] = iq_kp_;
      frame_[7] = iq_ki_;
      return true;
    }

  private:
    uint8_t angle_kp_;
    uint8_t angle_ki_;
    uint8_t speed_kp_;
    uint8_t speed_ki_;
    uint8_t iq_kp_;
    uint8_t iq_ki_;
  };

  class WritePIDParameterToROMRequestPacket: public RequestPacket
  {
  public:
    WritePIDParameterToROMRequestPacket(uint8_t angle_kp, uint8_t angle_ki, uint8_t speed_kp, uint8_t speed_ki, uint8_t iq_kp, uint8_t iq_ki)
      : RequestPacket(CMD_WRITE_PID_PARAMTER_TO_ROM, 8)
      , angle_kp_(angle_kp), angle_ki_(angle_ki), speed_kp_(speed_kp), speed_ki_(speed_ki), iq_kp_(iq_kp), iq_ki_(iq_ki)
    {}

    virtual bool pack() {
      if (!RequestPacket::pack()) return false;
      frame_[2] = angle_kp_;
      frame_[3] = angle_ki_;
      frame_[4] = speed_kp_;
      frame_[5] = speed_ki_;
      frame_[6] = iq_kp_;
      frame_[7] = iq_ki_;
      return true;
    }

  private:
    uint8_t angle_kp_;
    uint8_t angle_ki_;
    uint8_t speed_kp_;
    uint8_t speed_ki_;
    uint8_t iq_kp_;
    uint8_t iq_ki_;
  };

  class WriteAccerelationToRAMRequestPacket: public RequestPacket
  {
  public:
    WriteAccerelationToRAMRequestPacket(float acc)
      : RequestPacket(CMD_WRITE_ACCELERATION, 8)
      , accerelation_(acc)
    {}

  private:
    float accerelation_;
  };

  class WriteEncoderValueToROMAsZeroPointRequestPacket: public RequestPacket
  {
  public:
    WriteEncoderValueToROMAsZeroPointRequestPacket(uint16_t encoder_offset)
      : RequestPacket(CMD_WRITE_ACCELERATION, 8)
      , encoder_offset_(encoder_offset)
    {}

    virtual bool pack() {
      if (!RequestPacket::pack()) return false;
      std::memcpy(frame_.data() + 6, &encoder_offset_, sizeof(encoder_offset_));
      return true;
    }

  private:
    uint16_t encoder_offset_;
  };
}

#endif // !LKM_PACKET_HH
