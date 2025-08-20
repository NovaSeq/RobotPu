#!/usr/bin/env python3
"""
Micro:bit Flashing Script

This script automates the process of:
1. Setting up a Python virtual environment
2. Installing required dependencies
3. Minifying Python code
5. Flashing main.py to a connected micro:bit
6. Copying Python files to the micro:bit file system    

Usage:
    python flash_microbit.py [--port PORT] [--list] [--no-flash]
"""

import os
import sys
import subprocess
import shutil
import argparse
import time

# Configuration
VENV_DIR = ".venv"
REQUIREMENTS = "requirements.txt"
SOURCE_DIR = "src"
BUILD_DIR = "build"
OUTPUT_HEX = "output"
MICROBIT_VOLUME = "/Volumes/MICROBIT"  # Default for macOS, adjust for other OS

def run_command(cmd, check=True):
    """Run a shell command and return its output."""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            check=check,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if result.stdout:
            print(f"Output: {result.stdout.strip()}")
        if result.stderr and result.returncode != 0:
            print(f"Error: {result.stderr.strip()}")
        return result
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {e.cmd}")
        if e.stdout:
            print(f"stdout: {e.stdout}")
        if e.stderr:
            print(f"stderr: {e.stderr}")
        # Don't exit, just return None to allow the script to continue
        return None

def setup_venv():
    """Set up a Python virtual environment and install requirements.
    
    Returns:
        str: Path to the Python interpreter in the virtual environment
    """
    # Get the virtual environment paths
    if sys.platform == "win32":
        python = os.path.join(VENV_DIR, "Scripts", "python.exe")
        pip = os.path.join(VENV_DIR, "Scripts", "pip.exe")
    else:
        python = os.path.join(VENV_DIR, "bin", "python")
        pip = os.path.join(VENV_DIR, "bin", "pip")
    
    # Create virtual environment if it doesn't exist
    if not os.path.exists(VENV_DIR):
        print("Creating virtual environment...")
        run_command(f"{sys.executable} -m venv {VENV_DIR}")
    
    # Install/upgrade packages in the virtual environment
    print("Installing requirements...")
    run_command(f"{pip} install --upgrade pip")
    run_command(f"{pip} install -r {REQUIREMENTS}")
    run_command(f"{pip} install pyminify uflash microfs")
    
    # Verify Python interpreter exists
    if not os.path.exists(python):
        raise RuntimeError(f"Python interpreter not found at {python}")
    
    return python

def minify_code(python_exec):
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
                run_command(f"{python_exec} -m python_minifier {src_path} -o {dest_path} --remove-literal-statements ")
    
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
    """Generate a hex file from the main Python file using a specific MicroPython runtime.
    
    Uses the 0257_nrf52820_microbit_if_crc_c782a5ba90_gcc.hex firmware from the hex folder.
    """
    print("Generating hex file...")

    # Merge all Python files into one
    main_py = merge_python_files("temp", BUILD_DIR)
    
    if not os.path.exists(main_py):
        print(f"Error: {main_py} not found")
        sys.exit(1)

    # Path to the custom runtime firmware
    runtime_hex = os.path.join("hex", "0257_nrf52820_microbit_if_crc_c782a5ba90_gcc.hex")
    
    if not os.path.exists(runtime_hex):
        print(f"Error: Runtime firmware not found at {runtime_hex}")
        sys.exit(1)

    os.makedirs(OUTPUT_HEX, exist_ok=True)
    output_hex = os.path.join(OUTPUT_HEX, "micropython.hex")

    # Use uflash with the specified runtime
    cmd = f"{python_exec} -m uflash --runtime {runtime_hex} {main_py} -o {output_hex}"
    
    # Run the command
    result = run_command(cmd)
    
    if result and result.returncode == 0:
        print(f"Hex file generated: {os.path.abspath(output_hex)}")
        return output_hex
    else:
        print("Error generating hex file")
        sys.exit(1)

def copy_to_microbit(src_path, dest_name, max_retries=3):
    import microfs  # For micro:bit file system operations
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


def copy_to_microbit2(python_exec, src_path, dest_name=None, max_retries=3):
    """Copy file to micro:bit using 'python -m microfs put' command.
    
    Args:
        src_path (str): Path to the source file to copy
        dest_name (str, optional): Destination filename on the micro:bit. 
                                 If None, uses the source filename.
        max_retries (int): Maximum number of retry attempts
        
    Returns:
        bool: True if copy was successful, False otherwise
    """
    if dest_name is None:
        dest_name = os.path.basename(src_path)

    for attempt in range(max_retries):
        try:
            print(f"  - Attempt {attempt + 1}/{max_retries} for {os.path.basename(src_path)}...")
            
            # Run the microfs put command
            result = subprocess.run(
                [python_exec, '-m', 'microfs', 'put', src_path],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print(f"  - Successfully copied to {dest_name}")
                time.sleep(1)  # Brief pause for filesystem
                
                # Verify file exists
                ls_result = subprocess.run(
                    [python_exec, '-m', 'microfs', 'ls'],
                    capture_output=True,
                    text=True
                )
                
                if dest_name in ls_result.stdout:
                    print(f"  - Verified {dest_name} on micro:bit")
                    return True
                print(f"  - Warning: {dest_name} not found on micro:bit")
            else:
                error_msg = result.stderr.strip()
                if not error_msg and result.stdout:
                    error_msg = result.stdout.strip()
                print(f"  - Error: {error_msg or 'Unknown error'}")
                
            if attempt < max_retries - 1:
                print("  - Retrying in 5 seconds...")
                time.sleep(5)
                
        except Exception as e:
            print(f"  - Error: {str(e)}")
            if attempt < max_retries - 1:
                time.sleep(5)
    
    print(f"  - Failed to copy {dest_name} after {max_retries} attempts")
    return False


def flash_microbit(python_exec,port=None):
    """Flash the hex file to a connected micro:bit and copy Python files to the file system.
    Args:
        port: Serial port of the micro:bit (e.g., '/dev/tty.usbmodem...' on macOS/Linux, 'COM3' on Windows)
    """
        
    print(f"Looking for micro:bit on port: {port or 'auto'}")
    
    try:
        # flash main.py to the connected micro:bit
        print("Flashing main.py to micro:bit...")
        main_py_path = os.path.join(BUILD_DIR, 'main.py')
        # import uflash
        # if port:
        #     uflash.flash(paths_to_microbits=[port], path_to_python=main_py_path)
        # else:
        #     uflash.flash(path_to_python=main_py_path)
        cmd = [python_exec, "-m", "uflash", main_py_path]
        
        # Add port if specified
        if port:
            cmd.extend(["--port", port])
        
        print(f"Flashing {main_py_path} to micro:bit...")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
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
            success = copy_to_microbit2(python_exec, src_path)
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
    parser.add_argument('--prepare', action='store_true', help='Create virtual environment and install dependencies')
    args = parser.parse_args()
    
    print("=== Micro:bit Flasher ===")
    
    if args.list:
        list_microbits()
        return
    
    # Setup virtual environment and install dependencies
    python_exec = setup_venv()

    if not args.prepare:
        # Minify code
        build_dir = minify_code(python_exec)

        # Flash to micro:bit if requested
        flash_microbit(python_exec, args.port)
    
    print("=== Done ===")

if __name__ == "__main__":
    main()
