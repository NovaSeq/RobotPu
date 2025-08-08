# Your First Program

## Hello, Pu!
Let's create a simple program to make Pu display a happy face and say hello.

```python
from microbit import *

# Display a happy face
display.show(Image.HAPPY)

# Say hello
import speech
speech.say("Hello, I am Pu!")
```

## Uploading Your Program
1. Save the code as `main.py`
2. Connect Pu to your computer
3. Run the flash script:
   ```bash
   python flash_microbit.py
   ```

## Understanding the Code
- `from microbit import *` - Imports all micro:bit functions
- `display.show()` - Controls the LED display
- `speech.say()` - Makes Pu speak

## Next Steps
- Try changing the image to `Image.SAD` or `Image.HEART`
- Make Pu say different phrases
- Add button interactions

## Example: Button-Controlled Movement
```python
from pu_robot import Robot
from microbit import *

robot = Robot()

while True:
    if button_a.is_pressed():
        robot.walk(3, 0)  # Move forward when button A is pressed
    elif button_b.is_pressed():
        robot.walk(-3, 0.5)  # Spin backward right when button B is pressed
    else:
        robot.stop()  # Stop when no buttons are pressed
    
    sleep(10)  # Small delay to prevent excessive CPU usage
```
