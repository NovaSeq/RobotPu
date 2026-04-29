import sensor
import image
import time
import uos
import sys
import gc
import pyb
import machine
from pyb import UART

sensor.reset()
sensor.set_pixformat(sensor.GRAYSCALE)
sensor.set_framesize(sensor.QQQVGA)
sensor.skip_frames(time=2000)
sensor.set_auto_gain(False)
sensor.set_auto_whitebal(False)

clock = time.clock()

uart = UART(3, 115200, timeout_char=50)

led_r = pyb.LED(1)
led_g = pyb.LED(2)
led_b = pyb.LED(3)
led_r.off()
led_g.off()
led_b.off()

USE_UART = False


def _uart_write_safe(s):
    if not USE_UART:
        return False
    try:
        uart.write(s)
        return True
    except Exception as e:
        print("uart write failed:", e)
        return False

print("boot:", sys.platform)
try:
    print("impl:", sys.implementation.name, sys.implementation.version)
except Exception as e:
    print("impl print failed:", e)
time.sleep_ms(100)
try:
    print("listing files...")
    print("files:", uos.listdir())
except Exception as e:
    print("listdir failed:", e)
time.sleep_ms(100)


def _first_existing_path(paths):
    for p in paths:
        try:
            uos.stat(p)
            return p
        except OSError:
            pass
    return None


def _clamp(v, lo, hi):
    if v < lo:
        return lo
    if v > hi:
        return hi
    return v


_cascade_path = "frontalface.cascade"
try:
    if _cascade_path not in uos.listdir():
        raise RuntimeError("Could not find 'frontalface.cascade' in the OpenMV filesystem root")
except Exception as e:
    print("cascade file check failed:", e)
    sys.print_exception(e)
    time.sleep_ms(2000)
    raise

try:
    f = open(_cascade_path, "rb")
    head = f.read(16)
    f.close()
    print("cascade head:", head)
except Exception as e:
    print("cascade file read failed:", e)
    sys.print_exception(e)
    time.sleep_ms(2000)
    raise

try:
    print("loading cascade:", _cascade_path)
    time.sleep_ms(100)
    gc.collect()
    print("mem_free before cascade:", gc.mem_free())
    led_b.on()
    try:
        face_cascade = image.HaarCascade(_cascade_path, stages=5)
    except Exception:
        face_cascade = image.HaarCascade(_cascade_path, stages=5)
    led_b.off()
    gc.collect()
    print("mem_after:", gc.mem_free())
    time.sleep_ms(100)
    print("cascade loaded")
    time.sleep_ms(100)
except Exception as e:
    led_b.off()
    led_r.on()
    print("cascade load failed:", e)
    sys.print_exception(e)
    try:
        uart.write("E,CASCADE," + str(e) + "\n")
    except Exception:
        pass
    time.sleep_ms(2000)
    raise

led_g.on()
print("after cascade")
time.sleep_ms(500)

try:
    wdt = machine.WDT(timeout=4000)
except Exception:
    wdt = None

print("start main loop")
frame_i = 0
last_faces_n = 0

MIN_FACE_AREA = 150
MAX_FACES = 3
DETECT_EVERY_N = 10
DETECT_THRESHOLD = 0.7
DETECT_SCALE = 1.5
DETECT_START_FRAME = 30

last_kept = []
while True:
    try:
        frame_i += 1
        if wdt:
            try:
                wdt.feed()
            except Exception:
                pass
        if frame_i == 1:
            print("loop started")
            print("mem0:", gc.mem_free())
            time.sleep_ms(200)
        if (frame_i % 5) == 0:
            gc.collect()
        if (frame_i % 10) == 0:
            led_g.toggle()
        clock.tick()

        if (frame_i % 30) == 0:
            try:
                gc.collect()
                m = gc.mem_free()
                t = pyb.millis()
                print("hb", frame_i, t, m, last_faces_n)
                led_r.toggle()
            except Exception as e:
                print("hb_pre print failed:", e)
            _uart_write_safe("HB,%d,%d\n" % (frame_i, last_faces_n))

        step = "pre_snapshot"
        if frame_i <= 2:
            print("ps:", frame_i, "m:", gc.mem_free())
            time.sleep_ms(100)
        step = "snapshot"
        led_b.on()
        if (frame_i % 30) == 0:
            print("ss", frame_i)
        img = sensor.snapshot()
        if wdt:
            try:
                wdt.feed()
            except Exception:
                pass
        if (frame_i % 30) == 0:
            print("se", frame_i)
        led_b.off()
        if frame_i <= 2:
            print("sn:", frame_i, "m:", gc.mem_free())
            time.sleep_ms(100)

        if frame_i == 1:
            time.sleep_ms(200)

        kept = last_kept
        if (frame_i >= DETECT_START_FRAME) and ((frame_i % DETECT_EVERY_N) == 0):
            step = "find_features"
            try:
                gc.collect()
            except Exception:
                pass
            roi = (sensor.width() // 6, sensor.height() // 6, (sensor.width() * 2) // 3, (sensor.height() * 2) // 3)
            led_b.on()
            print("ff_s:", frame_i, "m:", gc.mem_free())
            faces = img.find_features(face_cascade, threshold=DETECT_THRESHOLD, scale=DETECT_SCALE, roi=roi)
            print("ff_e:", frame_i, "m:", gc.mem_free())
            led_b.off()
            try:
                print("detect:", frame_i, "raw:", 0 if not faces else len(faces), "mem_free:", gc.mem_free())
            except Exception:
                pass

            if faces:
                try:
                    print("rects:", faces[:3])
                except Exception:
                    pass

            kept = []
            if faces:
                for r in faces:
                    x, y, w, h = r
                    score = w * h
                    if score < MIN_FACE_AREA:
                        continue
                    cx = x + (w // 2)
                    cy = y + (h // 2)
                    kept.append((score, cx, cy))

            if kept:
                kept.sort(reverse=True)
                kept = kept[:MAX_FACES]

            last_kept = kept

        last_faces_n = len(kept)

        if (frame_i % 5) == 0:
            gc.collect()

        if not kept:
            step = "uart_no_face"
            if (frame_i % 5) == 0:
                _uart_write_safe("N,0\n")
            continue

        out = ["F", str(len(kept))]

        bs, bx, by = kept[0]
        for score, cx, cy in kept:
            out.append("%d,%d,%d" % (cx, cy, score))

        bx = _clamp(bx, 0, sensor.width() - 1)
        by = _clamp(by, 0, sensor.height() - 1)

        line = ",".join(out[0:2]) + "," + str(bx) + "," + str(by) + "," + str(bs)

        if len(out) > 2:
            line += ";" + ";".join(out[2:])

        step = "uart_face"
        _uart_write_safe(line + "\n")
        if (frame_i % 5) == 0:
            gc.collect()
        step = "end"
    except Exception as e:
        if isinstance(e, MemoryError):
            print("loop MemoryError at", frame_i, "step:", step, "mem_free:", gc.mem_free())
            sys.print_exception(e)
            try:
                uart.write("E,MEM,%d,%s\n" % (frame_i, step))
            except Exception:
                pass
            gc.collect()
            time.sleep_ms(50)
            continue
        print("loop crashed at", frame_i, "step:", step, "mem_free:", gc.mem_free(), "err:", e)
        sys.print_exception(e)
        try:
            uart.write("E,LOOP,%d,%s,%s\n" % (frame_i, step, str(e)))
        except Exception:
            pass
        time.sleep_ms(2000)
        raise
