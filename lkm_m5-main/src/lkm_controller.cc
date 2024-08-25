#include "lkm_controller.hh"
#include "lkm_driver.hh"
#include <memory>

using namespace lkm_m5;


Controller::Controller(uint8_t master_can_id)
  : p_can_(NULL)
  , configs_()
  , drivers_()
  , master_can_id_(master_can_id)
{}

Controller::~Controller()
{}

bool Controller::init(MCP_CAN* p_can, const std::vector<MotorConfig> & configs)
{
  p_can_ = p_can;
  configs_ = configs;

  for (auto config : configs)
  {
    drivers_[config.id] = std::make_shared<Driver>(master_can_id_, config.id, config.motor_type, config.encoder_type);
    drivers_[config.id]->init(p_can_);
  }
  return true;
}

bool Controller::motor_on()
{
  bool ret = false;
  for (auto config : configs_) {
    ret &= drivers_[config.id]->motor_on();
  }
  return ret;
}

bool Controller::motor_off()
{
  bool ret = false;
  for (auto config : configs_) {
    ret &= drivers_[config.id]->motor_off();
  }
  return true;
}

bool Controller::motor_stop()
{
  bool ret = false;
  for (auto config : configs_) {
    ret &= drivers_[config.id]->stop_motor();
  }
  return true;
}

DriverPtr Controller::driver(uint8_t id)
{
  if (drivers_.find(id) == drivers_.end()) return nullptr;
  return drivers_[id];
}

bool Controller::process_can_packet()
{
  if (p_can_->checkReceive() != CAN_MSGAVAIL) {
    return false;
  }

  while (p_can_->checkReceive() == CAN_MSGAVAIL) {
    // receive data
    unsigned long id;
    uint8_t len;
    p_can_->readMsgBuf(&id, &len, receive_buffer_);

    // parse packet --------------
    Frame frame(receive_buffer_, receive_buffer_ + len);
    uint8_t mot_id = static_cast<uint8_t>(id - 0x0140);

    if (drivers_.find(mot_id) != drivers_.end()) {
      drivers_[mot_id]->process_response_packet(frame);
    }
  }
  return true;
}
