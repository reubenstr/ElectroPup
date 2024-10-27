#include "Arduino.h"
#include <vector>

enum class Sequence
{
    NONE = -1,
    MCU_STARTUP,
    RPI_ON,
    RPI_OFF,
    MOTORS_ON,
    MOTORS_OFF,
    LOW_BATTERY,
    ERROR,
    SHUTDOWN,
    NUM_SOUNDS
};

class Buzzer
{
public:
    Buzzer(int pin) : _buzzerPin(pin)
    {
        _frequencies = {
            {250, 300, 350, 400, 450, 500}, // MCU_STARTUP
            {250, 500, 0, 250, 500},                // RPI_ON
            {500, 250, 0, 500, 250},                // RPI_OFF
            {250, 275, 300, 325, 500},              // MOTORS_ON
            {500, 325, 300, 275, 250},              // MOTORS_OFF
            {500, 0, 500, 0, 500, 0, 500},          // LOW BATTERY
            {500, 250, 500, 250, 500, 250},         // ERROR
            {500, 200},                             // SHUTDOWN
        };

        _delays = {
            {200, 100, 50, 200, 100, 500}, // MCU_STARTUP
            {50, 100, 100, 50, 500},                // RPI_ON
            {50, 100, 100, 50, 500},                // RPI_OFF
            {100, 100, 100, 100, 200},              // MOTORS_ON
            {100, 100, 100, 100, 200},              // MOTORS_OFF
            {100, 50, 100, 50, 100, 50, 100},       // LOW BATTERY
            {125, 250, 125, 250, 125, 250},         // ERROR
            {100, 500},                             // SHUTDOWN
        };
    }

    void play(Sequence sequence)
    {
        if (isPlaying())
            return;

        Serial.printf("[BUZZER] playing sequence: %u\n", (int)sequence);

        _sequence = sequence;
        _start = millis();
        _index = 0;
        _delay = _delays[(int)_sequence][_index];

        pinMode(_buzzerPin, OUTPUT);
        analogWriteFrequency(_frequencies[(int)_sequence][_index]);
        analogWrite(_buzzerPin, _dutyCycle);
    }

    bool isPlaying()
    {
        return _sequence != Sequence::NONE;
    }

    void stop()
    {
        pinMode(_buzzerPin, INPUT);
    }

    void tick()
    {
        if (_sequence != Sequence::NONE)
        {
            if (millis() - _start > _delay)
            {
                _start = millis();

                Serial.println(_index);

                if (_index < _delays[(int)_sequence].size() - 1)
                {
                    _index++;
                    _delay = _delays[(int)_sequence][_index];
                    uint32_t frequency = _frequencies[(int)_sequence][_index];
                    if (frequency == 0)
                    {
                        analogWrite(_buzzerPin, 0);
                    }
                    else
                    {
                        analogWriteFrequency(frequency);
                        analogWrite(_buzzerPin, _dutyCycle);
                    }
                }
                else
                {
                    _sequence = Sequence::NONE;
                    stop();
                }
            }
        }
    }

private:
    int _buzzerPin;
    Sequence _sequence{Sequence::NONE};
    uint32_t _start;
    uint32_t _delay;
    uint32_t _index;

    // Acts as a pseudo volume; too high and the buzzer sounds corrupted (over driven).
    const uint8_t _dutyCycle{25};

    std::vector<std::vector<int>> _frequencies;
    std::vector<std::vector<int>> _delays;
};