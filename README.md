# Pu Robot Project

![Pu Robot](https://robotgyms.com/wp-content/uploads/2025/05/amazon-main-page-3.png)

## 🤖 Meet Pu - Your AI-Powered Learning Buddy!

Welcome to the Pu Robot project! This repository contains the MicroPython code and resources for programming and customizing your Pu robot. Pu is an intelligent, programmable robot designed for entertainment, education, and creative exploration.

### ✨ Key Features

- **Interactive Companion**: Walks, dances, and navigates with auto-pilot
- **AI Capabilities**: Chat, compose music, and learn new skills
- **Programmable**: Customize Pu's behavior with MicroPython
- **Expandable**: Add new features and capabilities through programming
- **Community-Driven**: Share and download custom programs and modifications

## 🛠 Project Structure

```
.
├── README.md           # Project documentation
├── requirements.txt    # Python dependencies
├── src/                # Source code
│   └── main.py         # Main application code
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
- Create a virtual environment by running:
  ```bash
  python flash_microbit.py --prepare
  ```

### Using the Flash Script

1. Make sure your Micro:bit is connected to your computer
2. activate the virtual environment by running:
  ```bash
  source .venv/bin/activate
  ``` 
3. Run the flash script:
   ```bash
   python flash_microbit.py
   ```

### Advanced Options

- Specify a custom serial port:
  ```bash
  python flash_microbit.py --port /dev/tty.usbmodem1234
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

#### Option 1: Install Latest uflash from Source
```bash
git clone https://github.com/ntoll/uflash.git
cd uflash
pip install -e .
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
