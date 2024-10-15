
///////////////////////////////////////////////////////////////////////////////
// Timings
///////////////////////////////////////////////////////////////////////////////

const uint32_t heartbeatBlinkRateMs{250};

///////////////////////////////////////////////////////////////////////////////
// General
///////////////////////////////////////////////////////////////////////////////

const float lowBatteryPercent{0.20};

///////////////////////////////////////////////////////////////////////////////
// Display
///////////////////////////////////////////////////////////////////////////////

enum class Page
{
    SPLASH,
    SYSTEM,
    BATTERY
};

const char *systemStatusStrings[] = {"JA", "IK", "JOY", "RPI", "SW", "OC", "BA", "CAN"};
const char *motorStatusStrings[] = {"FLA", "FLH", "FLK", "FRA", "FRH", "FRK", "BLA", "BLH", "BLK", "BRA", "BRH", "BRK"};

///////////////////////////////////////////////////////////////////////////////
// Message Structs and Data
///////////////////////////////////////////////////////////////////////////////

const int numSystemStatus{8};
bool systemErrors[numSystemStatus];

const int numMotors{12};
bool motorErrors[numMotors];

#pragma pack(1)
struct MessageData
{
    /*bool jointAngleError;
    bool inverseKinematicsError;
    bool joystickError;
    bool overCurrentError;

    bool motorErrors[numMotors];*/

    float batteryVoltage;
};

#pragma pack(1)
struct Message
{
    MessageData messageData;
    uint32_t crc32;
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
// Temp Helpers
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
