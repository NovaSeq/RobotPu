from microbit import *
from machine import time_pulse_us
from utime import sleep_us


class HCSR04:
    def __init__(self, timeout_us=500 * 2 * 30):
        self.timeout_us = timeout_us
        pin2.write_digital(0)
        pin8.read_digital()

    def distance_cm(self):
        pin2.write_digital(0)
        sleep_us(5)
        pin2.write_digital(1)
        sleep_us(10)
        pin2.write_digital(0)
        t = time_pulse_us(pin8, 1, self.timeout_us)
        if t < 0:
            t = 500
        sleep_us(5)
        return t * 0.0171821

