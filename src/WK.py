from microbit import *
from Parameters import *
import math
import time
import random

WK_ADDR = 0x10

class WK(object):
    """
    A class to control the WK robot's motors, servos, and LED eyes.
    
    This class provides methods to control the robot's movement, servo positions,
    and LED eye animations. It communicates with the robot's hardware through I2C.
    """
    def __init__(self):
        """
        Initialize the WK robot controller.
        
        Sets up initial states for the robot's eyes and movement control.
        """
        self.last_bl_ts = 0  # Timestamp of last blink
        self.eye_on = True   # Current state of the eyes (on/off)
        self.l_e_b = self.r_e_b = 1023  # Left and right eye brightness (0-1023)
        self.eye_icr = 1     # Eye brightness increment for animation
        self.bl_itl = 6000   # Blink interval in milliseconds
        self.pos = self.num_steps = 0  # Position and step counters for movement
        self.bl_g = 4000     # Base blink duration
        self.idle = False    # Whether servos are idle
        self.c_s = 0         # Current state index
        i2c.init()           # Initialize I2C communication
    # control DC motor, m is motor index, sp is speed
    def motor(self, m, sp):
        """
        Control a DC motor on the robot.
        
        Args:
            m (int): Motor index (1 or 2)
            sp (int): Speed value from -100 to 100 (negative for reverse)
        """
        if -100 <= sp <= 100 and 1 <= m <= 2:
            i2c.write(WK_ADDR, bytearray([m, 0x01, sp, 0]))

    # control 8 servos that attached to the i2C expansion board
    def servo(self, sr, a):
        """
        Set the angle of a servo motor.
        
        Args:
            sr (int): Servo index (0-7)
            a (int): Target angle in degrees (0-180)
        """
        if 0 <= sr <= 7:
            a = min(180, max(0, int(a)))
            i2c.write(WK_ADDR, bytearray([0x10 if sr == 7 else sr + 3, a, 0, 0]))

    # control the LED lights on the i2C expansion board
    def set_light(self, light):
        """
        Control the LED lights on the I2C expansion board.
        
        Args:
            light (int): Light intensity or pattern value
        """
        i2c.write(WK_ADDR, bytearray([0x12, light, 0, 0]))
        sleep(100)
        i2c.write(WK_ADDR, bytearray([0x11, 160, 0, 0]))

    # move servo motor toward the target angle with step
    def servo_step(self, target, sp, idx: int, p: Parameters):
        """
        Move a servo motor toward a target position with controlled speed.
        
        Args:
            target (float): Target angle in degrees
            sp (float): Speed/step size for movement
            idx (int): Index of the servo to move
            p (Parameters): Parameters object containing servo state
        """
        sp = math.fabs(sp)
        target = max(0, min(179, target))  # Clamp target to valid range
        err = p.s_err[idx] = target - p.s_tg[idx]  # Calculate error
        # Move toward target at controlled speed
        p.s_tg[idx] += err if math.fabs(err) < sp else sp if err >= 0 else -sp
        self.servo(idx, p.s_tg[idx])  # Update servo position

    # move servo motor toward the target angle immediately
    def servo_move(self, idx: int, p: Parameters):
        """
        Move all servos to their target positions for a given state.
        
        Args:
            idx (int): Index of the target state
            p (Parameters): Parameters object containing servo configurations
        """
        for i in range(p.dof):
            self.servo(i, p.st_tg[idx][i] + p.s_tr[i])
        self.idle = True  # Mark servos as having reached target

    # check if the servo motors are idle (target angle arrived)
    def is_servo_idle(self, s_list, p: Parameters):
        """
        Check if the specified servos have reached their target positions.
        
        Args:
            s_list (list): List of servo indices to check
            p (Parameters): Parameters object containing servo states
            
        Returns:
            bool: True if all servos are within 1 degree of target, False otherwise
        """
        self.idle = all(abs(p.s_err[i]) < 1 for i in s_list)
        return self.idle

    # move the robot to a position state with step
    def move(self, p: Parameters, states: list[int],
             sync_list: list[int], sp: float,
             async_list: list[int], async_sp: float) -> int:
        """
        Move the robot through a sequence of states with controlled timing.
        
        Args:
            p (Parameters): Parameters object containing movement configurations
            states (list[int]): List of state indices to cycle through
            sync_list (list[int]): Servo indices to move synchronously
            sp (float): Speed multiplier for synchronous servos
            async_list (list[int]): Servo indices to move asynchronously
            async_sp (float): Speed multiplier for asynchronous servos
            
        Returns:
            int: 0 if movement to next state should begin, 1 if still moving
        """
        if sp == 0:
            return 0
        self.pos = min(self.pos, len(states) - 1)  # Ensure position is in range
        self.c_s = states[self.pos]  # Get current state
        targets = p.st_tg[self.c_s]  # Get target positions for current state
        sps = p.st_spu[p.dict_sp.get(self.c_s,1)]  # Get speed settings for current state
        
        # Move synchronous servos
        for i in sync_list:
            self.servo_step(targets[i] + p.s_tr[i] + p.s_ct[i], sp * sps[i], i, p)
            
        # Move asynchronous servos (if any)
        for i in async_list:
            self.servo_step(targets[i] + p.s_tr[i] + p.s_ct[i], async_sp * sps[i], i, p)
            
        # Check if synchronous movement is complete
        if self.is_servo_idle(sync_list, p):
            self.pos = (self.pos + 1) % len(states)  # Move to next state
            self.num_steps += 1
            return 0  # Ready for next state
        return 1  # Still moving

    # turn on or off the eye led lights
    def eyes_ctl(self, c):
        """
        Control both eye LEDs simultaneously.
        
        Args:
            c (int): 0 to turn off, 1 to turn on
        """
        pin12.write_digital(c)  # Left eye
        pin13.write_digital(c)  # Right eye
        self.eye_on = c
        self.last_bl_ts = time.ticks_ms()  # Update last blink timestamp

    # control the brightness of the left eye led light
    def left_eye_bright(self, b):
        """
        Set the brightness of the left eye LED.
        
        Args:
            b (int): Brightness value (0-1023)
        """
        pin12.write_analog(b)
        self.l_e_b = b  # Store current brightness

    # control the brightness of the right eye led light
    def right_eye_bright(self, b):
        """
        Set the brightness of the right eye LED.
        
        Args:
            b (int): Brightness value (0-1023)
        """
        pin13.write_analog(b)
        self.r_e_b = b  # Store current brightness

    # blink the eye led lights
    def blink(self, alert_l):
        """
        Control the blinking animation of the robot's eyes.
        
        Args:
            alert_l (int): Alert level affecting blink behavior and brightness
        """
        ts_diff = time.ticks_ms() - self.last_bl_ts
        
        if self.eye_on:
            # Eyes are on, check if it's time to blink
            if ts_diff > self.bl_itl:
                self.eyes_ctl(0)  # Turn eyes off for blink
            else:
                # Set eye brightness based on alert level
                brightness = alert_l * 102
                self.bl_g = alert_l * 400  # Update blink duration base
                self.left_eye_bright(brightness)
                self.right_eye_bright(brightness)
        # Eyes are off, check if it's time to turn them back on
        elif ts_diff > random.randint(100, 250):
            self.eyes_ctl(1)  # Turn eyes back on
            # Occasionally do a quick blink (20% chance)
            if random.randint(0, 4) == 0:
                self.bl_itl = random.randint(100, 250)  # Quick blink
            else:
                # Normal blink with duration based on alert level
                self.bl_g = int(self.bl_g)
                self.bl_itl = random.randint(self.bl_g, self.bl_g * 2)

    # flash the eye led lights from dark to bright and back
    def flash(self, icr: int = 50):
        """
        Create a flashing/pulsing effect with the eye LEDs.
        
        This creates an alternating brightness effect where one eye fades in
        while the other fades out, creating a "knight rider" style animation.
        
        Args:
            icr (int): Increment value for brightness change (controls speed)
        """
        # Update brightness with current increment
        self.l_e_b += self.eye_icr
        
        # Reverse direction at brightness limits
        if self.l_e_b >= 1023:
            self.eye_icr = -icr  # Start decreasing brightness
            self.l_e_b = 1023    # Clamp to maximum
        elif self.l_e_b <= 0:
            self.eye_icr = icr   # Start increasing brightness
            self.l_e_b = 0       # Clamp to minimum
            
        # Set complementary brightness for each eye
        self.right_eye_bright(1023 - self.l_e_b)  # Opposite of left eye
        self.left_eye_bright(self.l_e_b)