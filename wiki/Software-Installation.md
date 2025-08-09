# Software Installation

## Prerequisites
- Python 3.9 or higher
- pip (Python package manager)
- Git (optional)
- Mu Editor (optional)

## Installation Steps

### 1. Clone the Repository
```bash
git clone https://github.com/NovaSeq/RobotPu.git
cd RobotPu
```

### 2. Create and Activate Virtual Environment
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
pip install -r flash_requirements.txt
```

### 4. Install MicroPython Firmware
1. Download the latest [MicroPython firmware](https://microbit.org/get-started/user-guide/firmware/)
2. Flash it to your micro:bit using the Mu Editor or `uflash`

### 5. Verify Installation
```bash
python flash_microbit.py --test
```

## Development Tools
- [Mu Editor](https://codewith.mu/) - Beginner-friendly Python editor
- [Thonny](https://thonny.org/) - Python IDE for beginners
- [VS Code](https://code.visualstudio.com/) with Python extension

## Troubleshooting
- If you get permission errors, try running commands with `sudo` (Linux/Mac)
- Make sure your user has permissions to access the USB device
- On Windows, you might need to install drivers for the micro:bit
