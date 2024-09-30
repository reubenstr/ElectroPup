

const int numSystemStatus{8};
bool systemStatus[numSystemStatus];

const int numMotors{12};
bool motorStatus[numMotors];

#pragma pack(1)
struct MessageData
{
    bool jointAngle;
    bool inverseKinematics;
    bool joystick;
    bool overCurrent;

    bool motorStatus[numMotors];
};

#pragma pack(1)
struct Message
{
    MessageData messageData;
    uint32_t crc32;
};

const char *systemStatusStrings[] = {"JA", "IK", "JS", "RP", "SW", "OC", "BA", ""};
const char *motorStatusStrings[] = {"FLA", "FLH", "FLK", "FRA", "FRH", "FRK", "BLA", "BLH", "BLK", "BRA", "BRH", "BRK"};