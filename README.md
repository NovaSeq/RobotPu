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
- Minify your Python code
- Generate a hex file
- Flash the code to your connected Micro:bit

### Prerequisites

- Python 3.6 or higher
- A connected Micro:bit in bootloader mode
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
  python flash_microbit.py --port /dev/tty.usbmodem1234
  ```
## Development

- `main.py`: Contains the main application logic
- Add your custom modules in the `src/` directory
- Place external libraries in `lib/`
