def ring_buffer_idx(m, icr, size):
    return (m + icr) % size

class MusicLib(object):
    def __init__(self):
        self.loud_thr = 15
        self.loud = 0
        self.loud_buf_size = 21
        self.loud_buf = [0] * self.loud_buf_size
        self.last_loud_idx = 0
        self.music_ts = 0
        self.period = 500
        self.hits = 0

    def is_a_beat(self, timestamp, loudness, snr: float, sample_ms=125):
        self.loud = loudness
        is_a_beat = False
        idx = (timestamp // sample_ms) % self.loud_buf_size
        if idx == self.last_loud_idx:
            self.hits += 1
            self.loud_buf[idx] = (self.loud_buf[idx] * self.hits + self.loud) / (self.hits + 1)
        else:
            self.hits = 0
            self.loud_buf[idx] = self.loud
            self.last_loud_idx = idx
            idx = ring_buffer_idx(idx, -2, self.loud_buf_size)
            c_idx = idx
            c = 0
            length = self.loud_buf_size - 1
            for i in range(length):
                nl = ring_buffer_idx(c_idx, -1, self.loud_buf_size)
                nr = ring_buffer_idx(c_idx, 1, self.loud_buf_size)
                if self.loud_buf[c_idx] > self.loud_buf[nl] * snr and self.loud_buf[c_idx] > self.loud_buf[nr] * snr:
                    c += 1
                    if idx == c_idx:
                        self.loud_thr = self.loud_buf[idx]
                        is_a_beat = True
                c_idx = nl
            if c > 0:
                self.period = (self.period * 4 + sample_ms * length / c) * 0.2
        return is_a_beat
