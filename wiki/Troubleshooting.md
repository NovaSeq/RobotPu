# Troubleshooting

## Common Issues

### Pu Won't Turn On
- Check if the battery is properly connected
- Ensure the battery is charged (connect to USB and wait 30 minutes)
- Try a different USB cable
- Check the power switch is in the ON position
- If using batteries, try fresh ones

### Can't Connect to Computer
1. **Check USB Connection**
   - Try a different USB port
   - Use a different USB cable (some are power-only)
   - Try a different computer if possible

2. **Check Device Recognition**
   - **Windows**: Look for "MAINTENANCE" drive in File Explorer
   - **Mac/Linux**: Check if the device appears in `/Volumes/` or `/media/`
   - If not recognized, try resetting the micro:bit

3. **Driver Issues (Windows)**
   - Download and install the [mbed Windows serial driver](https://os.mbed.com/handbook/Windows-serial-configuration)
   - Update device drivers through Device Manager

### Code Won't Upload
- Make sure Pu is in programming mode (LEDs should be flashing)
- Close any programs that might be using the serial port (Mu, Thonny, etc.)
- Try resetting the micro:bit (press the reset button on the back)
- Ensure you have enough free space on the micro:bit
- Check for syntax errors in your code

### Motors Not Responding
1. Check motor connections
2. Ensure the battery is charged
3. Verify your code is using the correct pin numbers
4. Check for any error messages in the serial console
5. Try the motor test example from the Examples page

### Display Issues
- If the display is blank, try resetting the micro:bit
- Check your code for `display.clear()` or `display.off()` calls
- Ensure you're not overwriting the display too quickly (add small delays)
- Verify the contrast is set correctly in your code

## Error Messages

### "No micro:bit found"
1. Check USB connection
2. Try a different USB port/cable
3. Restart your computer
4. Check if the device appears in your system's file explorer

### "Out of memory"
1. Reduce the size of your program
2. Remove unused imports
3. Use more efficient data structures
4. Split your code into multiple files

### "Flash write failed"
1. Ensure the micro:bit is properly connected
2. Try resetting the micro:bit
3. Check for any physical damage to the USB port
4. Try a different computer if possible

## Common Programming Issues

### Buttons Not Working
- Make sure you're checking for button presses in a loop
- Use `button_a.was_pressed()` for single presses
- Add a small delay in your main loop to prevent missing inputs

### Sensors Giving Strange Values
- Check the sensor connections
- Ensure the sensor is properly calibrated
- Check for electrical interference
- Verify the sensor is getting power

### Program Crashes or Freezes
1. Check for infinite loops
2. Look for division by zero errors
3. Ensure all variables are initialized
4. Add error handling with try/except blocks

## Getting Help

If you can't resolve your issue:
1. Check the [GitHub Issues](https://github.com/NovaSeq/RobotPu/issues) for similar problems
2. Search the [Community Forum](https://github.com/NovaSeq/RobotPu/discussions)
3. Create a new issue with:
   - Steps to reproduce the problem
   - Expected vs actual behavior
   - Complete error messages
   - Your hardware setup (computer OS, Python version, etc.)
   - Any relevant code snippets

## Factory Reset
If all else fails, you can perform a factory reset:
1. Download the latest [RobotPu hex file](https://robotgyms.com/courses/the-story-of-pu-book-1-pair-up/lessons/the-user-manual-of-pu/topic/how-to-update-programs-for-pu/)
2. Drag and drop the hex file onto the micro:bit drive
3. Wait for the yellow LED to stop flashing
4. Your Pu robot should now be reset to factory settings
