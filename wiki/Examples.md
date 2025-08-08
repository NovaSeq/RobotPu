# Example Programs

## 1. Line Follower
```python
from pu_robot import Robot
from microbit import sleep, display, Image

robot = Robot()
threshold = 50  # Adjust based on surface

while True:
    left_sensor = robot.get_left_line_sensor()
    right_sensor = robot.get_right_line_sensor()
    
    if left_sensor > threshold and right_sensor > threshold:
        robot.forward(30)
        display.show(Image.ARROW_N)
    elif left_sensor > threshold:
        robot.left(20)
        display.show(Image.ARROW_W)
    else:
        robot.right(20)
        display.show(Image.ARROW_E)
    
    sleep(50)
```

## 2. Obstacle Avoider
```python
from pu_robot import Robot
from microbit import sleep, display, Image

robot = Robot()
safe_distance = 15  # cm

while True:
    distance = robot.get_distance()
    
    if distance > safe_distance:
        robot.forward(40)
        display.show(Image.HAPPY)
    else:
        robot.backward(30)
        display.show(Image.SURPRISED)
        sleep(500)
        robot.left(30)
        sleep(300)
    
    sleep(100)
```

## 3. Clap-Controlled Robot
```python
from pu_robot import Robot
from microbit import display, Image, audio
import music

robot = Robot()
clap_threshold = 1000
is_moving = False

# Play startup sound
music.play(["C4:2", "E4:2", "G4:2", "C5:4"])
display.show(Image.YES)

while True:
    sound_level = audio.sound_level()
    
    if sound_level > clap_threshold:
        if is_moving:
            robot.stop()
            display.show(Image.NO)
            music.play(["C5:2", "G4:2", "E4:2", "C4:4"])
        else:
            robot.forward(50)
            display.show(Image.YES)
            music.play(["C4:2", "E4:2", "G4:2", "C5:4"])
        is_moving = not is_moving
        sleep(500)  # Debounce
    
    sleep(10)
```

## 4. Light Seeker
```python
from pu_robot import Robot
from microbit import display, Image, sleep

robot = Robot()
LIGHT_THRESHOLD = 50

while True:
    left_light = display.read_light_level()
    sleep(50)
    robot.spin_left(20)
    sleep(100)
    right_light = display.read_light_level()
    
    if left_light > LIGHT_THRESHOLD or right_light > LIGHT_THRESHOLD:
        if left_light > right_light:
            robot.spin_left(30)
            display.show(Image.ARROW_W)
        else:
            robot.spin_right(30)
            display.show(Image.ARROW_E)
        robot.forward(40)
    else:
        robot.stop()
        display.show(Image.ASLEEP)
    
    sleep(100)
```

## 5. Dance Routine
```python
from pu_robot import Robot
from microbit import display, Image, sleep
import music

robot = Robot()
dance_moves = [
    ("Spin Left", robot.spin_left, 50, 1000),
    ("Spin Right", robot.spin_right, 50, 1000),
    ("Forward", robot.forward, 50, 500),
    ("Backward", robot.backward, 50, 500),
    ("Wiggle", robot.left, 30, 200),
    ("Wiggle", robot.right, 30, 200),
]

# Play some music
tune = ["C4:4", "D4:4", "E4:4", "C4:4", "E4:4", "G4:4", "G4:4"]
music.play(tune)

# Dance!
for move_name, move_func, speed, duration in dance_moves:
    display.scroll(move_name)
    move_func(speed)
    sleep(duration)
    robot.stop()
    sleep(200)

# Take a bow
robot.stop()
display.show(Image.HAPPY)
music.play(["C5:4", "G4:4", "C4:4"])
```

## More Examples
Check the `examples/` directory for additional programs:
- `maze_solver.py` - Navigate through mazes using wall-following
- `voice_control.py` - Control Pu with voice commands
- `remote_control.py` - Control Pu using another micro:bit
- `light_painter.py` - Create light paintings with Pu's LEDs
- `mood_detector.py` - Change behavior based on sensor inputs
