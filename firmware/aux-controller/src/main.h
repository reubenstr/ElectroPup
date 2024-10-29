///////////////////////////////////////////////////////////////////////////////
// Pins
///////////////////////////////////////////////////////////////////////////////

#define PIN_BTN_1 PC14
#define PIN_RPI_HEARTBEAT PB12
#define PIN_MCU_BUZZER PB9

///////////////////////////////////////////////////////////////////////////////
// Timings
///////////////////////////////////////////////////////////////////////////////

const uint32_t heartbeatBlinkRateMs{250};
const uint32_t noCommsTimeoutMs{1000};
const uint32_t rpiHeartbeatTimeoutMs{250};
const uint32_t byteLongPressActivationMs{3000};

///////////////////////////////////////////////////////////////////////////////
// General
///////////////////////////////////////////////////////////////////////////////

const float lowBatteryPercentThreashold{0.20};

///////////////////////////////////////////////////////////////////////////////
// Display
///////////////////////////////////////////////////////////////////////////////

enum class Page
{
    SPLASH,
    SYSTEM,
    BATTERY
};

const uint8_t numSystemStatusStrings{16};
const char *systemStatusStrings[numSystemStatusStrings] = {"RPI", "SFT", "JOY", "LIM", "JA", "IK", "CAN", "OTe", "UVo", "MCo", "SEN", "---"};
const char *motorStatusStrings[] = {"FLA", "FLH", "FLK", "FRA", "FRH", "FRK", "BLA", "BLH", "BLK", "BRA", "BRH", "BRK"};

///////////////////////////////////////////////////////////////////////////////
// Message Structs and Data
///////////////////////////////////////////////////////////////////////////////

const int numSystemStatus{8};
bool systemErrors[numSystemStatus];

const int numMotors{12};
bool motorOns[numMotors];
bool motorErrors[numMotors];

#pragma pack(1)
struct StatusData
{
    bool joystickError;

    bool physicalLimitError;
    bool jointAngleError;
    bool inverseKinematicsError;

    bool canError;
    bool overTemperatureError;
    bool underVoltageError;
    bool motorCommunicationError;

    bool sensorError;

    bool motorOns[numMotors];
    bool motorErrors[numMotors];

    float batteryVoltage;
};

enum class MessageType : uint8_t
{
    STATUS = 0,
    PLAY_SOUND,
    SHUTDOWN_RPI
};

#pragma pack(1)
struct StatusMessage
{
    MessageType messageType;
    StatusData statusData;
    uint32_t crc32;
};

#pragma pack(1)
struct PlaySoundMessage
{
    MessageType messageType;
    uint8_t sequenceId;
    uint32_t crc32;
};

#pragma pack(1)
struct ShutDownMessage
{
    MessageType messageType;
    uint32_t crc32;

    ShutDownMessage()
    {
        messageType = MessageType::SHUTDOWN_RPI;
    }
};

///////////////////////////////////////////////////////////////////////////////
// Prototypes
///////////////////////////////////////////////////////////////////////////////

void InitDisplay();
void UpdateDisplay(bool forceRefresh);
void DisplaySplashPage();
void DisplaySystemPage(bool forceRefresh);
void DisplayBatteryPage(bool forceRefresh);

bool IsLowBattery();
bool IsError();

///////////////////////////////////////////////////////////////////////////////
// Helpers
///////////////////////////////////////////////////////////////////////////////

// TODO: an assert of other warning should be applied of the string is not found.

int getIndexFromStatusString(const char *status)
{
    for (int i = 0; i < numSystemStatusStrings; ++i)
    {
        if (strcmp(status, systemStatusStrings[i]) == 0)
        {
            return i;
        }
    }
    return -1;
}

int getValueFromStatusString(const char *status)
{
    int index = getIndexFromStatusString(status);

    if (index > 0)
        return systemErrors[index];
    else
        return false;
}

void setValueFromStatusString(const char *status, bool state)
{
    int index = getIndexFromStatusString(status);

    if (index > 0)
        systemErrors[index] = state;
}

///////////////////////////////////////////////////////////////////////////////
// CRC
///////////////////////////////////////////////////////////////////////////////

uint32_t crc32(uint8_t *data, int length)
{
    const uint32_t POLYNOMIAL = 0x04C11DB7;
    uint32_t crc = 0xFFFFFFFF;

    for (size_t i = 0; i < length; i++)
    {
        crc ^= data[i] << 24;
        for (int j = 0; j < 8; ++j)
        {
            if (crc & 0x80000000)
            {
                crc = (crc << 1) ^ POLYNOMIAL;
            }
            else
            {
                crc <<= 1;
            }
            crc &= 0xFFFFFFFF;
        }
    }
    return crc ^ 0xFFFFFFFF;
}
