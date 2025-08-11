# TODO / Fixes

- Add version number to silkscreen
- Change terminal footprint to match the now used terminal: WM7877-ND 
- Add a switch for WiFi AP/Client switching
- LCD holes are not aligned and are off slightly
- Change 40 pin header from SMD to through-hold
- Consider adding a second tactile button

# General Thoughts

- Removing the Black Pill in favor of using a STM32 directly on the board will save space and allow the addition of more breakouts such as buttons.

- Removing the LCD PCB and directly connecting a LCD to the board will reduce the height of the board that will decrease the chance of screen damage when the quadruped rolls over.

