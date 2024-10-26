
/*






TODO:
  The way system errors bool and strings is magical and should be made it's own class
  to better allow code changes without risk of memory issues.

*/

#include <Arduino.h>
#include <math.h>
#include <SPI.h>
#include "TFT_eSPI.h"
#include "main.h"

TFT_eSPI tft = TFT_eSPI();

// TODO: move display pins to platformio.ini

const int cornerRadiusPx{2};

uint32_t lastMessageReceivedMillis;

Page page = Page::SYSTEM;

float batteryVoltage{0};

///////////////////////////////////////////////////////////////////////////////
// Program
///////////////////////////////////////////////////////////////////////////////

void HeartBeat()
{
  static uint32_t start{0};
  static bool toggle{false};

  if (millis() - start > heartbeatBlinkRateMs)
  {
    start = millis();
    digitalWrite(LED_BUILTIN, !digitalRead(LED_BUILTIN));
  }
}

void CheckUserButton()
{
  if (digitalRead(USER_BTN) == LOW)
  {
    Serial.println("USER BTN TEST");
    delay(100);
  }
}

///////////////////////////////////////////////////////////////////////////////
// Display
///////////////////////////////////////////////////////////////////////////////

void InitDisplay()
{
  tft.begin();
  delay(25);
  tft.setRotation(2);
  delay(25);
  tft.fillScreen(TFT_BLACK);
  tft.setTextDatum(CC_DATUM);

  UpdateDisplay(true);
}

void UpdateDisplay(bool forceRefresh = false)
{
  if (page == Page::SPLASH)
  {
    DisplaySplashPage();
  }
  else if (page == Page::SYSTEM)
  {
    DisplaySystemPage(forceRefresh);
  }
  else if (page == Page::BATTERY)
  {
    DisplayBatteryPage(forceRefresh);
  }
}

void DisplaySplashPage()
{
}

void DisplaySystemPage(bool forceRefresh = false)
{
  tft.setTextFont(2);
  tft.setTextSize(1);
  tft.setTextColor(TFT_GREEN);
  tft.drawString("SYSTEM", 64, 11);
  tft.drawString("MOTORS", 64, 76);

  tft.setTextFont(1);
  tft.setTextSize(1);
  tft.setTextColor(TFT_BLACK);

  {
    // SYSTEM
    static bool previousSystemStatus[numSystemStatus];
    const int xOffset = 7;
    const int yOffset = 20;
    const int xMult = 29;
    const int yMult = 24;
    int index = 0;
    for (int x = 0; x < 4; x++)
    {
      for (int y = 0; y < 2; y++)
      {
        if (previousSystemStatus[index] != systemErrors[index] || forceRefresh)
        {
          previousSystemStatus[index] = systemErrors[index];

          uint32_t color = systemErrors[index] ? TFT_RED : TFT_GREEN;
          tft.fillRoundRect(x * xMult + xOffset, y * yMult + yOffset, 26, 20, cornerRadiusPx, color);
          tft.drawString(systemStatusStrings[index], x * xMult + xOffset + 13, y * yMult + 10 + yOffset);
        }
        index++;
      }
    }
  }

  {
    // MOTORS
    static bool previousMotorOns[numMotors];
    static bool previousMotorErrors[numMotors];
    const int xOffset = 7;
    const int yOffset = 86;
    const int xMult = 29;
    const int yMult = 24;

    int index = 0;
    for (int x = 0; x < 4; x++)
    {
      for (int y = 0; y < 3; y++)
      {
        bool motorOn = motorOns[index];
        bool hasError = motorErrors[index];

        if (previousMotorOns[index] != motorOn || previousMotorErrors[index] != hasError || forceRefresh)
        {
          previousMotorOns[index] = hasError;
          previousMotorErrors[index] = motorOn;
          uint32_t color = hasError ? TFT_RED : motorOn ? TFT_GREEN
                                                        : TFT_BLUE;
          tft.fillRoundRect(x * xMult + xOffset, y * yMult + yOffset, 26, 20, cornerRadiusPx, color);
          tft.drawString(motorStatusStrings[index], x * xMult + xOffset + 13, y * yMult + 10 + yOffset);
        }
        index++;
      }
    }
  }

  if (forceRefresh)
  {
    // tft.fillRect(79, 0, 2, tft.height(), TFT_GREEN);
    tft.drawLine(0, 0, tft.width() - 1, 0, TFT_GREEN);
    tft.drawLine(tft.width() - 1, 0, tft.width() - 1, tft.height() - 1, TFT_GREEN);
    tft.drawLine(tft.width() - 1, tft.height() - 1, 0, tft.height() - 1, TFT_GREEN);
    tft.drawLine(0, tft.height() - 1, 0, 0, TFT_GREEN);
  }
}

