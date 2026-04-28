import sensor
import image
import time
from pyb import UART

sensor.reset()
sensor.set_pixformat(sensor.GRAYSCALE)
sensor.set_framesize(sensor.QVGA)
sensor.skip_frames(time=2000)
sensor.set_auto_gain(False)
sensor.set_auto_whitebal(False)

clock = time.clock()

uart = UART(3, 115200, timeout_char=50)

face_cascade = image.HaarCascade("frontalface", stages=25)


def _clamp(v, lo, hi):
    if v < lo:
        return lo
    if v > hi:
        return hi
    return v


while True:
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
