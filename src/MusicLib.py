def ring_buffer_idx(m, icr, size):
    return (m + icr) % size

class MusicLib(object):
    def __init__(self):
        self.loud_thr = 15 # the loudness threshold for beats
        self.loud = 0
        self.buf_size = 41 # 40 measurements bucket and 1 data collection bucket
        self.buf = [0] * self.buf_size # ring buffer of loudness
        self.last_idx = 0
        self.period = 500 # period of music beats, 500ms is the most possible period
        self.hits = 0 # number of measurements of current data collection bucket

    # check if it is a beat, compute music period, and update the loudness threshold
    def is_a_beat(self, timestamp, loudness, snr: float, sample_ms=125):
        self.loud = loudness*0.01 # scale down to prevent overflow
        is_a_beat = False
        # compute bucket index
        idx = (timestamp // sample_ms) % self.buf_size
        if idx == self.last_idx:
            # update the data collection bucket
            self.hits += 1
            self.buf[idx] = (self.buf[idx] * (self.hits-1) + self.loud) / self.hits
        else:
            # fill the new bucket
            self.hits = 0
            self.buf[idx] = self.loud
            self.last_idx = idx
            # beat detection only when previous bucket is full
            c_idx = ring_buffer_idx(idx, -2, self.buf_size) # starting with the bucket before previous bucket
            prev_idx = c_idx #  full bucket index before previous full bucket
            c = 0 # count of beats
            length = self.buf_size - 1 # only use full buckets
            # Calculate average loudness of the buffer
            avg_loudness = sum(self.buf) / self.buf_size
            for i in range(length):
                nl = ring_buffer_idx(c_idx, -1, self.buf_size) # left neighbor
                nr = ring_buffer_idx(c_idx, 1, self.buf_size) # right neighbor
                if self.buf[c_idx] > self.buf[nl] * snr and self.buf[c_idx] > self.buf[nr] * snr and self.buf[c_idx] > avg_loudness: 
                    # peak detected
                    c += 1
                    if prev_idx == c_idx:
                        # new beat detected as the nearest full bucket
                        self.loud_thr = self.buf[c_idx] * 0.9
                        is_a_beat = True
                c_idx = nl # move to previous bucket
            if c > 0:
                #self.period = (self.period * 9 + sample_ms * length / c) * 0.1
                # More aggressive smoothing for large period changes
                new_period = sample_ms * length / c
                period_ratio = new_period / self.period if self.period > 0 else 1.0
                smooth_factor = 0.1 if 0.8 < period_ratio < 1.2 else 0.05
                self.period = (self.period * (1.0 - smooth_factor) + 
                              new_period * smooth_factor)
                #print("Music period: ", self.period, is_a_beat, c, sample_ms, avg_loudness, self.loud_thr, self.loud)
        return is_a_beat
