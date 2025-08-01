from microbit import *
from PuBot import *
import time
import gc

r = RobotPu("Peu")
# r.p.s_tr[0]= -9
# r.p.s_tr[1]= -9
# r.p.s_tr[2]= -9
# r.p.s_tr[3]= -9
# r.p.s_tr[4]= -9
# r.p.s_tr[5]= 0
r.calibrate()

while True:
    try:
        r.process_radio_cmd()
        r.set_states()
        r.state_machine()
        #gc.collect()
        #print(time.ticks_ms(), gc.mem_alloc(), gc.mem_free())
    except Exception as e:
       print(e)
       gc.collect()
