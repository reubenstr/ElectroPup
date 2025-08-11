
/*
  Project:
    Auxiliary Board for ElectroPup quadruped.
    Drives a LCD display, buzzer, Neopixels strips, RC servo, and more.

  MCU:
    STM32F401CC

  Dev. Board:
    WeAct Black Pill:
      https://stm32-base.org/boards/STM32F401CCU6-WeAct-Black-Pill-V1.2.html
      https://www.aliexpress.us/item/3256801269871873.html
      https://www.amazon.com/dp/B09MLHYF89/

    Alternatives (Blue Pill and other Black Pill):
      STM32F103C8T6
      STM32F411CEU6

  Display:
    The TFT_eSPI library (LCD driver) configuration is located in platformio.ini
    ST7735 128*160 1.8"
    https://www.aliexpress.us/item/3256806134563059.html

  PCB/Schematics:
    See PCBs directory in the the ElectroPup repo for schematics:
      https://github.com/reubenstr/ElectroPup

  TODO:
    System error bools and strings are magical; should they be made into their own enum and/or class?
 */

#include <Arduino.h>
#include <math.h>
#include <SPI.h>
#include "TFT_eSPI.h"
#include "OneButton.h"
#include "buzzer.h"
#include "neopixels.h"
#include "main.h"

TFT_eSPI tft = TFT_eSPI();
Buzzer buzzer(PIN_MCU_BUZZER);
OneButton button(PIN_BTN_1, true);
Neopixels neopixels(PIN_NEO_0, PIN_NEO_1);

Page page = Page::SYSTEM;
const int cornerRadiusPx{2};

uint32_t lastMessageReceivedMillis;

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

