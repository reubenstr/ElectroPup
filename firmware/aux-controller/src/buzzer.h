#include "Arduino.h"
#include <vector>

enum class Sequence
{
    NONE = -1,
    MCU_STARTUP,
    RPI_READY,
    MOTORS_ON,
    MOTORS_OFF,
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
            {262, 330, 392},                // MCU_STARTUP
            {500, 0, 500},                  // RPI_READY
            {250, 275, 300, 325, 500},      // MOTORS_ON
            {500, 325, 300, 275, 250},      // MOTORS_OFF
            {500, 250, 500, 250, 500, 250}, // ERROR
            {250, 275, 300, 325, 500},      // SHUTDOWN
        };

        _delays = {
            {250, 250, 250},                // MCU_STARTUP
            {100, 50, 100},                 // RPI_READY
            {100, 100, 100, 100, 200},      // MOTORS_ON
            {100, 100, 100, 100, 200},      // MOTORS_OFF
            {125, 250, 125, 250, 125, 250}, // ERROR
            {100, 100, 100, 100, 200},      // SHUTDOWN
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