void DisplayBatteryPage(bool forceRefresh = false)
{
}

///////////////////////////////////////////////////////////////////////////////
// Communications
///////////////////////////////////////////////////////////////////////////////

void InitMessageComms()
{
  Serial1.begin(115200);
  Serial1.setTimeout(10);
}

void CheckForMessage()
{
  uint8_t data[256];

  StatusMessage message;

  if (Serial1.readBytes((uint8_t *)&message, sizeof(StatusMessage)))
  {
    uint32_t crc32Result = crc32((uint8_t *)&message, sizeof(StatusData));

    if (crc32Result == message.crc32)
    {
      Serial.println("Message CRC32 is valid.");
      lastMessageReceivedMillis = millis();

      systemErrors[getIndexFromStatusString("RPI")] = false;
      systemErrors[getIndexFromStatusString("JA")] = message.statusData.jointAngleError;
      systemErrors[getIndexFromStatusString("IK")] = message.statusData.inverseKinematicsError;
      systemErrors[getIndexFromStatusString("JOY")] = message.statusData.joystickError;
      systemErrors[getIndexFromStatusString("OC")] = message.statusData.overCurrentError;
      systemErrors[getIndexFromStatusString("UV")] = message.statusData.overCurrentError;
      systemErrors[getIndexFromStatusString("CAN")] = message.statusData.canError;

      for (int i = 0; i < numMotors; i++)
      {
        motorOns[i] = message.statusData.motorOns[i];
        motorErrors[i] = message.statusData.motorErrors[i];
      }

      batteryVoltage = message.statusData.batteryVoltage;
    }
    else
    {
      Serial.printf("Message CRC32 is invalid! Message CRC32: %X, calculated CRC32: %X \n", message.crc32, crc32Result);
    }
  }
}

void CheckCommsTimeout()
{
  if (millis() - lastMessageReceivedMillis > noCommsTimeoutMs)
  {
    systemErrors[getIndexFromStatusString("SFT")] = true;
  }
  else
  {
    systemErrors[getIndexFromStatusString("SFT")] = false;
  }
}

///////////////////////////////////////////////////////////////////////////////
// Calculations
///////////////////////////////////////////////////////////////////////////////

float CalcBatteryPercent()
{
  // https://electronics.stackexchange.com/questions/435837/calculate-battery-percentage-on-lipo-battery
  return 123 - (123 / pow(1 + pow(batteryVoltage / 3.7, 80), 0.165));
}

bool IsLowBattery()
{
  return CalcBatteryPercent() < lowBatteryPercentThreashold;
}

bool IsError()
{
  for (int i = 0; i < numSystemStatus; i++)
  {
    if (systemErrors[i])
      return true;
  }

  for (int i = 0; i < numMotors; i++)
  {
    if (motorErrors[i])
      return true;
  }

  return false;
}

///////////////////////////////////////////////////////////////////////////////
// Misc.
///////////////////////////////////////////////////////////////////////////////

void CheckRpiHeartbeat()
{
  static bool previousState{false};
  static uint32_t start{0};

  if (digitalRead(PIN_RPI_HEARTBEAT) != previousState)
  {
    previousState = digitalRead(PIN_RPI_HEARTBEAT);
    start = millis();
    systemErrors[getIndexFromStatusString("RPI")] = false;
  }
  else if (millis() - start > rpiHeartbeatTimeoutMs)
  {
    systemErrors[getIndexFromStatusString("RPI")] = true;
  }
}

///////////////////////////////////////////////////////////////////////////////
// Entry
///////////////////////////////////////////////////////////////////////////////

void setup()
{

  Serial.begin(115200);

  pinMode(LED_BUILTIN, OUTPUT);
  pinMode(USER_BTN, INPUT_PULLUP);
  pinMode(PIN_RPI_HEARTBEAT, INPUT);

  InitMessageComms();

  InitDisplay();
}

///////////////////////////////////////////////////////////////////////////////
// Main Loop
///////////////////////////////////////////////////////////////////////////////

void loop()
{
  HeartBeat();

  CheckUserButton();

  CheckForMessage();

  CheckCommsTimeout();

  CheckRpiHeartbeat();

  UpdateDisplay();
}

/*
 if (display == Display::Splash)
  {
    tft.pushImage(0, 0, splashWidth, splashHeight, splash);
  }
  else if (display == Display::SelectDifficulty)
  {
    Logo bit array created using Lcd Image Converter
    https://sourceforge.net/projects/lcd-image-converter/
    Use the following conversion settings:
    Type: Color
    Block Size: 16 bit
    Byte Order: Big-Endian
    Either "Convert" and save the file to copy the array into this file,
    or copy the array from the "Preview" option in the Conversion options window.
*/