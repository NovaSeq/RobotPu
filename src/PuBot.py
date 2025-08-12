from microbit import *
import speech
import math
import random
import time
import neopixel
from WK import *
from MakeRadio import *
from MusicLib import *
from HCSR04 import *
from Parameters import *
from Content import *
import os
import gc

pr = Parameters()
wk = WK()

class RobotPu(object):
    """
    Main class representing the RobotPu robot.
    
    Handles robot movement, state management, sensor processing, and communication.
    """
    def __init__(self, sn, name="peu"):
        """
        Initialize the RobotPu instance.
        
        Args:
            sn (str): Robot's serial number
            name (str, optional): Robot's name. Defaults to "peu".
            
        The initialization sets up all necessary parameters for robot operation including:
        - Motion control parameters
        - State management
        - Sensor configurations
        - Communication settings
        - Behavior patterns
        """
        # Robot identification and basic settings
        self.name = name          # User-assigned robot name
        self.sn = sn              # Unique serial number for the robot
        
        # State machine control
        self.gst = 0              # Current state machine state index
        
        # Motion control parameters
        self.last_cmd_ts = 0      # Timestamp of last received command (ms)
        self.fw_sp = 6         # Forward speed multiplier
        self.bw_sp = -3           # Backward speed multiplier
        self.sp = 0.0             # Current speed setting
        self.di = 0.0             # Current direction setting (degrees)
        
        # Head movement calibration
        self.h_u_bias = 0         # Vertical bias for head positioning
        self.h_l_bias = 0         # Horizontal bias for head positioning
        
        # Alert system parameters
        self.alt_l = 10           # Alert level (sensitivity to environment)
        self.alt_sc = 0.9         # Alert decay rate (0-1)
        self.r_st = 26            # Index of rest state in state machine
        
        # IMU and balance control
        self.bd_pth = 0.0         # Current body pitch (degrees)
        self.bd_pth2 = 0.0        # Previous body pitch (for filtering)
        self.bd_rl = 0.0          # Current body roll (degrees)
        self.bd_rl2 = 0.0         # Previous body roll (for filtering)
        self.pth = 0.0            # Target pitch for balance control
        self.rl = 0.0             # Target roll for balance control
        self.max_g = 1.0          # Maximum detected acceleration (g)
        self.g_thr = 2000         # Acceleration threshold for fall detection
        self.max_pth_ctl = 15.0   # Maximum allowed pitch control output
        self.max_rl_ctl = 15.0    # Maximum allowed roll control output
        
        # Exploration behavior parameters
        self.ep_sp = 0.0          # Exploration speed
        self.ep_di = 0.0          # Exploration direction
        self.ep_max_i = 0         # Index of clearest direction
        self.ep_thr = 7.5         # Distance threshold for obstacle detection (cm)
        self.ep_ot = 0            # Tilt offset during exploration
        self.ep_far = 30          # Far distance threshold for obstacle detection (cm)  
        
        # Fall recovery tracking
        self.fell_count = 0       # Number of falls detected
        self.last_state = 0       # State before falling
        
        # Timing and synchronization
        self.t_c = 0              # Last command timestamp
        self.l_o_t = 0            # Left tilt offset
        self.r_o_t = 0            # Right tilt offset
        
        # Dance behavior configuration
        self.d_st = [0]           # Current dance state
        self.d_dict = {           # Predefined dance routines
            14: [0, 15, 15, 0, 3, 5, 3],  # Forward-backward movement
            0: [0, 19, 0, 18, 0, 3],      # Side-to-side movement
            5: [3, 5, 2, 5, 3],           # Quick steps
            16: [17, 16, 17, 16, 17]      # Rocking motion
        }
        self.d_sp = 1.5           # Dance speed multiplier
        self.last_low_b = 0       # Timestamp of last low beat
        self.last_high_b = 0      # Timestamp of last high beat
        self.dance_l_itv = 12     # Left/right wiggle angle (degrees)
        self.dance_u_itv = 15     # Up/down wiggle angle (degrees)
        
        # Audio and speech
        self.s_list = []          # Phoneme list for speech synthesis
        
        # Radio communication
        self.groupID = 166        # Default radio group ID
        
        # Initialize hardware components
        self.read_config()        # Load configuration from file
        self.c = Content()        # Speech content manager
        self.music = MusicLib()   # Music and sound effects
        self.sonar = HCSR04()     # Ultrasonic distance sensor
        self.np = neopixel.NeoPixel(pin16, 4)  # LED control
        
        # Initialize communication
        self.set_group(self.groupID)
        
        # Initialize sensors and outputs
        wk.eyes_ctl(1)            # Turn on eyes
        self.sound_threshold = 116  # Sound detection threshold
        microphone.set_threshold(SoundEvent.LOUD, self.sound_threshold)
        speaker.on()              # Enable speaker
        
        # State index to function mapping
        self.st_dict = {
            -3: self.fall,
            -2: self.fetal,
            0: self.idle,
            1: self.explore,
            2: self.jump,
            3: self.dance,
            4: self.kick,
            5: self.joystick
        }
        
        # Radio command to function mapping
        self.cmd_dict = {
            "#puspeed" : self.speed,
            "#puturn" : self.turn,
            "#puroll" : self.roll,
            "#pupitch" : self.pitch,
            "#puB" : self.button,
            "#pulogo" : self.logo,
            "#purs" : self.pose
        }

    # read config from the pu.txt file
    def read_config(self):
        """
        Load robot configuration from 'pu.txt' file.
        
        The configuration file should contain three lines:
        1. Serial number (string)
        2. Group ID (integer)
        3. Comma-separated list of servo trim values (floats)
        
        If the file is missing or corrupted, default values will be used.
        """
        try:
            with open("pu.txt", 'r') as f:
                c = f.read().split('\n')
                self.sn = c[0]
                self.groupID = int(c[1])
                pr.s_tr = [float(i) for i in c[2].split(',')]
        except Exception:
            # Silently continue with default values if config can't be read
            pass

    #
    # def write_config (self):
    #     """
    #     Save current configuration to 'pu.txt' file.
    #     
    #     The configuration includes:
    #     - Robot serial number
    #     - Current group ID
    #     - Servo trim values
    #     """
    #     try:
    #         microfs.rm('pu.txt')
    #         #os.remove('pu.txt')
    #     except:
    #         print("pu.txt not found")
    #     with open("pu.txt", 'w') as f:
    #         f.write(self.sn + "\n")
    #         f.write(str(self.groupID) + "\n")
    #         # f.write(','.join([str(i) for i in self.p.s_tr]))

    # set radio channel
    def set_group(self, g):
        """
        Set the radio communication group/channel.
        
        Args:
            g (int): The group ID to set (0-255).
        """
        self.groupID = g
        self.show_channel()
        self.ro = MakeRadio(self.groupID)

    # show radio channel on the microbit display
    def show_channel(self):
        """
        Display the current radio channel on the micro:bit LED display.
        
        Note: The displayed value is (groupID - 160) to fit the 0-95 range
        that can be shown on the 5x5 LED matrix.
        """
        display.show(self.groupID - 160)

    # increment radio channel
    def incr_group_id(self, i):
        """
        Adjust the radio group ID by a specified amount.
        
        Args:
            i (int): Amount to adjust the group ID by (can be negative).
            The group ID will wrap around at 0 and 255.
        """
        self.groupID = (self.groupID + i) % 256
        self.set_group(self.groupID)

    # make the robot stand in neutral position
    def stand(self):
        """
        Set the robot to a neutral standing position.
        
        This method positions all servos to their default neutral positions
        with a moderate movement speed (2.0).
        """
        self.move([0], [0, 1, 2, 3, 4, 5], 2.0, [], 0.5)

    # make the robot introduce itself
    def intro(self):
        """
        Make the robot introduce itself using text-to-speech.
        
        The robot will speak its serial number and name in a friendly greeting.
        This helps with identification when multiple robots are present.
        """
        self.talk("My name is " + self.sn + " " + self.name)

    # calibrate the robot
    def calibrate(self):
        """
        Run the robot's calibration routine.
        
        This method performs the following steps:
        1. Moves servos to a known calibration position
        2. Makes the robot introduce itself
        3. Flashes the eyes three times for visual feedback
        4. Returns to a neutral standing position
        """
        wk.servo_move(25, pr)  # Move to calibration position
        self.intro()
        for i in range(3):
            wk.flash(1020)  # Bright flash
            sleep(500)      # Half second delay between flashes
        wk.eyes_ctl(1)      # Turn eyes on
        wk.servo_move(0, pr)  # Return to neutral position
        sleep(2000)         # Wait for movement to complete

    # make the robot fetal position
    def fetal(self):
        """
        Set the robot to a compact fetal position.
        
        This position is used for:
        - Protection during falls
        - Conserving power
        - Minimizing space when not in use
        """
        wk.flash()
        if random.randint(0, 200) == 0:
            self.talk("Help me!")
        self.move([1], [0, 1, 2, 3, 4, 5], 2.0, [], 0.5)

    # set servo control vector, the final target = current vector + control vector + trim vector
    def set_ct(self, indx_l, v_l):
        """
        Set multiple servo positions with direct control.
        
        Args:
            indx_l (list[int]): List of servo indices to control (0-25)
            v_l (list[int]): Target positions for each servo (0-180 degrees)
            
        Note:
            The length of indx_l and v_l must match.
            Only valid servo indices (0-25) will be processed.
        """
        le = min(len(indx_l), len(v_l))
        for i in range(le):
            pr.s_ct[indx_l[i]] = v_l[i]

    # make the robot loop through the given states  
    def move(self, states: list[int], sync_list: list[int], sp: float, async_list: list[int], async_sp: float):
        """
        Execute a coordinated movement sequence.
        
        Args:
            states (list[int]): Sequence of state indices to move through
            sync_list (list[int]): Indices of servos to move synchronously
            sp (float): Speed multiplier for synchronous movement (0.0-1.0)
            async_list (list[int]): Indices of servos to move asynchronously
            async_sp (float): Speed multiplier for asynchronous movement (0.0-1.0)
            
        Returns:
            int: Status code indicating movement completion
        """
        return wk.move(pr, states, sync_list, sp, async_list, async_sp)

    # make the robot move with self-balance
    def move_balance(self, sp: float, di: float, fw_l: list[int], bw_l: list[int]):
        """
        Execute balanced movement with speed and direction control.
        
        Args:
            sp (float): Speed multiplier (positive for forward, negative for backward)
            di (float): Directional bias (-1.0 to 1.0)
            fw_l (list[int]): State sequence for forward movement
            bw_l (list[int]): State sequence for backward movement
            
        Returns:
            int: Status code from movement execution
            
        Note:
            Automatically adjusts for balance and reduces speed when tilted.
        """
        sts = fw_l if sp > 0 else bw_l
        self.balance_param()
        
        if wk.pos < 2 or wk.pos == 6:  # left side
            self.l_o_t = min(self.max_rl_ctl, max(0.0, self.bd_rl*0.8 - pr.w_t))
            lf = -12 * di
        else:  # right side
            self.r_o_t = max(-self.max_rl_ctl, min(0.0, self.bd_rl*0.8 + pr.w_t))
            lf = 12 * di
            
        # Calculate overall tilt compensation
        o_t = self.l_o_t + self.r_o_t

        # stability compensation of speed
        sp /= 1.0 + 0.01 * (abs(self.bd_rl) + abs(self.bd_pth))+ math.sqrt(math.fabs(o_t * 0.5))
        
        # Apply control to servos
        self.set_ct([0, 1, 2, 3, 4, 5],
                   [o_t, lf - o_t, o_t, -lf - o_t, -40 * di - o_t, min(25.0, -2.0 * self.bd_pth2)])
        return self.move(sts, [0, 1, 2, 3], sp, [4, 5], sp)

    # calculate balance parameters from IMU data
    def balance_param(self):
        """
        Calculate and update balance parameters from IMU data.
        
        This method:
        1. Gets current accelerometer readings
        2. Calculates pitch and roll angles
        3. Updates body orientation
        4. Applies low-pass filtering to smooth readings
        """
        a = accelerometer.get_values()
        self.pth = math.degrees(math.atan2(a[1], -a[2]))
        self.max_g = math.sqrt(sum(x * x for x in a))
        self.rl = math.degrees(math.asin(a[0] / self.max_g)) if self.max_g > 0 else 0.0
        
        # Calculate body-relative angles with servo trim compensation
        bd_p = self.pth + (pr.st_tg[0][5] + pr.s_tr[5] - pr.s_tg[5])
        servo_lft = math.radians(pr.s_tg[4] - pr.st_tg[0][4] - pr.s_tr[4])
        
        # Update filtered body orientation with low-pass filter
        self.bd_rl = bd_p * math.sin(servo_lft) + self.rl * math.cos(servo_lft)
        self.bd_rl2 = (self.bd_rl + 9 * self.bd_rl2) * 0.1  # Low-pass filter
        
        self.bd_pth = bd_p * math.cos(servo_lft) - self.rl * math.sin(servo_lft)
        self.bd_pth2 = (self.bd_pth + 9 * self.bd_pth2) * 0.1  # Low-pass filter

    # make the robot rest
    def rest(self):
        self.balance_param()
        rl = min(35.0, max(-35.0, self.bd_rl2))
        if abs(rl)> 5:
            self.set_ct([0, 1, 2, 3, 4],
                       [rl, rl * -1.0, rl, rl * -1.0, rl * -0.5])
        if math.fabs(self.bd_pth2) > 12:
            self.set_ct([5], [-self.bd_pth2])
        sl = microphone.sound_level()
        pr.st_tg[self.r_st][5]=90-sl*0.3
        return self.move([self.r_st], [0, 1, 2, 3, 4, 5],
                         1 + sl*0.01,
                         [], 0.5)

    # make the robot walk with self-balance
    def walk(self, sp, di):
        return self.move_balance(sp, di, pr.walk_fw_sts, pr.walk_bw_sts)

    # make the robot side step with self-balance    
    def side_step(self, di):
        sts = [20, 22, 0, 19] if di > 0 else [18, 21, 23, 0]
        self.set_ct([0, 1, 2, 3, 4, 5], [0, 0, 0, 0, 0, 0])
        return self.move(sts, [0, 1, 2, 3], di * self.fw_sp,
                         [4, 5], di * self.fw_sp)

    def get_turn_from_sonar(self, ep_dis, turn_gain=1.5):
        """
        Map sonar distance readings to a steering direction for auto-pilot.
        
        Args:
            ep_dis: List of sonar distance readings from left to right
            turn_aggressiveness: Scaling factor for turn intensity (default: 1.5)
        
        Returns:
            float: Steering direction between -1.0 (full left) and 1.0 (full right)
        """
        if not ep_dis:
            return 0.0
        
        # Calculate center of mass of the distances
        tw = sum(ep_dis)
        if tw == 0:
            return 0.0
        
        # Calculate normalized position from -1 (left) to 1 (right)
        pos = [i * 2 / (len(ep_dis) - 1) - 1 for i in range(len(ep_dis))] if len(ep_dis) > 1 else [0]
        # calculate center of mass
        cm = sum(d * p for d, p in zip(ep_dis, pos)) / tw
        
        # Apply turn aggressiveness and clamp to [-1, 1]
        d = cm * turn_gain
        return max(-1.0, min(1.0, d))
    
    # compute auto-pilot parameters for explore mode
    def set_explore_param(self):
        obs_hcsr = min(pr.ep_dis[pr.ep_mid1], pr.ep_dis[pr.ep_mid2])
        if obs_hcsr < self.ep_thr + self.ep_far:
            # max_hcsr, self.ep_max_i = max((dis, i) for i, dis in enumerate(pr.ep_dis))
            # self.ep_di = (self.ep_di*3+pr.ep_dir[self.ep_max_i] + random.uniform(-0.2, 0.2))*0.25
            nd = self.get_turn_from_sonar(pr.ep_dis[pr.ep_mid1:pr.ep_mid2+1], 3)
        else:
            #self.ep_di = (self.ep_di*3+min(1.0, max(-1.0, (pr.ep_dis[pr.ep_mid2] - pr.ep_dis[pr.ep_mid1]) / (pr.ep_dis[pr.ep_mid2] + pr.ep_dis[pr.ep_mid1]) * 1.5)))*0.25
            nd = self.get_turn_from_sonar(pr.ep_dis, 5)
        obs_hcsr = min(pr.ep_dis)
        dis = (obs_hcsr - self.ep_thr)
        if self.ep_sp < 0:
            # stuck in corner, turn aggrassively
            nd = 1 if nd > 0 else -1
            self.ep_di = (self.ep_di*9+nd)*0.1
            dis -= 12 + random.randint(-5, 0)
            if random.randint(0, 400) == 0:
                self.talk(self.c.sentences[5])
                self.ro.send_str("#puc:" + self.sn + ":W1")
        else:
            self.ep_di = (self.ep_di*3+nd)*0.25
        # apply low-pass filter to speed
        self.ep_sp = (self.ep_sp+min(self.fw_sp, (dis + 5) * 0.8) if dis >= 0 else max(self.bw_sp, (dis - 5) * 0.6))*0.5

    # make the robot explore with self-balance
    def explore(self):
        # get current point cloud index
        a = pr.s_tg[1 if wk.pos < 2 else 3]
        # fill in point cloud by sonar distance
        d_i = 0 if a > 110 else 1 if a > 90 else 2 if a > 70 else 3
        pr.ep_dis[d_i] = (pr.ep_dis[d_i] + self.sonar.distance_cm()) * 0.5
        self.set_explore_param()
        return self.walk(self.ep_sp, self.ep_di)

    # make the robot do random LED light show
    def random_light(self):
        for p in range(0, 4):
            self.np[p] = (random.randint(0, 128), random.randint(0, 128), random.randint(0, 128))
        self.np.show()
    # make the robot dance with self-balance
    def dance(self):
        ts = time.ticks_ms()
        ms = microphone.sound_level()
        il = self.music.is_a_beat(ts, ms, 1.05)
        if ts - self.last_high_b > self.music.period * 0.5:
            self.dance_l_itv *= -1
            self.dance_u_itv *= -1
            self.random_light()
            self.last_high_b = ts
        if il and ts - self.last_low_b > self.music.period * random.randint(8, 16):
            self.d_st = self.d_dict.get(self.d_st[-1], [random.choice(pr.dance_ok)])
            self.last_low_b = ts
        self.balance_param()
        ft = min(12.0, max(-12.0, self.rl * 0.8 + self.dance_l_itv * 0.2))
        if math.fabs(ft)<8:
            ft =0
        lt = ft + self.dance_l_itv
        self.set_ct([0, 1, 2, 3, 4, 5], [ft, lt, ft, lt, self.rl, self.dance_u_itv-ms*0.1])
        self.d_sp = min(2.5, self.d_sp * 1.015)
        if self.max_g > 1800:
            self.d_sp *= 0.9
        return self.move(self.d_st, [0, 1, 2, 3], self.d_sp, [4, 5], self.d_sp)

    # make the robot jump
    def jump(self):
        md = self.move([24, 14, 0, 0], [0, 1, 2, 3], 3, [4, 5], 2)
        if md == 0 and wk.pos == 3:
            self.gst = 5
            wk.servo(6, 0)
        else:
            wk.servo(6, 100)

    # make the robot kick
    def kick(self):
        md = self.move(pr.walk_fw_sts, [0, 1, 2, 3], 3, [4, 5], 2)
        if md == 0 and (wk.pos == 0 or wk.pos == 2):
            self.gst = 5

    # make the robot talk
    def talk(self, t):
        speech.say(t, speed=90, pitch=35, throat=225, mouth=225)

    # make the robot sing
    def sing(self, s):
        speech.sing(s, speed=90, pitch=35, throat=225, mouth=225)

    # make the robot idle
    def idle(self):
        if random.randint(0, 100) == 0:
            # decrease alert level to sleep
            self.alt_l *= self.alt_sc
        self.check_wakeup()
        if self.rest() == 0:
            sl = microphone.sound_level()
            self.sound_threshold = (self.sound_threshold * 24 + sl) * 0.04
            if random.randint(0, 1000) == 0:
                self.alt_l -= 2
                self.state_talk()
                self.ro.send_str("#puhi, " + self.sn + " " + self.name)
            if random.randint(0, 280- sl)== 0 or sl> self.sound_threshold*3:
                pr.st_tg[26][4] = random.randint(30, 160) #min(160, max(20, self.p.st_tg[26][4]+random.randint(-10, 10)))
                pr.st_tg[26][5] = random.randint(40, 105) #min(115, max(30, self.p.st_tg[26][5]+random.randint(-10, 10)))
            if sl> self.sound_threshold*2.5:
                self.talk(self.c.cute_words())

    # make the robot sleep
    def sleep(self):
        self.balance_param()
        self.stand()
        wk.eyes_ctl(0)
        self.np.clear()
        if self.check_wakeup() == 1:
            self.gst = 0

    # make the robot deal with fall
    def fall(self):
        wk.flash()
        if random.randint(0, 500) == 0:
            self.talk("Help me stand up!")
            self.s_code("E2")

    # make the robot move with joystick
    def joystick(self):
        if self.sp == 0:
            wk.servo_step(90 + self.h_l_bias, 1, 4, pr)
            wk.servo_step(90 + self.h_u_bias, 1, 5, pr)
            if math.fabs(self.di) > 0.9:
                self.side_step(self.di)
        else:
            self.walk(self.sp, self.di)

    # check if the robot should wake up
    def check_wakeup(self):
        # wake up if there is noise and tilt
        if (self.max_g > self.g_thr or microphone.current_event() == SoundEvent.LOUD
                or math.fabs(self.bd_rl - self.bd_rl2) > 20 or math.fabs(self.bd_pth - self.bd_pth2) > 20):
            self.alt_l = 10
            return 1
        if self.alt_l < 1:
            self.gst = -1
        return 0

    # make the robot talk automatically
    def state_talk(self):
        rt = random.randint(0, 5)
        if rt == 0:
            self.sing(self.c.compose_song())
        else:
            self.talk(random.choice(["Hello! I am " + self.sn + " " + self.name + ". ",
                                     random.choice(self.c.sentences),
                                     "Temperature is " + str(temperature()) + " degree.",
                                     "I ran " + str(wk.num_steps) + " steps today!"
                                     ]))

    # do nothing
    def noop(self, v):
        pass

    # control the speed of the robot
    def speed (self, v:float):
        if v > 0.1:
            self.sp = v * self.fw_sp
            self.gst = 5
        elif v < -0.1:
            self.sp = -v * self.bw_sp
            self.gst = 5
        else:
            self.sp = 0

    # control the direction of the robot
    def turn(self, v:float):
        self.di = (self.di*4 + v) * 0.2

    # control the roll of the robot
    def roll(self, v:float):
        self.h_l_bias = (v + self.h_l_bias) * 0.5

    # control the pitch of the robot
    def pitch(self, v:float):
        self.h_u_bias = (v * -1 + self.h_u_bias) * 0.5

    # switch robot state with buttion events
    def button(self, v:int):
        if v == 0:
            self.gst = 0
            self.h_u_bias = 0
            self.h_l_bias = 0
            self.talk("Rest!")
            self.ro.send_str("#puack")
        elif v == 1:
            self.talk("Exploring")
            self.ep_sp = 4.0
            self.ep_di = 0.0
            self.gst = 1
        elif v == 2:
            self.gst = 2
        elif v == 3:
            self.talk("Dance!")
            self.d_sp = 1.5
            self.gst = 3
        elif v == 4:
            # self.talk("Kick!")
            self.gst = 4

    # robot actions when the logo button is pressed
    def logo (self, v):
        self.state_talk()

    # control the pose of the robot during rest
    def pose (self, v:int):
        self.r_st = v
        self.gst = 0
        self.rest()

    # publish robot status code via radio
    def s_code(self, code):
        self.ro.send_str(":".join(["#puc", self.sn, code]))

    # process radio commands, change robot states
    def process_radio_cmd(self):
        """
        Process incoming radio commands and update robot behavior accordingly.
        
        Handles various command formats:
        - "#put[text]": Make the robot speak the given text
        - "#pus[song]": Add to song buffer and play when complete (6 segments)
        - "#puhi[name]": Greet another robot by name when in idle state
        - "#pun[name]": Update robot's name and introduce itself
        
        Note:
            Song data is buffered in self.s_list and played when 6 segments are received
            to handle transmission of longer musical sequences.
        """
        d = self.ro.receive_packet()
        if d is None:
            return
            
        if isinstance(d, tuple):
            # Handle command tuples (from cmd_dict)
            self.last_cmd_ts = time.ticks_ms()
            la, v = d
            self.cmd_dict.get(la, self.noop)(v)
        elif type(d) is str:
            # Handle string-based commands
            if d.startswith("#put"):
                self.talk(d[4:])
            elif d.startswith("#pus"):
                self.s_list.append(d[4:])
                if len(self.s_list) >= 6:
                    self.sing(''.join(self.s_list))
                    self.s_list = []
            elif d.startswith("#puhi"):
                self.talk("My friend " + d[5:] + " is here")
            elif d.startswith("#pun"):
                self.sn = d[4:]
                self.intro()

    # set robot states based on sensor inputs   
    def set_states(self):
        """
        Update robot states based on sensor inputs and button presses.
        
        This method handles:
        - Fall detection using accelerometer
        - Radio group ID changes via button presses
        - Automatic state transitions based on inactivity
        - Balance monitoring and adjustments
        
        State Transitions:
        - Any -> Fall (-2): On free-fall detection
        - Active -> Idle (0): After 2 seconds of no commands
        - Balance Adjustment: When tilt exceeds safe thresholds
        
        Button Controls:
        - Button A: Increment radio group ID
        - Button B: Decrement radio group ID
        """
        # Check for free-fall condition
        if accelerometer.was_gesture("freefall"):
            self.gst = -2  # Enter fall state
            
        # Handle button presses for group ID changes
        if button_a.was_pressed():
            self.incr_group_id(1)
        if button_b.was_pressed():
            self.incr_group_id(-1)
            
        # Handle automatic state transitions
        if self.gst > 0:  # If in any active state
            self.alt_l = 10  # Reset alert level
            if time.ticks_ms() - self.last_cmd_ts > 2000:  # 2s timeout
                self.gst = 0  # Return to idle
                
        # Check balance and adjust if needed
        if self.gst != -2:  # If not in fall state
            if abs(self.bd_rl2) > 75 or abs(self.bd_pth2) > 75:  # Check tilt thresholds
                self.balance_param()  # Recalculate balance parameters
                self.fell_count += 1
                wk.num_steps = 0
                if self.fell_count > 16:  # If fallen too many times
                    self.gst = -3  # Enter recovery state
            else:
                self.fell_count = 0
                if self.gst == -3:  # If recovering
                    self.gst = self.last_state  # Return to previous state
                    self.talk("Thanks")  # Acknowledge recovery
                    #self.show_channel()  # Update display

    # state machine
    def state_machine(self):
        """
        Main state machine for robot behavior control.
        
        This method processes the current state (gst) and executes the corresponding
        behavior. The state machine handles the following states:
        
        States:
            0 (Idle/Standby): No active movement, responds to stimuli
            1 (Walking): Moving forward/backward with balance control
            2 (Dancing): Executing dance routines
            3 (Fallen): Handling fall recovery
            4 (Manual Control): Responding to joystick input
            5 (Sleep): Low-power mode with minimal activity
            
        State Transitions:
        - Idle -> Walking: When movement commands are received
        - Any -> Fallen: When IMU detects a fall
        - Fallen -> Previous: After successful recovery
        - Any -> Sleep: After inactivity or low battery
        """
        # Execute the current state's behavior
        self.st_dict.get(self.gst, self.sleep)()
        
        # Handle blinking and state tracking
        if self.gst >= 0:  # If in a normal state
            wk.blink(self.alt_l)  # Update eye blink animation
            self.last_state = self.gst  # Remember last normal state

    # main event loop
    def run(self):
        """
        Main event loop for the robot's operation.
        
        This method runs continuously and handles:
        1. Processing incoming radio commands
        2. Updating robot states based on inputs
        3. Executing the current state's behavior
        4. Handling errors gracefully
        
        The loop runs as fast as possible, with timing controlled by:
        - Hardware PWM timing for servos
        - Delays in state machine methods
        - Radio communication timing
        
        Error Handling:
        - Catches and logs exceptions to prevent crashes
        - Performs garbage collection on error to free memory
        - Continues operation after errors when possible
        """
        while True:
            try:
                # Process any incoming radio commands
                self.process_radio_cmd()
                
                # Update robot states based on current conditions
                self.set_states()
                
                # Execute the current state's behavior
                self.state_machine()
                
                # Optional: Uncomment for memory usage monitoring
                if random.randint(0, 200) == 0: gc.collect()
                # print(time.ticks_ms(), gc.mem_alloc(), gc.mem_free())
                
            except Exception as e:
                # Log errors and attempt to recover
                print(e)
                gc.collect()  # Clean up memory on error
