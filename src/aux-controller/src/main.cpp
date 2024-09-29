#include <Arduino.h>
#include <SPI.h>
#include "TFT_eSPI.h"

TFT_eSPI tft = TFT_eSPI();

const uint32_t heartbeatBlinkRateMs{250};

#define TFT_CS PIN_A4
#define TFT_RST PIN_A2
#define TFT_DC PIN_A3

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
  tft.setRotation(1);
  delay(25);
  tft.fillScreen(TFT_BLACK);
  tft.setTextDatum(CC_DATUM);
}

void UpdateDisplay()
{
  tft.setTextFont(2);
  tft.setTextSize(1);
  tft.setTextColor(TFT_GREEN);
  tft.drawString("SYSTEM", 40, 15);
  tft.drawString("MOTORS", 120, 15);

  tft.setTextFont(1);
  tft.setTextSize(1);
  tft.setTextColor(TFT_BLACK);

  const int cornerRadiusPx{1};
  const int xOffset = 85;
  const int yOffset = 28;
  const int xMult = 25;
  const int yMult = 25;

  int index = 0;
  for (int y = 0; y < 4; y++)
  {
    for (int x = 0; x < 3; x++)
    {
      tft.fillRoundRect(x * xMult + xOffset, y * xMult + yOffset, 20, 20, cornerRadiusPx, TFT_GREEN);
      char buf[128];
      sprintf(buf, "M%u", index);
      tft.drawString(buf, x * yMult + xOffset + 10, y * yMult + 10 + yOffset);

      index++;
    }
  }

  {
    const int numStates{7};
    const char *strings[] = {"JA", "IK", "JS", "RP", "SW", "OC", "BA"};
    const int xOffset = 5;
    const int yOffset = 28;
    const int xMult = 25;
    const int yMult = 25;
    int index = 0;
    for (int y = 0; y < 3; y++)
    {
      for (int x = 0; x < 3; x++)
      {
        tft.fillRoundRect(x * xMult + xOffset, y * xMult + yOffset, 20, 20, cornerRadiusPx, TFT_GREEN);
      

          tft.drawString(strings[index], x * yMult + xOffset + 10, y * yMult + 10 + yOffset);

   
          if (++index > numStates - 1)
          break;
      }
    }
  }

  {
    tft.fillRect(79, 0, 2, tft.height(), TFT_GREEN);
    tft.drawLine(0, 0, tft.width() - 1, 0, TFT_GREEN);
    tft.drawLine(tft.width() - 1, 0, tft.width() - 1, tft.height() - 1, TFT_GREEN);
    tft.drawLine(tft.width() - 1, tft.height() - 1, 0, tft.height() - 1, TFT_GREEN);
    tft.drawLine(0, tft.height() - 1, 0, 0, TFT_GREEN);
  }
}

void setup()
{
  pinMode(LED_BUILTIN, OUTPUT);

  InitDisplay();

  // HEALTH CHECKS:

  // Joint limit
  // IK breach
  // Gamepad
  // voltage
  // RPI
  // Motor response / current protection
}

void loop()
{
  HeartBeat();

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