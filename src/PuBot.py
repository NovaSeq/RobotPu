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

class RobotPu(object):
    def __init__(self, sn, name="peu"):
        # internal
        self.name = name
        self.sn = sn
        # state machine
        self.st = 0
        # manual ctrl
        self.last_cmd_ts = 0
        self.fw_sp = 4
        self.bw_sp = -3
        self.sp = 0.0
        self.di = 0.0
        self.h_u_bias = 0
        self.h_l_bias = 0
        self.alt_l = 10
        self.alt_sc = 0.9
        self.r_st = 26
        # auto ctrl
        self.bd_pth = 0.0
        self.bd_pth2 = 0.0
        self.bd_rl = 0.0
        self.bd_rl2 = 0.0
        self.pth = 0.0
        self.rl = 0.0
        self.max_g = 1.0
        self.g_thr = 2000
        self.max_pth_ctl = 15.0
        self.max_rl_ctl = 30.0
        self.ep_sp = 0.0
        self.ep_di = 0.0
        self.ep_max_i = 0
        self.ep_thr = 8.5
        self.ep_ot = 0
        self.fell_count = 0
        self.last_state = 0
        self.t_c = 0
        self.l_o_t= 0
        self.r_o_t = 0
        # dance
        self.d_st = [0]
        self.d_dict = {
            14: [0, 15, 15, 0, 3, 5, 3],
            0: [ 0, 19, 0, 18, 0, 3],
            5: [7, 5, 8, 5, 7],
            16: [17, 16, 17, 16, 17]
        }
        self.d_sp = 1.5
        self.last_low_b = 0
        self.last_high_b = 0
        self.dance_l_itv = 15
        self.dance_u_itv = 20
        self.s_list = []

        # radio
        self.groupID = 166
        # mode
        self.walk_m = 0
        # hardware
        self.read_config()
        self.c = Content()
        self.p = Parameters()
        self.music = MusicLib()
        self.sonar = HCSR04()
        self.np = neopixel.NeoPixel(pin16, 4)
        self.set_group(self.groupID)
        self.wk = WK()
        self.wk.eyes_ctl(1)
        self.sound_threshold = 116
        microphone.set_threshold(SoundEvent.LOUD, self.sound_threshold)
        speaker.on()

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

        self.cmd_dict = {
            "#puspeed" : self.speed,
            "#puturn" : self.turn,
            "#puroll" : self.roll,
            "#pupitch" : self.pitch,
            "#puB" : self.button,
            "#pulogo" : self.logo,
            "#purs" : self.pose
        }


    def read_config (self):
        try:
            with open("pu.txt", 'r') as f:
                c = f.read().split('\n')
                self.sn = c[0]
                self.groupID = int(c[1])
                # self.p.s_tr = [float(i) for i in c[1].split(',')]
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

    def set_group(self, g):
        self.groupID = g
        self.display()
        self.ro = MakeRadio(self.groupID)

    def display(self):
        display.show(self.groupID - 160)

    def incr_group_id(self, i):
        self.groupID = (self.groupID + i) % 256
        self.set_group(self.groupID)

    def stand(self):
        self.move([0], [0, 1, 2, 3, 4, 5], 2.0, [], 0.5)

    def intro(self):
        self.talk("My name is " + self.sn + " " + self.name)

    def calibrate(self):
        self.wk.servo_move(25, self.p)
        self.intro()
        for i in range(3):
            self.wk.flash(1020)
            sleep(500)
        self.wk.eyes_ctl(1)
        self.wk.servo_move(0, self.p)
        sleep(2000)

    def fetal(self):
        self.wk.flash()
        if random.randint(0, 200) == 0:
            self.talk("Help me!")
            self.s_code("E1")
        return self.wk.servo_move(1, self.p)

    def set_ct(self, indx_l, v_l):
        le = min(len(indx_l), len(v_l))
        for i in range(le):
            self.p.s_ct[indx_l[i]] = v_l[i]

    def move(self, states: list[int], sync_list: list[int], sp: float, async_list: list[int], async_sp: float):
        return self.wk.move(self.p, states, sync_list, sp, async_list, async_sp)
        # print(self.st, self.wk.pos, self.sp, self.di, self.alert_level, self.max_g,
        #       self.p.s_tg, self.p.s_ct,
        #       [self.rl, self.pth], [self.bd_rl, self.bd_pth], [self.rl_min, self.rl_max, self.rl_mid],
        #       [self.h_l_bias, self.h_u_bias], self.wk.num_steps, self.fell_count,
        #       self.p.ep_dis, [self.ep_sp, self.ep_di, self.ep_max_i],
        #       self.dance_st, self.dance_sp, self.music.period, self.music.loud, self.music.loud_thr
        #       )

    def balance_param(self):
        a = accelerometer.get_values()
        self.pth = math.degrees(math.atan2(a[1], -a[2]))
        self.max_g = math.sqrt(sum(x * x for x in a))
        self.rl = math.degrees(math.asin(a[0] / self.max_g)) if self.max_g > 0 else 0.0
        bd_p = self.pth + (self.p.st_tg[0][5] + self.p.s_tr[5] - self.p.s_tg[5])
        servo_lft = math.radians(self.p.s_tg[4] - self.p.st_tg[0][4] - self.p.s_tr[4])
        self.bd_rl = bd_p * math.sin(servo_lft) + self.rl * math.cos(servo_lft)
        self.bd_rl2 = (self.bd_rl + 9 * self.bd_rl2) * 0.1
        self.bd_pth = bd_p * math.cos(servo_lft) - self.rl * math.sin(servo_lft)
        self.bd_pth2 = (self.bd_pth + 9 * self.bd_pth2) * 0.1

    def rest(self):
        self.balance_param()
        rl = min(35.0, max(-35.0, self.bd_rl2))
        if abs(rl)> 5:
            self.set_ct([0, 1, 2, 3, 4],
                       [rl, rl * -1.0, rl, rl * -1.0, rl * -0.5])
        if math.fabs(self.bd_pth2) > 12:
            self.set_ct([5], [-self.bd_pth2])
        return self.move([self.r_st], [0, 1, 2, 3, 4, 5],
                         1 + microphone.sound_level()*0.01,
                         [], 0.5)

    def move_balance(self, sp: float, di: float, fw_l: list[int], bw_l: list[int]):
        sts = fw_l if sp > 0 else bw_l
        self.balance_param()
        if self.max_g > 2500:
            sp *= 0.6
        if self.wk.pos < 2:  # left side
            self.l_o_t = min(self.max_rl_ctl, max(0.0, (self.rl - self.p.w_t *1.0) * 0.5))
            lf = -16 * di
            self.r_o_t *= 0.99
        else:  # right side
            self.r_o_t = max(-self.max_rl_ctl, min(0.0, (self.rl + self.p.w_t * 1.0) * 0.5))
            lf = 16 * di
            self.l_o_t *= 0.99
        # if self.num_steps > 5 and math.fabs(self.rl_mid < 25):
        #     o_t -= self.rl_mid
        o_t = self.l_o_t+self.r_o_t
        if math.fabs(o_t) > 3:
            sp = sp * 0.2
        self.set_ct([0, 1, 2, 3, 4, 5],
                    [o_t, lf - o_t, o_t, -lf - o_t, -40 * di - o_t, min(25.0, -3.0*self.bd_pth2)])
        return self.move(sts, [0, 1, 2, 3], sp, [4, 5], sp)

    def walk(self, sp, di):
        return self.move_balance(sp, di, self.p.walk_fw_sts, self.p.walk_bw_sts)

    def side_step(self, di):
        sts = [20, 22, 0, 19] if di > 0 else [18, 21, 23, 0]
        self.set_ct([0, 1, 2, 3, 4, 5], [0, 0, 0, 0, 0, 0])
        return self.move(sts, [0, 1, 2, 3], di * self.fw_sp,
                         [4, 5], di * self.fw_sp)

    def set_explore_param(self):
        obs_hcsr = min(self.p.ep_dis[self.p.ep_mid1], self.p.ep_dis[self.p.ep_mid2])
        if obs_hcsr < self.ep_thr + 30:
            max_hcsr, self.ep_max_i = max((dis, i) for i, dis in enumerate(self.p.ep_dis))
            self.ep_di = self.p.ep_dir[self.ep_max_i] + random.uniform(-0.2, 0.2)
        else:
            self.ep_max_i = self.p.ep_mid2 if self.p.ep_dis[self.p.ep_mid2] > self.p.ep_dis[self.p.ep_mid1] else self.p.ep_mid1
            self.ep_di = random.uniform(-0.1, 0) if self.ep_max_i == self.p.ep_mid1 else random.uniform(0, 0.1)
        obs_hcsr = min(self.p.ep_dis)
        dis = (obs_hcsr - self.ep_thr)
        if self.ep_sp < 0:
            dis -= 8 + random.randint(-5, 0)
            self.ep_di = self.ep_di*1.3
            if random.randint(0, 200) == 0:
                self.talk(self.c.sentences[5])
                self.ro.send_str("#puc:" + self.sn + ":W1")
        self.ep_sp = min(self.fw_sp, (dis + 5) * 0.8) if dis >= 0 else max(self.bw_sp, (dis - 4) * 0.3)

    def explore(self):
        a = self.p.s_tg[1 if self.wk.pos < 2 else 3]
        d_i = 0 if a > 110 else 1 if a > 90 else 2 if a > 70 else 3
        self.p.ep_dis[d_i] = (self.p.ep_dis[d_i] + self.sonar.distance_cm()) * 0.5
        self.set_explore_param()
        return self.walk(self.ep_sp, self.ep_di)

    def random_light(self):
        for p in range(0, 4):
            self.np[p] = (random.randint(0, 128), random.randint(0, 128), random.randint(0, 128))
        self.np.show()

    def dance(self):
        ts = time.ticks_ms()
        il = self.music.is_a_beat(ts, microphone.sound_level(), 1.05)
        if ts - self.last_high_b > self.music.period * 0.5:
            self.dance_l_itv *= -1
            self.dance_u_itv *= -1
            self.random_light()
            self.last_high_b = ts
        if il and ts - self.last_low_b > self.music.period * random.randint(8, 16):
            self.d_st = self.d_dict.get(self.d_st[-1], [random.choice(self.p.dance_ok)])
            self.last_low_b = ts
        self.balance_param()
        ft = min(15.0, max(-15.0, self.rl * 0.3 + self.dance_l_itv * 0.2))
        lt = self.rl * -0.3 + self.dance_l_itv
        self.set_ct([0, 1, 2, 3, 4, 5], [ft, lt, ft, lt, self.rl * -0.6, self.dance_u_itv])
        self.d_sp = min(2.5, self.d_sp * 1.015)
        if self.max_g > 1800:
            self.d_sp *= 0.9
        return self.move(self.d_st, [0, 1, 2, 3], self.d_sp, [4, 5], self.d_sp)

    def jump(self):
        md = self.move([24, 14, 0, 0], [0, 1, 2, 3], 3, [4, 5], 2)
        if md == 0 and self.wk.pos == 3:
            self.st = 5

    def kick(self):
        md = self.move(self.p.walk_fw_sts, [0, 1, 2, 3], 3, [4, 5], 2)
        if md == 0 and (self.wk.pos == 0 or self.wk.pos == 2):
            self.st = 5

    def talk(self, t):
        speech.say(t, speed=90, pitch=35, throat=225, mouth=225)

    def sing(self, s):
        speech.sing(s, speed=90, pitch=35, throat=225, mouth=225)

    def idle(self):
        if random.randint(0, 100) == 0:
            # decrease alert level to sleep
            self.alt_l *= self.alt_sc
        self.check_wakeup()
        self.sound_threshold = (self.sound_threshold*24 + microphone.sound_level()) * 0.04
        if self.rest() == 0:
            if random.randint(0, 1000) == 0:
                self.alt_l -= 2
                self.state_talk()
                self.ro.send_str("#puhi, " + self.sn + " " + self.name)
            if random.randint(0, 280-microphone.sound_level()) == 0 or microphone.sound_level()> self.sound_threshold*3:
                self.p.st_tg[26][4] = random.randint(30, 160) #min(160, max(20, self.p.st_tg[26][4]+random.randint(-10, 10)))
                self.p.st_tg[26][5] = random.randint(40, 105) #min(115, max(30, self.p.st_tg[26][5]+random.randint(-10, 10)))


    def sleep(self):
        self.balance_param()
        self.stand()
        self.wk.eyes_ctl(0)
        self.np.clear()
        if self.check_wakeup() == 1:
            self.st = 0

    def fall(self):
        self.wk.flash()
        display.show(self.wk.c_s)
        if random.randint(0, 500) == 0:
            self.talk("Help me stand up!")
            self.s_code("E2")

    def joystick(self):
        if self.sp == 0:
            self.wk.servo_step(90 + self.h_l_bias, 1, 4, self.p)
            self.wk.servo_step(90 + self.h_u_bias, 1, 5, self.p)
            if math.fabs(self.di) > 0.9:
                self.side_step(self.di)
        else:
            self.walk(self.sp, self.di)

    def check_wakeup(self):
        # wake up if there is noise and tilt
        if (self.max_g > self.g_thr or microphone.current_event() == SoundEvent.LOUD
                or math.fabs(self.bd_rl - self.bd_rl2) > 20 or math.fabs(self.bd_pth - self.bd_pth2) > 20):
            self.alt_l = 10
            return 1
        if self.alt_l < 1:
            self.st = -1
        return 0

    def state_talk(self):
        rt = random.randint(0, 5)
        if rt == 0:
            self.sing(self.c.compose_song())
        else:
            self.talk(random.choice(["Hello! I am " + self.sn + " " + self.name + ". ",
                                     self.c.cute_words(),
                                     random.choice(self.c.sentences),
                                     "Temperature is " + str(temperature()) + " degree.",
                                     "I ran " + str(self.wk.num_steps) + " steps today!"
                                     ]))

    def noop(self, v):
        pass

    def speed (self, v:float):
        if v > 0.2:
            self.sp = v * self.fw_sp
            self.st = 5
        elif v < -0.2:
            self.sp = -v * self.bw_sp
            self.st = 5
        else:
            self.sp = 0
            
    def turn(self, v:float):
        self.di = (self.di + v) * 0.5
    
    def roll(self, v:float):
        self.h_l_bias = (v + self.h_l_bias) * 0.5
        
    def pitch(self, v:float):
        self.h_u_bias = (v * -1 + self.h_u_bias) * 0.5
        
    def button(self, v:int):
        if v == 0:
            self.st = 0
            self.h_u_bias = 0
            self.h_l_bias = 0
            self.talk("Rest!")
            self.ro.send_str("#puack")
        elif v == 1:
            self.talk("Exploring")
            self.ep_sp = 3.0
            self.ep_di = 0.0
            self.st = 1
        elif v == 2:
            self.st = 2
        elif v == 3:
            self.talk("Dance!")
            self.d_sp = 1.5
            self.st = 3
        elif v == 4:
            # self.talk("Kick!")
            self.st = 4

    def logo (self, v):
        self.state_talk()
        
    def pose (self, v:int):
        self.r_st = v
        self.st = 0
        self.rest()

    def s_code(self, code):
        self.ro.send_str(":".join(["#puc", self.sn, code]))

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
            elif d.startswith("#puhi") and self.st == 0 and random.randint(0, 3) == 0:
                self.talk("My friend " + d[5:] + " is here")
            elif d.startswith("#pun"):
                self.sn = d[4:]
                self.intro()
                #self.write_config()
        #else if type(d) is int or type(d) is float:
        #    pass

    def set_states(self):
        if accelerometer.was_gesture("freefall"):
            # falling
            self.st = -2
        if button_a.was_pressed():
            self.incr_group_id(1)
            #self.write_config()
        if button_b.was_pressed():
            self.incr_group_id(-1)
            #self.write_config()
        if self.st > 0:
            self.alt_l = 10
            if time.ticks_ms() - self.last_cmd_ts > 2000:
                # resting
                self.st = 0

    def state_machine(self):
        if self.st != -2:
            if math.fabs(self.bd_rl2) > 75 or math.fabs(self.bd_pth2) > 75:
                self.balance_param()
                self.fell_count += 1
                self.wk.num_steps = 0
                if self.fell_count > 16:
                    self.st = -3
            else:
                self.fell_count = 0
                if self.st == -3:
                    self.st = self.last_state
                    self.talk("Thanks")
                    self.display()
        # actions
        self.st_dict.get(self.st, self.sleep)()
        #display.show(self.st)
        if self.st >= 0:
            self.wk.blink(self.alt_l)
            self.last_state = self.st
