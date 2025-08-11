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
        self.fw_sp = 4            # Forward speed multiplier
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
    def read_config (self):
        try:
            with open("pu.txt", 'r') as f:
                c = f.read().split('\n')
                self.sn = c[0]
                self.groupID = int(c[1])
                pr.s_tr = [float(i) for i in c[2].split(',')]
        except: pass

    #
    # def write_config (self):
    #     try:
    #         os.remove('pu.txt')
    #     except:
    #         print("pu.txt not found")
    #     #try:
    #     with open("pu.txt", 'w') as f:
    #         f.write(self.sn + "\n")
    #         f.write(str(self.groupID) + "\n")
    #         # f.write(','.join([str(i) for i in self.p.s_tr]))
    #     #except: pass
    #
    # def sync_config(self):
    #     try:
    #         self.read_config()
    #     except Exception as e:
    #         self.write_config()

    # set radio channel
    def set_group(self, g):
        self.groupID = g
        self.show_channel()
        self.ro = MakeRadio(self.groupID)

    # show radio channel on the microbit display
    def show_channel(self):
        display.show(self.groupID - 160)

    # increment radio channel
    def incr_group_id(self, i):
        self.groupID = (self.groupID + i) % 256
        self.set_group(self.groupID)

    # make the robot stand up
    def stand(self):
        self.move([0], [0, 1, 2, 3, 4, 5], 2.0, [], 0.5)

    # make the robot introduce itself
    def intro(self):
        self.talk("My name is " + self.sn + " " + self.name)

    # calibrate the robot
    def calibrate(self):
        wk.servo_move(25, pr)
        self.intro()
        for i in range(3):
            wk.flash(1020)
            sleep(500)
        wk.eyes_ctl(1)
        wk.servo_move(0, pr)
        sleep(2000)

    # make the robot fetal position
    def fetal(self):
        wk.flash()
        if random.randint(0, 200) == 0:
            self.talk("Help me!")
            self.s_code("E1")
        return wk.servo_move(1, pr)

    # set servo control vector, the final taget = current vector + control vector + trim vector
    def set_ct(self, indx_l, v_l):
        le = min(len(indx_l), len(v_l))
        for i in range(le):
            pr.s_ct[indx_l[i]] = v_l[i]

    # make the robot loop through the given states  
    def move(self, states: list[int], sync_list: list[int], sp: float, async_list: list[int], async_sp: float):
        return wk.move(pr, states, sync_list, sp, async_list, async_sp)
        # print(self.st, wk.pos, self.sp, self.di, self.alert_level, self.max_g,
        #       self.p.s_tg, self.p.s_ct,
        #       [self.rl, self.pth], [self.bd_rl, self.bd_pth], [self.rl_min, self.rl_max, self.rl_mid],
        #       [self.h_l_bias, self.h_u_bias], wk.num_steps, self.fell_count,
        #       self.p.ep_dis, [self.ep_sp, self.ep_di, self.ep_max_i],
        #       self.dance_st, self.dance_sp, self.music.period, self.music.loud, self.music.loud_thr
        #       )

    # calculate postion balance parameters
    def balance_param(self):
        a = accelerometer.get_values()
        self.pth = math.degrees(math.atan2(a[1], -a[2]))
        self.max_g = math.sqrt(sum(x * x for x in a))
        self.rl = math.degrees(math.asin(a[0] / self.max_g)) if self.max_g > 0 else 0.0
        bd_p = self.pth + (pr.st_tg[0][5] + pr.s_tr[5] - pr.s_tg[5])
        servo_lft = math.radians(pr.s_tg[4] - pr.st_tg[0][4] - pr.s_tr[4])
        self.bd_rl = bd_p * math.sin(servo_lft) + self.rl * math.cos(servo_lft)
        self.bd_rl2 = (self.bd_rl + 9 * self.bd_rl2) * 0.1
        self.bd_pth = bd_p * math.cos(servo_lft) - self.rl * math.sin(servo_lft)
        self.bd_pth2 = (self.bd_pth + 9 * self.bd_pth2) * 0.1

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

    # make the robot move with self-balance
    def move_balance(self, sp: float, di: float, fw_l: list[int], bw_l: list[int]):
        sts = fw_l if sp > 0 else bw_l
        self.balance_param()
        if self.max_g > 2500:
            sp *= 0.6
        if wk.pos < 2 or wk.pos == 6:  # left side
            self.l_o_t = min(self.max_rl_ctl, max(0.0, self.bd_rl*0.8 - pr.w_t))
            lf = -15 * di
        else:  # right side
            self.r_o_t = max(-self.max_rl_ctl, min(0.0, self.bd_rl*0.8 + pr.w_t))
            lf = 15 * di
        #self.r_o_t *= 0.995
        #self.l_o_t *= 0.995
        o_t = self.l_o_t+self.r_o_t
        sp = sp /(1+math.sqrt(math.fabs(o_t*0.5)))
        self.set_ct([0, 1, 2, 3, 4, 5],
                    [o_t, lf - o_t, o_t, -lf - o_t, -40 * di - o_t, min(25.0, -2.0*self.bd_pth2)])
        return self.move(sts, [0, 1, 2, 3], sp, [4, 5], sp)
    # make the robot walk with self-balance
    def walk(self, sp, di):
        return self.move_balance(sp, di, pr.walk_fw_sts, pr.walk_bw_sts)

    # make the robot side step with self-balance    
    def side_step(self, di):
        sts = [20, 22, 0, 19] if di > 0 else [18, 21, 23, 0]
        self.set_ct([0, 1, 2, 3, 4, 5], [0, 0, 0, 0, 0, 0])
        return self.move(sts, [0, 1, 2, 3], di * self.fw_sp,
                         [4, 5], di * self.fw_sp)
    # compute auto-pilot parameters for explore mode
    def set_explore_param(self):
        obs_hcsr = min(pr.ep_dis[pr.ep_mid1], pr.ep_dis[pr.ep_mid2])
        if obs_hcsr < self.ep_thr + 15:
            max_hcsr, self.ep_max_i = max((dis, i) for i, dis in enumerate(pr.ep_dis))
            self.ep_di = pr.ep_dir[self.ep_max_i] + random.uniform(-0.2, 0.2)
        else:
            self.ep_di = min(1.0, max(-1.0, (pr.ep_dis[pr.ep_mid2] - pr.ep_dis[pr.ep_mid1]) / (pr.ep_dis[pr.ep_mid2] + pr.ep_dis[pr.ep_mid1]) * 1.5))
        obs_hcsr = min(pr.ep_dis)
        dis = (obs_hcsr - self.ep_thr)
        if self.ep_sp < 0:
            dis -= 12 + random.randint(-5, 0)
            if random.randint(0, 400) == 0:
                self.talk(self.c.sentences[5])
                self.ro.send_str("#puc:" + self.sn + ":W1")
        self.ep_sp = min(self.fw_sp, (dis + 5) * 0.8) if dis >= 0 else max(self.bw_sp, (dis - 4) * 0.3)

    # make the robot explore with self-balance
    def explore(self):
        a = pr.s_tg[1 if wk.pos < 2 else 3]
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
        self.di = (self.di + v) * 0.5

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
            self.ep_sp = 3.0
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
        d = self.ro.receive_packet()
        if d is None:
            return
        if isinstance(d, tuple):
            self.last_cmd_ts = time.ticks_ms()
            la, v = d
            self.cmd_dict.get(la, self.noop)(v)
        elif type(d) is str:
            if d.startswith("#put"):
                self.talk(d[4:])
                # self.p.st_tg[26][4] = random.randint(30,160)
                # self.p.st_tg[26][5] = random.randint(30, 90)
            elif d.startswith("#pus"):
                self.s_list.append(d[4:])
                #print(''.join(self.s_list))
                if len(self.s_list) >= 6:
                    self.sing(''.join(self.s_list))
                    self.s_list = []
            elif d.startswith("#puhi") and self.gst == 0 and random.randint(0, 3) == 0:
                self.talk("My friend " + d[5:] + " is here")
            elif d.startswith("#pun"):
                self.sn = d[4:]
                self.intro()
                #self.write_config()
        #else if type(d) is int or type(d) is float:
        #    pass

    # set robot states based on sensor inputs   
    def set_states(self):
        #wk.servo(6, microphone.sound_level()*2)
        if accelerometer.was_gesture("freefall"):
            # falling
            self.gst = -2
        if button_a.was_pressed():
            self.incr_group_id(1)
            #self.write_config()
        if button_b.was_pressed():
            self.incr_group_id(-1)
            #self.write_config()
        if self.gst > 0:
            self.alt_l = 10
            if time.ticks_ms() - self.last_cmd_ts > 2000:
                # resting
                self.gst = 0
        if self.gst != -2:
            if math.fabs(self.bd_rl2) > 75 or math.fabs(self.bd_pth2) > 75:
                self.balance_param()
                self.fell_count += 1
                wk.num_steps = 0
                if self.fell_count > 16:
                    self.gst = -3
            else:
                self.fell_count = 0
                if self.gst == -3:
                    self.gst = self.last_state
                    self.talk("Thanks")
                    self.show_channel()

    # state machine
    def state_machine(self):
        # actions
        self.st_dict.get(self.gst, self.sleep)()
        # blink
        if self.gst >= 0:
            wk.blink(self.alt_l)
            self.last_state = self.gst
            
    # main event loop
    def run(self):
        while True:
            try:
                self.process_radio_cmd()
                self.set_states()
                self.state_machine()
                # gc.collect()
                # print(time.ticks_ms(), gc.mem_alloc(), gc.mem_free())
            except Exception as e:
                print(e)
                gc.collect()
