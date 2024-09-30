#include <Arduino.h>
#include <SPI.h>
#include "TFT_eSPI.h"
#include "CRC32.h"
#include "main.h"

TFT_eSPI tft = TFT_eSPI();

const uint32_t heartbeatBlinkRateMs{250};

#define TFT_CS PIN_A4
#define TFT_RST PIN_A2
#define TFT_DC PIN_A3

const int cornerRadiusPx{2};

uint32_t lastMessageReceivedMillis;
const uint32_t noCommsTimeoutMs{1000};

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

void InitDisplay()
{
  tft.begin();
  delay(25);
  tft.setRotation(2);
  delay(25);
  tft.fillScreen(TFT_BLACK);
  tft.setTextDatum(CC_DATUM);
}

void UpdateDisplay()
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
    const int xOffset = 7;
    const int yOffset = 20;
    const int xMult = 29;
    const int yMult = 24;
    int index = 0;
    for (int x = 0; x < 4; x++)
    {
      for (int y = 0; y < 2; y++)
      {
        uint32_t color = systemStatus[index] ? TFT_RED: TFT_GREEN;
        tft.fillRoundRect(x * xMult + xOffset, y * yMult + yOffset, 26, 20, cornerRadiusPx, color);
        tft.drawString(systemStatusStrings[index++], x * xMult + xOffset + 13, y * yMult + 10 + yOffset);
      }
    }
  }

  {
    // MOTORS
    const int xOffset = 7;
    const int yOffset = 86;
    const int xMult = 29;
    const int yMult = 24;

    int index = 0;
    for (int x = 0; x < 4; x++)
    {
      for (int y = 0; y < 3; y++)
      {
        uint32_t color = motorStatus[index] ? TFT_RED: TFT_GREEN;
        tft.fillRoundRect(x * xMult + xOffset, y * yMult + yOffset, 26, 20, cornerRadiusPx, color);
        tft.drawString(motorStatusStrings[index], x * xMult + xOffset + 13, y * yMult + 10 + yOffset);
        index++;
      }
    }
  }

  {
    // tft.fillRect(79, 0, 2, tft.height(), TFT_GREEN);
    tft.drawLine(0, 0, tft.width() - 1, 0, TFT_GREEN);
    tft.drawLine(tft.width() - 1, 0, tft.width() - 1, tft.height() - 1, TFT_GREEN);
    tft.drawLine(tft.width() - 1, tft.height() - 1, 0, tft.height() - 1, TFT_GREEN);
    tft.drawLine(0, tft.height() - 1, 0, 0, TFT_GREEN);
  }
}

void InitMessageComms()
{
  Serial1.begin(115200);
  Serial1.setTimeout(10);
}

void CheckForMessage()
{

  uint8_t data[256];

  Message message;

  if (Serial1.readBytes((uint8_t *)&message, sizeof(Message)))
  {

    CRC32 crc;
    crc.add((uint8_t *)&message, sizeof(MessageData));
    uint32_t crc32Result = crc.calc();

    if (crc.calc() == message.crc32)
    {
      Serial.println("Message CRC32 is valid.");
      lastMessageReceivedMillis = millis();

      systemStatus[0] = message.messageData.jointAngle;
      systemStatus[1] = message.messageData.inverseKinematics;
      systemStatus[2] = message.messageData.joystick;
      systemStatus[3] = message.messageData.overCurrent;

      for (int i = 0; i < numMotors; i++)
        motorStatus[i] = message.messageData.motorStatus[i];
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
  }
}

///////////////////////////////////////////////////////////////////////////////
// Entry
///////////////////////////////////////////////////////////////////////////////

void setup()
{

  Serial.begin(115200);

  pinMode(LED_BUILTIN, OUTPUT);

  InitMessageComms();

  InitDisplay();
}

///////////////////////////////////////////////////////////////////////////////
// Main Loop
///////////////////////////////////////////////////////////////////////////////

void loop()
{
  HeartBeat();

  CheckForMessage();

  CheckCommsTimeout();

  UpdateDisplay();

  delay(1000);
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