import sensor
import image
import time
import gc
import uos
import sys
import machine
from pyb import UART

sensor.reset()
sensor.set_pixformat(sensor.GRAYSCALE)
sensor.set_framesize(sensor.QQQVGA)
sensor.skip_frames(time=1000)
sensor.set_auto_gain(False)
sensor.set_auto_whitebal(False)

try:
    wdt = machine.WDT(timeout=10000)
except:
    wdt = None

def feed_wdt():
    if wdt:
        try:
            wdt.feed()
        except:
            pass

try:
    uart = UART(3, 115200)
except Exception as e:
    print("UART init failed:", e)
    uart = None


def uart_write(msg):
    if uart:
        try:
            uart.write(msg + "\n")
        except Exception:
            pass


CRASH_LOG = "crash.txt"

def log_step(s):
    try:
        f = open(CRASH_LOG, "w")
        f.write(s)
        f.close()
    except:
        pass

try:
    f = open(CRASH_LOG, "r")
    last = f.read()
    f.close()
    print("LAST CRASH STEP:", last)
except:
    print("no crash log")

if "frontalface.cascade" not in uos.listdir():
    raise RuntimeError("Missing frontalface.cascade file")

try:
    gc.collect()
    print("mem before cascade:", gc.mem_free())
    face_cascade = image.HaarCascade("/rom/frontalface.cascade", stages=25)
    try:
        face_cascade = image.HaarCascade("frontalface", stages=25)
        print("using built-in cascade")
    except:
        face_cascade = image.HaarCascade("frontalface.cascade", stages=14)
        print("using file cascade")
    gc.collect()
    print("cascade loaded, mem after:", gc.mem_free())
except Exception as e:
    print("cascade load error:", e)
    raise

MAX_FACES = 3
MIN_AREA = 100
FRAME_DELAY_MS = 100
DETECT_EVERY = 10

snap_fail = 0
frame_i = 0
while True:
    try:
        frame_i += 1
        feed_wdt()
        print("snap")
        try:
            img = sensor.snapshot()
        except Exception as e:
            snap_fail += 1
            print("snap failed:", snap_fail, e)
            time.sleep_ms(200)
            continue

        snap_fail = 0

        if frame_i % DETECT_EVERY != 0:
            gc.collect()
            time.sleep_ms(FRAME_DELAY_MS)
            continue

        feed_wdt()
        gc.collect()
        print("detect")
        try:
            print("find_features start", gc.mem_free())
            log_step("before_find_features f=%d" % gc.mem_free())
            feed_wdt()
            w = sensor.width()
            h = sensor.height()
            roi = (0, 0, w, h)
            gc.collect()
            time.sleep_ms(100)
            feed_wdt()
            log_step("calling_find_features f=%d" % gc.mem_free())
            faces = img.find_features(face_cascade, threshold=0.8, scale=2.0, roi=roi)
            log_step("find_features_returned n=%d f=%d" % (len(faces), gc.mem_free()))
            feed_wdt()
            print("find_features done, found:", len(faces))
            kept = []
            if faces:
                print("sort")
                for (x, y, w, h) in faces:
                    area = w * h
                    if area >= MIN_AREA:
                        kept.append((area, x + w // 2, y + h // 2))

            if kept:
                print("filter")
                kept.sort(reverse=True)
                kept = kept[:MAX_FACES]
                msg = "F,%d" % len(kept)
                for (area, cx, cy) in kept:
                    msg += ",%d,%d,%d" % (cx, cy, area)
                print(msg)
                uart_write(msg)
            feed_wdt()
        except BaseException as e:
            print("find_features error:", e)
            faces = []

        feed_wdt()
        gc.collect()
        print("mem:", gc.mem_free())
        time.sleep_ms(FRAME_DELAY_MS)

    except Exception as e:
        print("err:", e)
        sys.print_exception(e)
        gc.collect()
        time.sleep_ms(200)
