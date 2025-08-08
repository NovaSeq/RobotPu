#!/usr/bin/env python3
"""
Micro:bit Flashing Script

This script automates the process of:
1. Setting up a Python virtual environment
2. Installing required dependencies
3. Minifying Python code
4. Generating a hex file
5. Flashing to a connected micro:bit

Usage:
    python flash_microbit.py [--port PORT] [--list] [--no-flash]
"""

import os
import sys
import subprocess
import shutil
import argparse
import time
from pathlib import Path
try:
    import microfs  # For micro:bit file system operations
except ImportError:
    print("Warning: microfs module not found. Install with: pip install microfs")
    microfs = None
import uflash

# Configuration
VENV_DIR = ".venv"
REQUIREMENTS = "requirements.txt"
SOURCE_DIR = "src"
BUILD_DIR = "build"
OUTPUT_HEX = "pu_robot_hex"
MICROBIT_VOLUME = "/Volumes/MICROBIT"  # Default for macOS, adjust for other OS

def run_command(cmd):
    """Run a shell command and return its output."""
    print(f"Running: {cmd}")
    try:
        # Use shell=True to handle paths with spaces properly
        result = subprocess.run(
            cmd,
            shell=True,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if result.stdout:
            print(f"Output: {result.stdout.strip()}")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {e.cmd}")
        if e.stdout:
            print(f"stdout: {e.stdout}")
        if e.stderr:
            print(f"stderr: {e.stderr}")
        # Don't exit, just return None to allow the script to continue
        return None

def setup_venv():
    """Set up a Python virtual environment."""
    if not os.path.exists(VENV_DIR):
        print("Creating virtual environment...")
        run_command(f"python -m venv {VENV_DIR}")
    
    # Activate venv and install requirements
    if sys.platform == "win32":
        pip = os.path.join(VENV_DIR, "Scripts", "pip")
        python = os.path.join(VENV_DIR, "Scripts", "python")
    else:
        pip = os.path.join(VENV_DIR, "bin", "pip")
        python = os.path.join(VENV_DIR, "bin", "python")
    
    print("Installing requirements...")
    run_command(f"{pip} install --upgrade pip")
    run_command(f"{pip} install -r {REQUIREMENTS}")
    run_command(f"{pip} install pyminify")
    
    return python

def minify_code():
    """Minify Python code using pyminify."""
    print("Minifying Python code...")
    
    # Create build directory if it doesn't exist
    if os.path.exists(BUILD_DIR):
        shutil.rmtree(BUILD_DIR)
    os.makedirs(BUILD_DIR, exist_ok=True)
    
    # Minify each Python file
    for root, _, files in os.walk(SOURCE_DIR):
        for file in files:
            if file.endswith('.py'):
                src_path = os.path.join(root, file)
                rel_path = os.path.relpath(src_path, SOURCE_DIR)
                dest_path = os.path.join(BUILD_DIR, rel_path)
                
                # Create subdirectories if they don't exist
                os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                
                # Minify the file
                run_command(f"python -m python_minifier {src_path} -o {dest_path} --remove-literal-statements ")
    
    return BUILD_DIR


def merge_python_files(work_dir, src_dir):
    """Merge all Python files from src directory into a single file."""
    print("Merging Python files...")
    
    # Create build directory if it doesn't exist
    os.makedirs(work_dir, exist_ok=True)
    
    # Path to the merged output file
    merged_file = os.path.join(work_dir, 'merged_main.py')
    
    # Get all Python files from src directory
    src_files = [os.path.join(src_dir, f) for f in os.listdir(src_dir) 
                if f.endswith('.py') and os.path.isfile(os.path.join(src_dir, f))]
    
    if not src_files:
        print(f"Error: No Python files found in {src_dir}")
        sys.exit(1)
    
    # Sort files to ensure consistent ordering (main.py first if it exists)
    src_files.sort(key=lambda x: x.endswith('main.py'))
    
    # Merge all Python files
    with open(merged_file, 'w') as outfile:
        for fname in src_files:
            with open(fname) as infile:
                # Skip shebang lines and encoding declarations
                content = infile.read()
                lines = content.splitlines(True)
                
                # Skip shebang and encoding lines
                for line in lines:
                    if line.startswith('#!') or ('coding=' in line and 'python' in line.lower()):
                        continue
                    outfile.write(line)
                
                # Add newline between files for better readability
                outfile.write('\n')
    
    return merged_file

def generate_hex(python_exec):
    """Generate a hex file from the main Python file."""
    print("Generating hex file...")

    # Merge all Python files into one
    main_py = merge_python_files("temp", BUILD_DIR)
    
    if not os.path.exists(main_py):
        print(f"Error: {main_py} not found")
        sys.exit(1)

    os.makedirs(OUTPUT_HEX, exist_ok=True)

    # Only pass the main.py file to uflash - it will handle imports
    cmd = f"{python_exec} -m uflash {main_py} {OUTPUT_HEX}"
    
    # Run the command
    run_command(cmd)
    
    print(f"Hex file generated: {os.path.abspath(OUTPUT_HEX)}")
    return os.path.join(OUTPUT_HEX, "micropython.hex")
    
def copy_to_microbit(src_path, dest_name, max_retries=3):
    """Helper function to copy a file to micro:bit with retry logic."""
    for attempt in range(max_retries):
        try:
            print(f"  - Attempt {attempt + 1}/{max_retries} for {os.path.basename(src_path)}...")
            microfs.put(src_path, dest_name)
            print(f"  - Successfully copied to {dest_name}")
            
            # Verify the file was copied
            time.sleep(2)  # Give micro:bit a moment to update its filesystem
            file_list = microfs.ls()
            if dest_name in file_list:
                print(f"  - Verified {dest_name} on micro:bit")
                return True
            else:
                print(f"  - Warning: {dest_name} not found on micro:bit")
                
        except Exception as e:
            print(f"  - Error (attempt {attempt + 1}): {str(e)}")
            if attempt < max_retries - 1:  # Don't sleep on the last attempt
                print(f"  - Retrying in 10 seconds...")
                time.sleep(10)
    
    print(f"  - Failed to copy {dest_name} after {max_retries} attempts")
    return False

def flash_microbit(port=None):
    """Flash the hex file to a connected micro:bit and copy Python files to the file system.
    Args:
        port: Serial port of the micro:bit (e.g., '/dev/tty.usbmodem...' on macOS/Linux, 'COM3' on Windows)
    """
    if microfs is None:
        print("Error: microfs module is required for file operations")
        return False
        
    print(f"Looking for micro:bit on port: {port or 'auto'}")
    
    try:
        # flash main.py to the connected micro:bit
        print("Flashing main.py to micro:bit...")
        main_py_path = os.path.join(BUILD_DIR, 'main.py')
        if port:
            uflash.flash(paths_to_microbits=[port], path_to_python=main_py_path)
        else:
            uflash.flash(path_to_python=main_py_path)
            
        print("Waiting for micro:bit to initialize...")
        time.sleep(6)  # Wait for micro:bit to initialize
        
        # 2. Get list of files to copy
        files_to_copy = []
        if os.path.exists(BUILD_DIR):
            # Get all Python files except main.py
            files_to_copy = [f for f in os.listdir(BUILD_DIR) 
                           if f.endswith('.py') and f != 'main.py' 
                           and os.path.isfile(os.path.join(BUILD_DIR, f))]
        
        # Add pu.txt to the list
        pu_txt_src = os.path.abspath(os.path.join(SOURCE_DIR, 'pu.txt'))
        if os.path.exists(pu_txt_src):
            files_to_copy.append(('pu.txt', pu_txt_src))
        
        if not files_to_copy:
            print("No additional files found to copy")
            return True
            
        # 3. Copy files one by one with microfs
        print(f"Copying {len(files_to_copy)} files to micro:bit file system...")
        for file_info in files_to_copy:
            if isinstance(file_info, tuple):
                dest_name, src_path = file_info
            else:
                src_path = os.path.abspath(os.path.join(BUILD_DIR, file_info))
                dest_name = os.path.basename(file_info)
                
            print(f"\n--- Copying {os.path.basename(src_path)} ---")
            success = copy_to_microbit(src_path, dest_name)
            if not success:
                print(f"  - Warning: Failed to copy {os.path.basename(src_path)}")
            
            time.sleep(2)  # Small delay between files
        
        print("\nFile copy process completed")
        return True
        
    except Exception as e:
        print(f"Error during micro:bit operation: {e}")
        return False

def list_microbits():
    """List all connected micro:bits with their serial ports."""
    try:
        print("\nLooking for connected micro:bits...")
        devices = microfs.get_serial_ports()
        if not devices:
            print("No micro:bits found. Please ensure your micro:bit is connected and in flash mode.")
            return False
            
        print("\nConnected micro:bits:")
        for i, device in enumerate(devices, 1):
            print(f"  {i}. {device}")
            
        return True
    except Exception as e:
        print(f"Error listing micro:bits: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Flash micro:bit with Python code')
    parser.add_argument('--port', help='Serial port for micro:bit (e.g., /dev/tty.usbmodem... or COM3)')
    parser.add_argument('--list', action='store_true', help='List connected micro:bits and exit')
    parser.add_argument('--no-flash', action='store_true', help='Generate hex without flashing')
    args = parser.parse_args()
    
    print("=== Micro:bit Flasher ===")
    
    if args.list:
        list_microbits()
        return
    
    # Setup virtual environment and install dependencies
    python_exec = setup_venv()
    
    # Minify code
    build_dir = minify_code()

    # Flash to micro:bit if requested
    flash_microbit(args.port)
    
    print("=== Done ===")

if __name__ == "__main__":
    main()
