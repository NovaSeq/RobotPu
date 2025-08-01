from microbit import *
from Parameters import *
import math
import time
import random

WK_ADDR = 0x10

class WK(object):
    def __init__(self):
        self.last_bl_ts = 0
        self.eye_on = True
        self.l_e_b = self.r_e_b = 1023
        self.eye_icr = 1
        self.bl_itl = 6000
        self.pos = self.num_steps = 0
        self.bl_g = 4000
        self.idle =False
        self.c_s = 0
        i2c.init()

    def motor(self, m, sp):
        if -100 <= sp <= 100 and 1 <= m <= 2:
            i2c.write(WK_ADDR, bytearray([m, 0x01, sp, 0]))

    def servo(self, sr, a):
        if 0 <= sr <= 7:
            a = min(180, max(0, int(a)))
            i2c.write(WK_ADDR, bytearray([0x10 if sr == 7 else sr + 3, a, 0, 0]))

    def set_light(self, light):
        i2c.write(WK_ADDR, bytearray([0x12, light, 0, 0]))
        sleep(100)
        i2c.write(WK_ADDR, bytearray([0x11, 160, 0, 0]))

    def servo_step(self, target, sp, idx: int, p:Parameters):
        sp = math.fabs(sp)
        target = max(0, min(179, target))
        err = p.s_err[idx] = target - p.s_tg[idx]
        p.s_tg[idx] += err if math.fabs(err) < sp else sp if err >= 0 else -sp
        self.servo(idx, p.s_tg[idx])

    def servo_move(self, idx: int, p: Parameters):
        for i in range(p.dof):
            self.servo(i, p.st_tg[idx][i] + p.s_tr[i])
        self.idle = True

    def is_servo_idle(self, s_list, p:Parameters):
        self.idle = all(abs(p.s_err[i]) < 1 for i in s_list)
        return self.idle

    def move(self, p:Parameters, states: list[int],
             sync_list: list[int], sp: float,
             async_list: list[int], async_sp: float):
        if sp == 0:
            return 0
        self.pos = min(self.pos, len(states) - 1)
        self.c_s = states[self.pos]
        targets = p.st_tg[self.c_s]
        sps = p.st_sp[self.c_s]
        for i in sync_list:
            self.servo_step(targets[i] + p.s_tr[i] + p.s_ct[i], sp * sps[i], i, p)
        for i in async_list:
            self.servo_step(targets[i] + p.s_tr[i] + p.s_ct[i], async_sp * sps[i], i, p)
        if self.is_servo_idle(sync_list, p):
            self.pos = (self.pos + 1) % len(states)
            self.num_steps += 1
            return 0
        return 1

    def eyes_ctl(self, c):
        pin12.write_digital(c)
        pin13.write_digital(c)
        self.eye_on = c
        self.last_bl_ts = time.ticks_ms()

    def left_eye_bright(self, b):
        pin12.write_analog(b)
        self.l_e_b = b

    def right_eye_bright(self, b):
        pin13.write_analog(b)
        self.r_e_b = b

    def blink(self, alert_l):
        ts_diff = time.ticks_ms() - self.last_bl_ts
        if self.eye_on:
            if ts_diff > self.bl_itl:
                self.eyes_ctl(0)
            else:
                brightness = alert_l * 102
                self.bl_g = alert_l * 400
                self.left_eye_bright(brightness)
                self.right_eye_bright(brightness)
        elif ts_diff > random.randint(100, 250):
            self.eyes_ctl(1)
            if random.randint(0, 4) == 0:
                self.bl_itl = random.randint(100, 250)
            else:
                self.bl_g = int(self.bl_g)
                self.bl_itl = random.randint(self.bl_g, self.bl_g * 2)

    def flash(self, icr: int = 50):
        self.l_e_b += self.eye_icr
        if self.l_e_b >= 1023:
            self.eye_icr = -icr
            self.l_e_b = 1023
        elif self.l_e_b <= 0:
            self.eye_icr = icr
            self.l_e_b = 0
        self.right_eye_bright(1023 - self.l_e_b)
        self.left_eye_bright(self.l_e_b)