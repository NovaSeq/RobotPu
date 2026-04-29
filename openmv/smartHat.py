import sensor
import image
import time
import uos
import sys
from pyb import UART

sensor.reset()
sensor.set_pixformat(sensor.GRAYSCALE)
sensor.set_framesize(sensor.QVGA)
sensor.skip_frames(time=2000)
sensor.set_auto_gain(False)
sensor.set_auto_whitebal(False)

clock = time.clock()

uart = UART(3, 115200, timeout_char=50)

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


_cascade_path = _first_existing_path(("frontalface.cascade", "/frontalface.cascade"))
if not _cascade_path:
    raise RuntimeError("Could not find 'frontalface.cascade' in the OpenMV filesystem root")

try:
    print("loading cascade:", _cascade_path)
    face_cascade = image.HaarCascade(_cascade_path, stages=25)
    print("cascade loaded")
except Exception as e:
    print("cascade load failed:", e)
    sys.print_exception(e)
    try:
        uart.write("E,CASCADE," + str(e) + "\n")
    except Exception:
        pass
    raise


def _clamp(v, lo, hi):
    if v < lo:
        return lo
    if v > hi:
        return hi
    return v


while True:
    try:
        clock.tick()
        img = sensor.snapshot()

        faces = img.find_features(face_cascade, threshold=0.65, scale=1.25)

        if not faces:
            uart.write("N,0\n")
            continue

        best = None
        best_score = -1

        out = ["F", str(len(faces))]

        for r in faces:
            x, y, w, h = r
            cx = x + (w // 2)
            cy = y + (h // 2)

            score = w * h
            if score > best_score:
                best_score = score
                best = (cx, cy, score)

            out.append("%d,%d,%d" % (cx, cy, score))

        bx, by, bs = best
        bx = _clamp(bx, 0, sensor.width() - 1)
        by = _clamp(by, 0, sensor.height() - 1)

        line = ",".join(out[0:2]) + "," + str(bx) + "," + str(by) + "," + str(bs)

        if len(out) > 2:
            line += ";" + ";".join(out[2:])

        uart.write(line + "\n")
    except Exception as e:
        print("loop crashed:", e)
        sys.print_exception(e)
        try:
            uart.write("E,LOOP," + str(e) + "\n")
        except Exception:
            pass
        raise
