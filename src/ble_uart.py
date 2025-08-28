from microbit import *
import ubluetooth as bt
from ubluetooth import FLAG_NOTIFY as FN, FLAG_READ as FR, FLAG_WRITE as FW

_ICON = 1  # _IRQ_CENTRAL_CONNECT
_IDC = 2   # _IRQ_CENTRAL_DISCONNECT
_IGW = 3   # _IRQ_GATTS_WRITE

class BLEUART:
    def __init__(self, name='RobotPu', cb= None):
        self.b = bluetooth
        self.b.active(1)
        self.su = '6E400001-B5A3-F393-E0A9-E50E24DCCA9E'
        self.tu = '6E400003-B5A3-F393-E0A9-E50E24DCCA9E'
        self.ru = '6E400002-B5A3-F393-E0A9-E50E24DCCA9E'
        self.ch = None
        self._setup()
        self._adv()
        self.rb = bytearray()
        self.n = name  
        self.cb = cb # callback function of data received

    def _setup(self):
        su = bt.UUID(self.su)
        ru = bt.UUID(self.ru)
        tu = bt.UUID(self.tu)
        rx = (ru, FW)
        tx = (tu, FN | FR)
        svc = (su, (tx, rx))
        (self.th, self.rh), = self.b.gatts_register_services((svc,))
        self.b.gatts_set_buffer(self.th, 512, 1)
        self.b.gatts_set_buffer(self.rh, 512, 1)
        self.b.irq(self._irq)

    def _adv(self):
        self.b.gap_advertise(100, b'\x02\x01\x06' + bytes([len(self.n) + 1, 0x09]) + self.n.encode())

    def _irq(self, e, d):
        if e == _ICON:  # Connected
            self.ch = d[0]
        elif e == _IDC:  # Disconnected
            if self.ch == d[0]:
                self.ch = None
            self._adv()
        elif e == _IGW and d[0] == self.ch and d[1] == self.rh:  # Data received
            self.rb += self.b.gatts_read(self.rh)
            if self.cb:
                self.cb()

    def write(self, d):
        if self.ch:
            for i in range(0, len(d), 20):
                self.b.gatts_notify(self.ch, self.th, d[i:i+20])

    def read(self, n=None):
        n = n or len(self.rb)
        d, self.rb = self.rb[:n], self.rb[n:]
        return d

    def any(self): 
        return len(self.rb)

    def close(self):
        if self.ch:
            self.b.gap_disconnect(self.ch)
            self.ch = None
        self.b.active(0)

    def __enter__(self): 
        return self
        
    def __exit__(self, *a): 
        self.close()