// Black Pill STM32 onboard button.
void CheckUserButton()
{
  if (digitalRead(USER_BTN) == LOW)
  {
    Serial.println("Blackpill onboard button is pressed.");
    delay(500);
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

  // SBC (RPI) errors take precedence of colors and requires refreshes.
  bool isSbcError = getValueFromStatusString("RPI") || getValueFromStatusString("SFT");
  static bool previousSbcStatus;
  if (previousSbcStatus != isSbcError)
  {
    previousSbcStatus = isSbcError;
    forceRefresh = true;
  }

  if (forceRefresh)
  {
    tft.setTextFont(1);
    tft.setTextSize(1);
    tft.setTextColor(TFT_BLACK);
  }

  {
    // SYSTEM
    static bool previousSystemStatus[numSystemStatus];
    const int xOffset = 7;
    const int yOffset = 5;
    const int xMult = 29;
    const int yMult = 24;
    int index = 0;
    for (int x = 0; x < 4; x++)
    {
      for (int y = 0; y < 3; y++)
      {
        bool hasError = systemErrors[index];

        if (previousSystemStatus[index] != hasError || forceRefresh)
        {
          previousSystemStatus[index] = hasError;

          uint32_t color = hasError ? TFT_RED : TFT_GREEN;

          if (isSbcError)
          {
            if ((index != getIndexFromStatusString("RPI") && !hasError) || (index != getIndexFromStatusString("SFT") && !hasError))
            {
              color = TFT_DARKGREY;
            }
          }
          else if (index == getIndexFromStatusString("JOY") && systemValues.joystickBatteryPercentage < systemLowBatteryPercentThreashold)
          {    
            color = TFT_YELLOW;
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
          previousMotorOns[index] = motorOn;
          previousMotorErrors[index] = hasError;
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

// TODO: DRY crc error message.
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

        setValueFromStatusString("JOY", message.statusData.joystickError);
        setValueFromStatusString("LIM", message.statusData.physicalLimitError);
        setValueFromStatusString("JA", message.statusData.jointAngleError);
        setValueFromStatusString("IK", message.statusData.inverseKinematicsError);
        setValueFromStatusString("CAN", message.statusData.canError);
        setValueFromStatusString("OTe", message.statusData.overTemperatureError);
        setValueFromStatusString("UVo", message.statusData.underVoltageError);
        setValueFromStatusString("MCo", message.statusData.motorCommunicationError);
        setValueFromStatusString("IMU", message.statusData.imuError);
        setValueFromStatusString("---", false);

        for (int i = 0; i < numMotors; i++)
        {
          motorOns[i] = message.statusData.motorOns[i];
          motorErrors[i] = message.statusData.motorErrors[i];
        }

        systemValues.batteryVoltage = message.statusData.batteryVoltage;
        systemValues.joystickBatteryPercentage = message.statusData.joystickBatteryPercentage;
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
    setValueFromStatusString("SFT", true);
  }
  else
  {
    setValueFromStatusString("SFT", false);
  }
}

///////////////////////////////////////////////////////////////////////////////
// Calculations
///////////////////////////////////////////////////////////////////////////////

float CalcBatteryPercent()
{
  // https://electronics.stackexchange.com/questions/435837/calculate-battery-percentage-on-lipo-battery
  return 123 - (123 / pow(1 + pow(systemValues.batteryVoltage / 3.7, 80), 0.165));
}

bool IsLowBattery()
{
  return CalcBatteryPercent() < systemLowBatteryPercentThreashold;
}

///////////////////////////////////////////////////////////////////////////////
// Misc.
///////////////////////////////////////////////////////////////////////////////

// Raspberry Pi sends a heartbeat as square wave changing state every 0.250 seconds.
void CheckRpiHeartbeat()
{
  static bool previousHeartbeatState{true};
  static bool rpiHasError{true};
  static bool previousRpiHasError{true};
  static uint32_t start{0};

  if (digitalRead(PIN_RPI_HEARTBEAT) != previousHeartbeatState)
  {
    previousHeartbeatState = digitalRead(PIN_RPI_HEARTBEAT);
    start = millis();
    rpiHasError = false;
  }

  if (millis() - start > rpiHeartbeatTimeoutMs)
  {
    rpiHasError = true;
  }

  if (previousRpiHasError != rpiHasError)
  {
    previousRpiHasError = rpiHasError;

    setValueFromStatusString("RPI", rpiHasError);

    if (rpiHasError)
      buzzer.play(Sequence::RPI_OFF);
    else
      buzzer.play(Sequence::RPI_ON);
  }
}

void ProcessNeopixels()
{
  static bool inStartState{true};

  bool error = false;
  for (int i = 0; i < numSystemStatus; i++)
  {
    if (systemErrors[i])
      error = true;
  }

  // Don't change starting pattern until all errors are clear,
  // which means the RPI has booted and is ready.
  if (!error)
  {
    inStartState = false;
  }

  if (inStartState)
  {
    neopixels.setMode(PixelMode::SPARKLE, PixelColor::RED);
  }
  else
  {
    if (error)
    {
      neopixels.setMode(PixelMode::ERROR, PixelColor::RED);
    }
    else
    {
      bool allMotorsOn{true};
      for (int i = 0; i < numMotors; i++)
      {
        if (!motorOns[i])
          allMotorsOn = false;
      }
      if (allMotorsOn)
        neopixels.setMode(PixelMode::RIDER, PixelColor::RED);
      else
        neopixels.setMode(PixelMode::RIDER, PixelColor::BLUE);
    }
  }

  neopixels.tick();
}

///////////////////////////////////////////////////////////////////////////////
// Handle Button Inputs
///////////////////////////////////////////////////////////////////////////////

void btnClick(void *oneButton)
{
  Serial.println("btnClick");

  buzzer.play(Sequence::BTN_BEEP_SHORT);
}

void btnDoubleClick(void *oneButton)
{
  Serial.println("btnDoubleClick");
}

void btnLongPressStart(void *oneButton)
{
  ShutDownMessage message;
  uint32_t crc32Result = crc32((uint8_t *)&message, sizeof(ShutDownMessage) - sizeof(uint32_t));
  message.crc32 = crc32Result;
  Serial1.write((uint8_t *)&message, sizeof(ShutDownMessage));
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

  // Expected errors at startup; prevents sound from starting during init.
  setValueFromStatusString("RPI", true);
  setValueFromStatusString("SFT", true);

  button.attachClick(btnClick, &button);
  button.attachDoubleClick(btnDoubleClick, &button);
  button.attachLongPressStart(btnLongPressStart, &button);
  button.setPressMs(byteLongPressActivationMs);
  button.setClickMs(100);

  neopixels.init();

  InitMessageComms();

  InitDisplay();

  buzzer.play(Sequence::MCU_STARTUP);
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

  button.tick();

  ProcessNeopixels();
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