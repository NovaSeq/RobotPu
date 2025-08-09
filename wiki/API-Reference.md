# API Reference

## Movement
```python
from pu_robot import Robot

robot = Robot()

# Basic movement
robot.walk(3, -0.5)
robot.side_step(0.5)
robot.jump()
robot.kick()
robot.dance()
robot.fall()
robot.fetal()   
robot.explore() 
robot.joystick() 
robot.sleep()
robot.stand()
robot.talk("Hello")
robot.sing("C4:4")
robot.calibrate()   
robot.set_group(166)
robot.display()

```

## Sensors
```python
# Distance sensor
distance = robot.get_distance()  # in cm

# Line sensors
left_line = robot.get_left_line_sensor()   # 0-1023
right_line = robot.get_right_line_sensor() # 0-1023

# Buttons
from microbit import button_a, button_b

if button_a.is_pressed():
    # Button A is pressed
    pass

if button_b.was_pressed():
    # Button B was pressed since last check
    pass
```

## Display
```python
from microbit import display, Image

# Show text
display.scroll("Hello!")

# Show images
display.show(Image.HAPPY)

# Individual LEDs
display.set_pixel(x, y, brightness)  # x,y: 0-4, brightness: 0-9

# Clear display
display.clear()
```

## Sound
```python
import music

# Play a note
music.play(['C4:4'])  # Note C4 for 4 ticks

# Play a melody
tune = ["C4:4", "D4:4", "E4:4", "C4:4"]
music.play(tune)

# Stop all sound
music.stop()

# Play built-in sounds
import audio
audio.play(audio.GIGGLE)  # Other options: HAPPY, HELLO, etc.
```

## Timing and Delays
```python
from microbit import sleep

# Delay in milliseconds
sleep(1000)  # 1 second delay

# Get running time in milliseconds
from microbit import running_time
start = running_time()
# Do something
elapsed = running_time() - start
```

## Advanced Features
```python
# Bluetooth communication
import radio
radio.on()
radio.send('hello')
message = radio.receive()

# Accelerometer
from microbit import accelerometer
x = accelerometer.get_x()
y = accelerometer.get_y()
z = accelerometer.get_z()

# Compass
from microbit import compass
compass.calibrate()
heading = compass.heading()  # 0-359 degrees
```
