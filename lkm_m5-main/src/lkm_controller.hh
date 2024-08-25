#ifndef LKM_CONTROLLER_HH
#define LKM_CONTROLLER_HH

#include <cstdint>
#include <unordered_map>
#include <vector>
#include <memory>
#include "lkm_driver.hh"

namespace lkm_m5
{
  struct MotorConfig
  {
    uint8_t id;
    uint8_t motor_type;
    uint8_t encoder_type;
  };

  typedef std::shared_ptr<Driver> DriverPtr;

  class Controller
  {
  public:
    explicit Controller(uint8_t master_can_id);
    virtual ~Controller();

    bool init(MCP_CAN* p_can, const std::vector<MotorConfig> & configs);
    bool motor_on();
    bool motor_off();
    bool motor_stop();
    DriverPtr driver(uint8_t id);
    bool process_can_packet();

  private:
    uint8_t master_can_id_;
    MCP_CAN * p_can_;
    uint8_t receive_buffer_[64];  //!< receive buffer
    std::vector<MotorConfig> configs_;
    std::unordered_map<uint8_t, DriverPtr> drivers_;
  };

}; // end namespace lkm_m5

#endif // !LKM_CONTROLLER_HH
