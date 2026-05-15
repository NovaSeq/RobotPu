# Robot PU Project

![Pu Robot](https://robotgyms.com/wp-content/uploads/2025/05/amazon-main-page-3.png)

## 🤖 Meet Pu - Your AI-Powered Learning Buddy!

Welcome to the Pu Robot project! This repository contains the MicroPython code and resources for programming and customizing your Pu robot. Pu is an intelligent, programmable robot designed for entertainment, education, and creative exploration.

### ✨ Key Features

- **Interactive Companion**: Walks, dances, and navigates with auto-pilot
- **AI Capabilities**: Chat, compose music, and learn new skills
- **Programmable**: Customize Pu's behavior with MicroPython
- **Expandable**: Add new features and capabilities through programming and 3D printing
- **Community-Driven**: Share and download custom programs and modifications

Learn more about The Story of PU, which shows robot PU's activities, hardware, software, tutorials, and upgrade projects at:

- **Website**: [robotgyms.com/pu](https://robotgyms.com/pu)
- **YouTube**: [The Story of PU](https://www.youtube.com/@TheStoryofPu-yw8tr)
- **TikTok**: [@thestoryofpu](https://www.tiktok.com/@thestoryofpu)

Purchase links:

- **Amazon**: [Robot PU kit](https://www.amazon.com/Robot-Programmable-Interactive-Upgradable-Self-Balancing/dp/B0DR8RGVXN)

## Features

- **Expressive personality**: dance routines, reactions, auto-pilot, soccer
- **Classroom-ready** with block coding, javascript and Python paths
- **Maker-friendly** with free tutorials and projects of hardware and software to upgrade robot PU
- **Open-source** with community resources

## What’s in the Kit

- Robot PU (pre-built and upgradable)
- 2 × micro:bit compatible board
- Gamepad (remote control and distributed computation)
- [Manual](https://robotgyms.com/courses/the-story-of-pu-book-1-pair-up/)
- [Tutorials](https://github.com/robotgyms/pxt-robotpu/tree/main/tutorials/JavaScripts/README.md)
- [Games](https://robotgyms.com/courses/the-story-of-pu-book-2-games/)
- [Classes](https://robotgyms.com/courses/the-story-of-pu-book-3-growth)
- [Upgrade Projects](https://robotgyms.com/courses/the-story-of-pu-book-4-journey/)

The retail kit includes a **gamepad that uses the second micro:bit**. For the best experience (and to ensure the radio control protocol matches robotPu’s `runKeyValueCommand` / `runStringCommand`), flash the official Robot PU gamepad program to the gamepad micro:bit:

- https://makecode.microbit.org/_JbygU12aCAsU

## The Story Of Robot PU
- [The Saga of Saduka](https://robotgyms.com/courses/the-saga-of-robot-pu)

## JavaScript/Block Codes
- [MakeCode Extensions on GitHub](https://github.com/robotgyms/pxt-robotpu.git)

## Radio Command to Function Mapping in `PuBot.py`

Robot PU can be programmed at the radio command level by sending micro:bit radio packets from the gamepad or another micro:bit. The robot receives packets in `PuBot.process_radio_cmd()` and dispatches them in two ways:

- **Key/value packets**: Parsed by `MakeRadio.receive_packet()` as `(command_name, value)` tuples, then dispatched through `self.cmd_dict`.
- **String packets**: Parsed as strings and handled directly by prefix checks such as `#put`, `#pus`, `#puhi`, and `#pun`.

### Key/value command mapping

The main command table is defined in `PuBot.__init__()` as `self.cmd_dict`:

| Radio command | Function called | Value type | Purpose                                                                                                     |
| --- | --- | --- |-------------------------------------------------------------------------------------------------------------|
| `#puspeed` | `self.speed(v)` | float | Controls walking speed. Positive values move forward, negative values move backward, near-zero values stop. |
| `#puturn` | `self.turn(v)` | float | Controls turning direction.                                                                                 |
| `#puroll` | `self.roll(v)` | float | Adjusts left/right body bias.                                                                               |
| `#pupitch` | `self.pitch(v)` | float | Adjusts forward/back body bias.                                                                             |
| `#puB` | `self.button(v)` | int | Triggers button-style robot actions such as rest, explore, jump, dance, or kick.                            |
| `#pulogo` | `self.logo(v)` | int/float | Runs the logo-button action and reports the robot state by speech.                                          |
| `#purs` | `self.pose(v)` | int | Selects a rest pose and returns the robot to idle/rest state.                                               |
| `#puai` | `self.ai(v)` | int | Selects AI mode level. `0` means off.                                                                       |
| `#pule` | `wk.left_eye_bright(v)` | int/float | Sets left eye brightness, [0-1023).                                                                         |
| `#pure` | `wk.right_eye_bright(v)` | int/float | Sets right eye brightness, [0-1023).                                                                        |

To send one of these commands from another micro:bit using the same helper class, use:

```python
ro.send_value("#puspeed", 0.8)
ro.send_value("#puturn", -0.4)
ro.send_value("#puB", 3)
```

`MakeRadio.send_value(name, value)` encodes integers as packet type `1` and floats as packet type `5`. `PuBot.py` receives both forms as `(name, value)` and calls `self.cmd_dict.get(name, self.noop)(value)`. If the command name is unknown, `self.noop(value)` runs and nothing changes.

### String commands

String packets are sent with `MakeRadio.send_str()` and are handled by `process_radio_cmd()`:

| String prefix | Example | Robot behavior |
| --- | --- | --- |
| `#put` | `#putHello` | Speaks the text after `#put`. |
| `#pus` | `#pus...` | Buffers song text after `#pus`; after 6 segments, Pu sings the combined song. |
| `#puhi` | `#puhiPu` | Says that the named friend is here. |
| `#pun` | `#punNova` | Updates the robot serial/name field and introduces itself. |

Examples:

```python
ro.send_str("#putHello, I am Pu")
ro.send_str("#puhiNova")
ro.send_str("#punPuBot1")
```

### Adding a new radio-level command

To add a new key/value command:

1. Add a method to `PuBot`, for example `def wave(self, v):`.
2. Add the command name to `self.cmd_dict` in `PuBot.__init__()`, for example `"#puwave": self.wave`.
3. Send it from the controller with `ro.send_value("#puwave", value)`.

To add a new string command:

1. Add a new `elif d.startswith("#pu..."):` branch inside `process_radio_cmd()`.
2. Parse the payload from the string using slicing, following the existing examples.
3. Send it from the controller with `ro.send_str("#pu...payload")`.

Keep command names short because `MakeRadio.send_value()` truncates key/value command names longer than 8 characters.

## 🛠 Project Structure

```
.
├── README.md           # Project documentation
├── requirements.txt    # Python dependencies
├── src/                # Source code
│   └── main.py         # Main application code
├── 3dModels            # 3D models for 3D printing to upgrade PU
├── gamepad             # Make code hex for gamepad programs
├── lib/                # External libraries
├── tests/              # Test files
└── utils/              # Utility scripts
```

## Getting Started

1. Install python3.10 above to your computer

2. Flash your micro:bit with the latest MicroPython firmware (optional)

3. Deploy your code using the flash script or your preferred method

## Flashing Code to Micro:bit

This project includes a flash script to simplify the process of uploading code to your Micro:bit. The script will:

- Set up a Python virtual environment
- Install required dependencies
- Minify your Python code to reduce file size
- Flash the code to your connected Micro:bit
- Flash the pu.txt (configuration file) to your connected Micro:bit

### Prerequisites

- Python 3.10 or higher
- A connected Micro:bit using USB cable
- On macOS/Linux: Ensure you have read/write permissions for the Micro:bit
- Create a virtual environment by running: (optional)
  ```bash
  python3 flash_microbit.py --prepare
  ```

### Using the Flash Script

1. Make sure your Micro:bit is connected to your computer
2. Run the flash script:
   ```bash
   python3 flash_microbit.py
   ```

### Advanced Options

- Specify a custom serial port:
  ```bash
  python3 flash_microbit.py --port /dev/tty.usbmodem1234
  ```

#### Finding the Correct Port:

**Windows:**
1. Open Device Manager (Win + X, then select "Device Manager")
2. Expand "Ports (COM & LPT)"
3. Look for "mbed Serial Port" or "USB Serial Device"
4. The port will be something like `COM3` or `COM4`

**macOS:**
1. Open Terminal
2. Run: `ls /dev/tty.*`
3. Look for a device like `/dev/tty.usbmodem1234` or `/dev/tty.usbmodem1412`
4. The Micro:bit usually has "usbmodem" in its name

**Linux:**
1. Open Terminal
2. Run: `ls /dev/tty*` before and after connecting the Micro:bit
3. The new device that appears is your Micro:bit
4. Common names: `/dev/ttyACM0` or `/dev/ttyUSB0`

> **Note:** On Linux, you might need to add your user to the `dialout` group:
> ```bash
> sudo usermod -a -G dialout $USER
> # Then log out and log back in for changes to take effect
> ```

### Warning

**Important Stability Notice for uflash 2.0.0**

The current stable version of uflash (2.0.0) uses MicroPython firmware 2.0.0.beta which may cause random freezes during operation. For stable builds, please use one of the following methods:

#### Option 1: Install Latest uflash from github Source that has fixed the issue
```bash
git clone https://github.com/ntoll/uflash.git
cd uflash
. RobotPu/.venv/bin/activate    # activate the virtual environment that is in RobotPu directory
pip uninstall uflash -y # uninstall the old uflash
python setup.py install # install the new uflash from uflash directory
```
Then use the flash script as normal.

#### Option 2: Use MU Editor
1. **Initial Flash**
   - Install [MU Editor](https://codewith.mu/) version 1.2.0 or later
   - Open your minified `main.py` (under the build directory) in MU Editor
   - Click the "Flash" button to flash the main script to your micro:bit

2. **Copy Additional Files**
   - After flashing, use MU Editor's file browser (Files button)
   - Manually copy all other minified Python files (under the build directory) to the micro:bit
   - Manually copy the `pu.txt` (under the src directory) to the micro:bit
   - Ensure files are transferred completely before disconnecting

3. **Verification**
   - The micro:bit should restart automatically
   - Check the serial console in MU Editor for any error messages

**Note:** These workarounds are temporary until uflash includes a stable release of the MicroPython firmware.

## Development

- `main.py`: Contains the main application logic
- Add your custom modules in the `src/` directory
- Place external libraries in `lib/`
