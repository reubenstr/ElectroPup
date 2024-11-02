/*
    NeoPixels controls ElectroPup's NeoPixel strips.

    There are two strips and the colors duplicated between strips.

    TODO:
        If complexity grows, consider creating a master pixel array that
        is copied into neopixels strips contained in an array to simplify the code.
*/


#include <Arduino.h>
#include "Adafruit_NeoPixel.h"

enum class PixelMode
{
    OFF,
    RAINBOW,
    RIDER,
    SPARKLE,
    ERROR
};

enum class PixelColor
{
    RED,
    GREEN,
    BLUE,
    YELLOW,
    MAGENTA,
    CYAN,
    RANDOM
};

class Neopixels
{

public:
    Neopixels(uint8_t pin_0, uint8_t pin_1)
    {
        _neo0 = new Adafruit_NeoPixel(_numNeopixelsPerStrip, pin_0, NEO_GRB + NEO_KHZ800);
        _neo1 = new Adafruit_NeoPixel(_numNeopixelsPerStrip, pin_1, NEO_GRB + NEO_KHZ800);
    }

    void init()
    {
        _neo0->begin();
        _neo0->show();
        _neo0->setBrightness(_neopixelBrightness);
    }

    void setMode(PixelMode pixelMode, PixelColor pixelColor)
    {
        _pixelMode = pixelMode;
        _pixelColor = pixelColor;
    }

    void setMode(PixelMode pixelMode)
    {
        _pixelMode = pixelMode;
    }

    void setPixelColor(PixelColor pixelColor)
    {
        _pixelColor = pixelColor;
    }

    void tick()
    {
        static PixelMode previousMode;

        if (previousMode != _pixelMode)
        {
            previousMode = _pixelMode;
            off();
        }

        if (_pixelMode == PixelMode::OFF)
        {
            off();
        }
        else if (_pixelMode == PixelMode::RAINBOW)
        {
            rainbow();
        }
        else if (_pixelMode == PixelMode::RIDER)
        {
            rider();
        }
        else if (_pixelMode == PixelMode::SPARKLE)
        {
            sparkle();
        }
        else if (_pixelMode == PixelMode::ERROR)
        {
            error();
        }
    }

private:
    void off()
    {
        for (uint16_t i = 0; i < _numNeopixelsPerStrip; i++)
        {
            _neo0->setPixelColor(i, 0);
            _neo1->setPixelColor(i, 0);
        }

        _neo0->show();
        _neo1->show();
    }

    void rainbow()
    {
        static uint8_t wheelIndex{0};
        static uint32_t start{0};
        const uint8_t space{10};
        static uint32_t incrementRateMs{20};

        if (millis() - start > incrementRateMs)
        {
            start = millis();
            wheelIndex++;
        }

        for (uint16_t i = 0; i < _numNeopixelsPerStrip; i++)
        {
            _neo0->setPixelColor(i, _wheel(wheelIndex + space * i));
            _neo1->setPixelColor(i, _wheel(wheelIndex + space * i));
        }

        _neo0->show();
        _neo1->show();
    }

    void rider()
    {
        static uint32_t startIncrement{0};
        static uint32_t startFade{0};
        static uint8_t index{0};
        static int direction{1};
        static uint32_t fadeRateMs{15};
        static uint32_t incrementRateMs{250};

        if (millis() - startIncrement > incrementRateMs)
        {
            startIncrement = millis();

            index += direction;

            if (index == 0)
            {
                direction = 1;
            }
            else if (index == _numNeopixelsPerStrip - 1)
            {
                direction = -1;
            }          
            _neo0->setPixelColor(index, _getColor());
            _neo1->setPixelColor(index, _getColor());
            _neo0->show();
            _neo1->show();
        }

        if (millis() - startFade > fadeRateMs)
        {
            startFade = millis();
            _fade(_neo0);
            _fade(_neo1);
            _neo0->show();
            _neo1->show();
        }
    }

    void sparkle()
    {
        static uint32_t startUpdate{0};
        static uint32_t startFade{0};
        static uint32_t updateRateMs{250};
        static uint32_t fadeRateMs{15};

        if (millis() - startUpdate > updateRateMs)
        {
            startUpdate = millis();

            uint8_t index;
            do
            {
                index = random(0, _numNeopixelsPerStrip);
            } while (_neo0->getPixelColor(index) > 0);

                _neo0->setPixelColor(index, _getColor());
            _neo1->setPixelColor(index, _getColor());
            _neo0->show();
            _neo1->show();
        }

        if (millis() - startFade > fadeRateMs)
        {
            startFade = millis();
            _fade(_neo0);
            _fade(_neo1);
            _neo0->show();
            _neo1->show();
        }
    }

    void error()
    {
        static uint32_t start{0};
        static uint32_t startFade{0};
        static uint32_t rateMs{1500};
        static uint32_t fadeRateMs{12};

        if (millis() - start > rateMs)
        {
            start = millis();
            for (uint16_t i = 0; i < _numNeopixelsPerStrip; i++)
            {             
                _neo0->setPixelColor(i, _getColor());
                _neo1->setPixelColor(i, _getColor());
            }
            _neo0->show();
            _neo1->show();
        }

        if (millis() - startFade > fadeRateMs)
        {
            startFade = millis();
            _fade(_neo0);
            _fade(_neo1);
            _neo0->show();
            _neo1->show();
        }
    }

    void _fade(Adafruit_NeoPixel *neo)
    {
        for (int i = 0; i < neo->numPixels(); i++)
        {
            uint32_t color = neo->getPixelColor(i);
            uint8_t r = (color >> 16) & 0xFF; // Extract red
            uint8_t g = (color >> 8) & 0xFF;  // Extract green
            uint8_t b = color & 0xFF;         // Extract blue

            if (r > 0)
                r--;
            if (g > 0)
                g--;
            if (b > 0)
                b--;

            neo->setPixelColor(i, _color(r, g, b));
        }
    }

    uint32_t _getColor()
    {
        if (_pixelColor == PixelColor::RANDOM)
        {
            int randomIndex = random(0, 3);
            return _colors[randomIndex];
        }
        else
        {
            _colors[(uint8_t)_pixelColor];
        }
    }

    static uint32_t _color(uint8_t r, uint8_t g, uint8_t b)
    {
        return ((uint32_t)r << 16) | ((uint32_t)g << 8) | b;
    }

    uint32_t _wheel(byte WheelPos)
    {
        WheelPos = 255 - WheelPos;
        if (WheelPos < 85)
        {
            return _color(255 - WheelPos * 3, 0, WheelPos * 3);
        }
        else if (WheelPos < 170)
        {
            WheelPos -= 85;
            return _color(0, WheelPos * 3, 255 - WheelPos * 3);
        }
        else
        {
            WheelPos -= 170;
            return _color(WheelPos * 3, 255 - WheelPos * 3, 0);
        }
    }

    Adafruit_NeoPixel *_neo0;
    Adafruit_NeoPixel *_neo1;

    PixelMode _pixelMode{PixelMode::OFF};
    PixelColor _pixelColor{PixelColor::RED};

    const uint8_t _numNeopixelsPerStrip{9};
    const uint8_t _neopixelBrightness{50};

    uint32_t _colors[6] = {
        _color(255, 0, 0),   // Red
        _color(0, 255, 0),   // Green
        _color(0, 0, 255),   // Blue
        _color(255, 255, 0), // Yellow
        _color(0, 255, 255), // Cyan
        _color(255, 0, 255)  // Magenta
    };
};