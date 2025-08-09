# Pu Robot Project

![Pu Robot](https://robotgyms.com/wp-content/uploads/2023/10/Pu-1-1024x1024.jpg)

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

1. Install required dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Flash your micro:bit with the latest MicroPython firmware

3. Deploy your code using the flash script or your preferred method

## Flashing Code to Micro:bit

This project includes a flash script to simplify the process of uploading code to your Micro:bit. The script will:

- Set up a Python virtual environment
- Install required dependencies
- Minify your Python code to reduce file size
- Flash the code to your connected Micro:bit
- Flash the pu.txt (configuration file) to your connected Micro:bit

### Prerequisites

- Python 3.6 or higher
- A connected Micro:bit using USB cable
- On macOS/Linux: Ensure you have read/write permissions for the Micro:bit

### Using the Flash Script

1. Make sure your Micro:bit is connected to your computer
2. Run the flash script:
   ```bash
   python flash_microbit.py
   ```

### Advanced Options

- Specify a custom serial port:
  ```bash
  python flash_microbit.py --port PORT_STRING
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

## Development

- `main.py`: Contains the main application logic
- Add your custom modules in the `src/` directory
- Place external libraries in `lib/`
