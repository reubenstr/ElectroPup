
/*




TODO:
  The way system errors bool and strings is magical and should be made it's own class
  to better allow code changes without risk of memory issues.

*/

#include <Arduino.h>
#include <math.h>
#include <SPI.h>
#include "TFT_eSPI.h"
#include "buzzer.h"
#include "main.h"

TFT_eSPI tft = TFT_eSPI();
Buzzer buzzer(PIN_MCU_BUZZER);

// TODO: move display pins to platformio.ini

const int cornerRadiusPx{2};

uint32_t lastMessageReceivedMillis;

Page page = Page::SYSTEM;

float batteryVoltage{0};

///////////////////////////////////////////////////////////////////////////////
// Program
///////////////////////////////////////////////////////////////////////////////

void HeartbeatLed()
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

  // TODO: force refresh on page change

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
  if (forceRefresh)
  {
    tft.setTextFont(2);
    tft.setTextSize(1);
    tft.setTextColor(TFT_DARKGREY);
    tft.drawString("SYSTEM", 64, 11);
    tft.drawString("MOTORS", 64, 76);

    tft.setTextFont(1);
    tft.setTextSize(1);
    tft.setTextColor(TFT_BLACK);
  }

  // SBC (RPI) errors take precedence of colors and requires refreshes.
  bool isSbcError = getValueFromStatusString("RPI") || getValueFromStatusString("SFT");
  static bool previousSbcStatus = isSbcError;
  if (previousSbcStatus != isSbcError)
  {
    previousSbcStatus = isSbcError;
    forceRefresh = true;
  }

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
        bool hasError = systemErrors[index];

        if (previousSystemStatus[index] != hasError || forceRefresh)
        {
          previousSystemStatus[index] = hasError;

          uint32_t color = hasError ? TFT_RED : TFT_GREEN;

          if (isSbcError)
          {
            if ((index != getValueFromStatusString("RPI") && !hasError) || (index != getValueFromStatusString("SFT") && !hasError))
            {
              color = TFT_DARKGREY;
            }
          }

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

          if (isSbcError)
            color = TFT_DARKGREY;

          tft.fillRoundRect(x * xMult + xOffset, y * yMult + yOffset, 26, 20, cornerRadiusPx, color);
          tft.drawString(motorStatusStrings[index], x * xMult + xOffset + 13, y * yMult + 10 + yOffset);
        }
        index++;
      }
    }
  }

  /* if (forceRefresh)
  {
    // tft.fillRect(79, 0, 2, tft.height(), TFT_GREEN);
    tft.drawLine(0, 0, tft.width() - 1, 0, TFT_GREEN);
    tft.drawLine(tft.width() - 1, 0, tft.width() - 1, tft.height() - 1, TFT_GREEN);
    tft.drawLine(tft.width() - 1, tft.height() - 1, 0, tft.height() - 1, TFT_GREEN);
    tft.drawLine(0, tft.height() - 1, 0, 0, TFT_GREEN);
  } */
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
  uint8_t data[1024];

  size_t numBytes = Serial1.readBytes((uint8_t *)&data, sizeof(data));
  if (numBytes)
  {

    MessageType messageType = static_cast<MessageType>(data[0]);

    if (messageType == MessageType::STATUS)
    {
      if (numBytes != sizeof(StatusMessage))
      {
        Serial.printf("[Comms] error, status message length does not match. Received: %u, expected: %u\n", numBytes, sizeof(StatusMessage));
        return;
      }

      StatusMessage message;
      memcpy(&message, data, sizeof(StatusMessage));
      uint32_t crc32Result = crc32((uint8_t *)&message, sizeof(StatusMessage) - sizeof(uint32_t));
      if (crc32Result == message.crc32)
      {
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
    else if (messageType == MessageType::PLAY_SOUND)
    {
      if (numBytes != sizeof(PlaySoundMessage))
      {
        Serial.printf("[Comms] error, play sound message length does not match. Received: %u, expected: %u\n", numBytes, sizeof(PlaySoundMessage));
        return;
      }

      PlaySoundMessage message;
      memcpy(&message, data, sizeof(PlaySoundMessage));
      uint32_t crc32Result = crc32((uint8_t *)&message, sizeof(PlaySoundMessage) - sizeof(uint32_t));
      if (crc32Result == message.crc32)
      {
        if (message.sequenceId > (int)Sequence::NONE && message.sequenceId < (int)Sequence::NUM_SOUNDS)
        {
          buzzer.play((Sequence)message.sequenceId);
        }
      }
      else
      {
        Serial.printf("Message CRC32 is invalid! Message CRC32: %X, calculated CRC32: %X \n", message.crc32, crc32Result);
      }
    }
    else
    {
      Serial.printf("[Comms] error, received unknown message type: %u\n", (int)messageType);
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
  pinMode(PIN_BTN_1, INPUT_PULLUP);
  pinMode(PIN_RPI_HEARTBEAT, INPUT);

  InitMessageComms();

  InitDisplay();
}

///////////////////////////////////////////////////////////////////////////////
// Main Loop
///////////////////////////////////////////////////////////////////////////////

void loop()
{
  HeartbeatLed();

  CheckUserButton();

  CheckForMessage();

  CheckCommsTimeout();

  CheckRpiHeartbeat();

  UpdateDisplay();

  buzzer.tick();

  if (digitalRead(PIN_BTN_1) == LOW)
  {
    if (!buzzer.isPlaying())
    {
      buzzer.play(Sequence::RPI_READY);
    }
  }
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