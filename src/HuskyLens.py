from microbit import *
from WK import WK
from Parameters import Parameters
import time

# HuskyLens I2C address
HUSKYLENS_ADDR = 0x32

# HuskyLens protocol commands
CMD_HEADER = 0x55
CMD_TAIL = 0xAA
CMD_REQUEST = 0x20
CMD_REQUEST_BLOCKS = 0x21

# HuskyLens algorithm IDs
ALGORITHM_OBJECT_TRACKING = 0x03  # Object recognition mode

# Image dimensions (HuskyLens has a 320x240 resolution)
IMAGE_WIDTH = 320
IMAGE_HEIGHT = 240

# Servo indices (adjust based on your robot's configuration)
SERVO_PAN = 0   # Index for pan (left-right) servo
SERVO_TILT = 1  # Index for tilt (up-down) servo

# Center position of the image
CENTER_X = IMAGE_WIDTH // 2
CENTER_Y = IMAGE_HEIGHT // 2

# Threshold for considering the object centered (in pixels)
CENTER_THRESHOLD = 20

class HuskyLensController:
    def __init__(self, wk, params):
        """Initialize the HuskyLens controller and robot servos."""
        self.wk = wk
        self.params = params
        
        # Initialize servos to center position
        self.current_pan = 90
        self.current_tilt = 90
        
        # Initialize I2C
        #i2c.init() # WK already init the I2C
        
        # Set HuskyLens to object recognition mode
        self._set_algorithm(ALGORITHM_OBJECT_TRACKING)
        
        # Wait for HuskyLens to initialize
        sleep(1000)
    
    def _send_command(self, command, data=[]):
        """Send a command to HuskyLens over I2C."""
        buffer = bytearray()
        buffer.append(CMD_HEADER)
        buffer.append(CMD_HEADER)
        buffer.append(len(data) + 3)  # Length of command + data + checksum
        buffer.append(command)
        
        # Add data bytes
        for b in data:
            buffer.append(b)
            
        # Calculate checksum
        checksum = 0
        for b in buffer[2:]:  # Exclude header bytes
            checksum += b
        buffer.append(checksum & 0xFF)
        
        # Send command
        try:
            i2c.write(HUSKYLENS_ADDR, buffer)
            return True
        except OSError:
            return False
    
    def _set_algorithm(self, algorithm_id):
        """Set the algorithm mode on HuskyLens."""
        return self._send_command(0x2D, [0x02, 0x01, algorithm_id])
    
    def _request_blocks(self):
        """Request object detection blocks from HuskyLens."""
        if not self._send_command(CMD_REQUEST_BLOCKS):
            return None
            
        try:
            # Read response (header: 0x55 0x55, length, command, data..., checksum)
            response = i2c.read(HUSKYLENS_ADDR, 5)  # Read header and length first
            if not response or len(response) < 5 or response[0] != CMD_HEADER or response[1] != CMD_HEADER:
                return None
                
            data_length = response[2] - 3  # Subtract command and checksum bytes
            if data_length <= 0:
                return []
                
            # Read remaining data
            data = i2c.read(HUSKYLENS_ADDR, data_length + 1)  # +1 for checksum
            if not data or len(data) < data_length + 1:
                return None
                
            # Verify checksum
            checksum = sum(bytearray(response[2:])) + sum(bytearray(data[:-1]))
            if (checksum & 0xFF) != data[-1]:
                return None
                
            # Parse blocks
            blocks = []
            i = 0
            while i < data_length:
                if i + 8 > data_length:  # Each block is 8 bytes
                    break
                    
                block = {
                    'x': (data[i] << 8) | data[i+1],
                    'y': (data[i+2] << 8) | data[i+3],
                    'width': (data[i+4] << 8) | data[i+5],
                    'height': (data[i+6] << 8) | data[i+7],
                    'id': data[i+8] if i + 8 < data_length else 0
                }
                blocks.append(block)
                i += 9  # Move to next block
                
            return blocks
            
        except OSError:
            return None
    
    def _move_servos_to_center(self, x, y):
        """Adjust servos to center the detected object."""
        # Calculate error from center
        error_x = x - CENTER_X
        error_y = y - CENTER_Y
        
        # Adjust pan (left-right)
        if abs(error_x) > CENTER_THRESHOLD:
            # Scale the movement based on how far from center
            pan_step = min(5, max(1, abs(error_x) // 20))
            if error_x < 0:
                self.current_pan = min(180, self.current_pan + pan_step)
            else:
                self.current_pan = max(0, self.current_pan - pan_step)
            self.wk.servo(SERVO_PAN, int(self.current_pan))
        
        # Adjust tilt (up-down)
        if abs(error_y) > CENTER_THRESHOLD:
            # Scale the movement based on how far from center
            tilt_step = min(5, max(1, abs(error_y) // 20))
            if error_y < 0:
                self.current_tilt = min(180, self.current_tilt + tilt_step)
            else:
                self.current_tilt = max(0, self.current_tilt - tilt_step)
            self.wk.servo(SERVO_TILT, int(self.current_tilt))
        
        # Check if the object is centered
        return abs(error_x) <= CENTER_THRESHOLD and abs(error_y) <= CENTER_THRESHOLD
    
    def track_objects(self):
        """Main tracking loop."""
        print("Starting object tracking...")
        
        blocks = self._request_blocks()
        
        if blocks and len(blocks) > 0:
            # Get the first detected object
            obj = blocks[0]
            x = obj['x']
            y = obj['y']
            
            print(f"Object detected at ({x}, {y})")
            
            # Move servos to center the object
            #is_centered = self._move_servos_to_center(x, y)
                

# Main execution
# if __name__ == "__main__":
#     try:
#         controller = HuskyLensController()
#         controller.track_objects()
#     except KeyboardInterrupt:
#         print("\nStopping object tracking...")
#     except Exception as e:
#         print(f"Error: {e}")
#     finally:
#         # Reset servos to center position
#         i2c.init()
#         controller.wk.servo(SERVO_PAN, 90)
#         controller.wk.servo(SERVO_TILT, 90)
#         print("Servos reset to center position.")