from microbit import *
import ustruct
import radio


class MakeRadio:
    def __init__(self, g, power=6, queue=3, chan=7):
        radio.config(
            group=g, data_rate=radio.RATE_1MBIT, channel=chan, power=power, queue=queue
        )
        radio.on()
        self.dal_header = b"\x01" + g.to_bytes(1, "little") + b"\x01"
        radio.off()
        radio.on()

    def send_str(self, s):
        ts = running_time().to_bytes(4, "little")
        sn = int(0).to_bytes(4, "little")
        nb = bytes(s, "utf8")
        nl = len(nb).to_bytes(1, "little")
        r_b = self.dal_header + int(2).to_bytes(1, "little") + ts + sn + nl + nb
        radio.send_bytes(r_b)

    def send_value(self, name, value):
        if len(name) > 8:
            name = name[:8]
        ts = running_time().to_bytes(4, "little")
        sn = int(0).to_bytes(4, "little")
        if  isinstance(value, int) and -2147483648 <= value <= 2147483647:
            n = int(value).to_bytes(4, "little")
            packet_type = int(1).to_bytes(1, "little")
        else:
            n = ustruct.pack("<d", value)
            packet_type = int(5).to_bytes(1, "little")

        nb = bytes(str(name), "utf8")
        nl = len(nb).to_bytes(1, "little")
        raw_bytes = self.dal_header + packet_type + ts + sn + n + nl + nb
        radio.send_bytes(raw_bytes)

    def receive_packet(self):
        d = radio.receive_bytes()
        return self._parse_packet(d)

    def _parse_packet(self, d):
        if d is None:
            return None
        if d[:3] != self.dal_header:
            pass
        p_t = int.from_bytes(d[3:4], "little")
        if p_t == 5:  # value with float
            float_ = ustruct.unpack("<d", d[12:20])[0]
            name = str(d[21:min(len(d), 29)], "ascii").rstrip("\x00")
            return (name, float_)
        elif p_t == 2:  # string
            return str(d[13:], "utf8").rstrip("\x00")
        elif p_t == 0:  # number
            return ustruct.unpack("<i", d[-4:])[0]
        elif p_t == 1:  # value
            value = ustruct.unpack("<i", d[12:16])[0]
            return (str(d[17:], "utf8").rstrip("\x00"), value)
        elif p_t == 4:  # floating point number
            return ustruct.unpack("<d", d[-8:])[0]
        return None

