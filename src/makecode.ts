// Ported MusicLib for beat detection on micro:bit
function ringBufferIdx (m: number, icr: number, size: number) {
    result = (m + icr) % size
    if (result < 0) {
        // Handle negative modulo in JS
        result += size
    }
    return result
}

let result = 0
let now = 0
let micLoudness = 0
let pitch = 0
let pulseDelay = 0
class Parameters {
    w_t: number;
    j_t: number;
    l_s: number;
    dof: number;
    s_err: number[];
    s_ct: number[];
    s_tg: number[];
    s_tr: number[];
    ep_dir: number[];
    ep_size: number;
    ep_dis: number[];
    ep_mid2: number;
    ep_mid1: number;
    walk_fw_sts: number[];
    walk_bw_sts: number[];
    skate_fw_sts: number[];
    skate_bw_sts: number[];
    dance_ok: number[];
    st_tg: number[][];
    dict_sp: number[]; // Using index-based array for mapping
    st_spu: number[][];

    constructor() {
        this.w_t = 16;
        this.j_t = 27;
        this.l_s = 45;
        this.dof = 6;

        // Initialize vectors
        this.s_err = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0];
        this.s_ct = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0];
        this.s_tg = [90.0, 90.0, 90.0, 90.0, 90.0, 90.0];

        // Servo trim
        this.s_tr = [-5, -0.0, -5, -0.0, -9.0, 0.0];

        // Turning directions
        this.ep_dir = [-1.0, -0.7, 0.7, 1.0];
        this.ep_size = this.ep_dir.length;
        this.ep_dis = [500.0, 500.0, 500.0, 500.0];
        this.ep_mid2 = Math.floor(this.ep_size * 0.5);
        this.ep_mid1 = Math.max(0, this.ep_mid2 - 1);

        // Movement sequences
        this.walk_fw_sts = [2, 3, 4, 5];
        this.walk_bw_sts = [6, 5, 7, 3];
        this.skate_fw_sts = [8, 9, 10, 11];
        this.skate_bw_sts = [12, 1, 13, 9];
        this.dance_ok = [0, 2, 3, 4, 5, 8, 9, 10, 11, 12, 13, 14, 16, 17];

        let w_t = this.w_t;
        let l_s = this.l_s;
        let j_t = this.j_t;

        // Servo targets for each pose
        this.st_tg = [
            [90, 90, 90, 90, 90, 80],                  // 0: stand
            [10, 150, 170, 30, 40, 125],               // 1: duck
            [90 - w_t, 90 + 35, 90 - j_t, 90 + 30, 90 - l_s - 8, 80], // 2: walk1
            [93, 90 + l_s, 93, 90 + l_s, 90 - l_s - 8, 80],           // 3: w2
            [90 + j_t, 90 - 30, 90 + w_t, 90 - 35, 90 + l_s + 8, 80], // 4: w3
            [87, 90 - l_s, 87, 90 - l_s, 90 + l_s + 8, 80],           // 5: w4
            [90 - w_t, 90 - 25, 90 - j_t, 90 - 45, 90 + l_s, 80],     // 6: w5
            [90 + j_t, 90 + 45, 90 + w_t, 90 + 25, 90 - l_s, 80],     // 7: w6
            [90 - w_t + 5, 90 + 35, 90 - w_t, 90 + 10, 90 + 35, 90 + 5], // 8: skate 1
            [90 + w_t - 5, 90 + 35, 90 + w_t - 5, 90 + 25, 90 - 20, 90 - 15], // 9: s2
            [90 + w_t, 90 - 10, 90 + w_t - 5, 90 - 35, 90 - 35, 90 + 5], // 10: s3
            [90 - w_t + 5, 90 - 25, 90 - w_t + 5, 90 - 35, 90 + 20, 90 - 15], // 11: s4
            [90 - w_t + 5, 90 - 20, 90 - j_t, 90 - 20, 90 + 20, 90],  // 12: s5
            [90 + j_t, 90 + 20, 90 + w_t - 5, 90 + 20, 90 - 20, 90],  // 13: s6
            [130, 90, 50, 90, 90, 90],                 // 14: jump
            [0, 85, 180, 95, 90, 90],                  // 15
            [85, 90, 95, 90, 45, 65],                  // 16: dance
            [85, 90, 95, 90, 135, 65],                 // 17
            [75, 90, 30, 90, 135, 105],                // 18: side move
            [150, 90, 105, 90, 45, 105],               // 19
            [75, 90, 30, 90, 45, 75],                  // 20
            [150, 90, 105, 90, 135, 75],               // 21
            [75, 90, 75, 90, 90, 90],                  // 22
            [105, 90, 105, 90, 90, 90],                // 23
            [130, 90, 50, 90, 90, 55],                 // 24: soccer
            [90, 60, 90, 120, 90, 90],                 // 25: calibrate
            [90, 90, 90, 90, 90, 90]                   // 26: rest
        ];

        // Mapping dictionary
        this.dict_sp = [1, 0, 3, 4, 2, 4, 3, 2, 3, 4, 2, 4, 3, 2, 8, 10, 0, 0, 6, 6, 6, 6, 9, 7, 5, 7, 0];

        // Control speed vectors
        this.st_spu = [
            [1, 1, 1, 1, 1, 1],             // 0
            [1, 1, 1, 1, 0.5, 0.5],         // 1
            [2, 1, 1, 1, 1.2, 0.4],         // 2
            [1, 1, 2, 1, 1.2, 0.4],         // 3
            [1, 1, 1, 1, 1.2, 0.4],         // 4
            [5, 1, 5, 1, 1, 5],             // 5
            [0.55, 1, 0.55, 1, 1, 1],       // 6
            [2, 1, 1, 1, 1, 1],             // 7
            [5, 1, 5, 1, 1, 3],             // 8
            [1, 1, 2, 1, 1, 1],             // 9
            [6, 2, 6, 2, 1, 1]              // 10
        ];
    }
}
class MusicLib {
    loud_thr: number;
    loud: number;
    buf_size: number;
    buf: number[];
    last_idx: number;
    period: number;
    hits: number;

    constructor() {
        this.loud_thr = 15; // loudness threshold for beats
        this.loud = 0;
        this.buf_size = 43; // 42 measurements bucket and 1 data collection bucket
        this.buf = [];
        for (let i = 0; i < this.buf_size; i++) {
            this.buf.push(0);
        }
        this.last_idx = 0;
        this.period = 500; // most possible period in ms
        this.hits = 0;
    }

    /**
     * check if it is a beat, compute music period, and update threshold
     */
    isABeat(timestamp: number, loudness: number, snr: number, sampleMs: number = 125): boolean {
        this.loud = loudness * 0.01; // scale down
        let isABeatResult = false;

        // compute bucket index
        let idx = Math.floor(timestamp / sampleMs) % this.buf_size;

        if (idx == this.last_idx) {
            // update the data collection bucket
            this.hits += 1;
            this.buf[idx] = (this.buf[idx] * (this.hits - 1) + this.loud) / this.hits;
        } else {
            // fill the new bucket
            this.hits = 0;
            this.buf[idx] = this.loud;
            this.last_idx = idx;

            // beat detection only when previous bucket is full
            let cIdx = ringBufferIdx(idx, -2, this.buf_size);
            let prevIdx = cIdx;
            let c = 0; // beat count

            // Calculate average loudness
            let sumLoud = 0;
            for (let val of this.buf) {
                sumLoud += val;
            }
            let avgLoudness = sumLoud / this.buf_size;
            let length = this.buf_size - 3;

            for (let j = 0; j < length; j++) {
                let nl = ringBufferIdx(cIdx, -1, this.buf_size);
                let nr = ringBufferIdx(cIdx, 1, this.buf_size);

                if (this.buf[cIdx] > this.buf[nl] * snr &&
                    this.buf[cIdx] > this.buf[nr] * snr &&
                    this.buf[cIdx] > avgLoudness) {

                    c++;
                    if (prevIdx == cIdx) {
                        this.loud_thr = this.buf[cIdx] * 0.9;
                        isABeatResult = true;
                    }
                }
                cIdx = nl; // move to previous
            }

            if (c > 0) {
                let newPeriod = sampleMs * length / c;
                let periodRatio = this.period > 0 ? newPeriod / this.period : 1.0;
                let smoothFactor = (periodRatio > 0.8 && periodRatio < 1.2) ? 0.1 : 0.05;

                this.period = (this.period * (1.0 - smoothFactor)) + (newPeriod * smoothFactor);
            }
        }
        return isABeatResult;
    }
}
class Content {
    notes: string[];
    chord: number[][];
    pattern: number[][];
    loc: string[];
    act: string[];
    sub: string[];
    obj: string[];
    sentences: string[];

    constructor() {
        this.notes = ["#70REYY", "#62MIYY", "#58FAOR", "#52SOHW", "#46LAOR", "#42TIYY", "#39DOWW",
            "#35REYY", "#31MIYY", "#29FAOR", "#26SOHW", "#23LAOR", "#21TIYY", "#20DOWW"];
        this.chord = [[0, 3, 5], [0, 2, 4, 6], [0, 2, 4, 7], [0, 1, 2, 3]];
        this.pattern = [[0, 0, 0, 0], [0, 0, 1], [0, 1, 0], [1, 0, 0], [1, 1], [3]];
        this.loc = ["here", "there", "up", "down", "left", "right", "front", "back", ""];
        this.act = ["liked", "saw", "heard", "felt", ""];
        this.sub = ["I", "He", "She", "They", ""];
        this.obj = ["me", "you", "him", "her", "them", "it", "the dance", "the song", ""];
        this.sentences = ["I am so tired.", "Let's go, go, go!", "Be careful!", "Life lies in motion.",
            "Let's pair up!", "I am stuck!", "New song:", "Easy peasy!", "I like my backpack",
            "I love you", "You are the best!", "yeh!", "woohoo!"];
    }

    // Helper to pick random item from an array
    private choice<T>(arr: T[]): T {
        return arr[Math.floor(Math.random() * arr.length)];
    }

    // Helper to get random integer between min and max (inclusive)
    private randint(min: number, max: number): number {
        return Math.floor(Math.random() * (max - min + 1)) + min;
    }

    /**
     * Composes a procedural song string
     */
    compose_song(): string {
        let song: string[] = [];
        let b = this.notes.length;
        let d = this.choice(this.chord);
        let w = this.choice(this.pattern);
        let k = 0;

        while (k < 16) {
            let l = this.randint(0, b - 1);
            for (let m of w) {
                let n = (l + this.choice(d) + this.choice([-1, 0, 0, 0, 0, 1])) % b;
                if (n < 0) n += b; // Handle negative modulo

                let o = this.notes[n];

                if (m >= 1 && this.randint(0, 8) == 0) {
                    song.push(o);
                    for (let count = 0; count < m; count++) {
                        let innerIdx = (n + this.choice([-1, 0, 1])) % b;
                        if (innerIdx < 0) innerIdx += b;
                        song.push(this.notes[innerIdx]);
                    }
                } else {
                    // Python: n + n[-1] * 4 * j
                    // Appends the last character of the note string repeated (4 * j) times
                    let repeatedChar = o.charAt(o.length - 1);
                    let suffix = "";
                    for (let count2 = 0; count2 < (4 * m); count2++) {
                        suffix += repeatedChar;
                    }
                    song.push(o + suffix);
                }
                k += m + 1;
            }
            d = this.choice(this.chord);
            w = this.choice(this.pattern);
        }
        return song.join("");
    }

    /**
     * Generates a random "cute" sentence
     */
    cute_words(): string {
        return this.choice(this.sub) + " " +
            this.choice(this.act) + " " +
            this.choice(this.obj) + " " +
            this.choice(this.loc) + ".";
    }
}
class HCSR04 {
    timeout_us: number;
    trig: DigitalPin;
    echo: DigitalPin;

    constructor(trigPin: DigitalPin = DigitalPin.P2, echoPin: DigitalPin = DigitalPin.P8) {
        // Default timeout: 30000us (approx 500cm)
        this.timeout_us = 500 * 2 * 30;
        this.trig = trigPin;
        this.echo = echoPin;

        // Initialize pins
        pins.digitalWritePin(this.trig, 0);
        pins.digitalReadPin(this.echo);
    }

    /**
     * Measures distance in centimeters
     */
    distance_cm(): number {
        // 1. Send 10us pulse to Trigger pin
        pins.digitalWritePin(this.trig, 0);
        control.waitMicros(5);
        pins.digitalWritePin(this.trig, 1);
        control.waitMicros(10);
        pins.digitalWritePin(this.trig, 0);

        // 2. Read the pulse width on Echo pin (High pulse)
        // returns duration in microseconds
        let t = pins.pulseIn(this.echo, PulseValue.High, this.timeout_us);

        // 3. Handle timeout (Python code defaults to 500 if t < 0)
        if (t <= 0) {
            t = 500;
        }

        control.waitMicros(5);

        // 4. Calculate distance: (time * speed of sound / 2)
        // The original multiplier 0.0171821 is (343.64 m/s / 2 / 10000)
        return t * 0.0171821;
    }
}
// Configuration Constants
let WK_ADDR = 16
class WK {
    private last_bl_ts: number;
    private eye_on: boolean;
    private l_e_b: number;
    private r_e_b: number;
    private eye_icr: number;
    private bl_itl: number;
    public pos: number;
    public num_steps: number;
    private bl_g: number;
    private idle: boolean;
    public c_s: number;

    constructor() {
        this.last_bl_ts = 0;
        this.eye_on = true;
        this.l_e_b = 1023;
        this.r_e_b = 1023;
        this.eye_icr = 1;
        this.bl_itl = 6000;
        this.pos = 0;
        this.num_steps = 0;
        this.bl_g = 4000;
        this.idle = false;
        this.c_s = 0;
        // I2C is initialized automatically in MakeCode
    }

    /**
     * Control a DC motor. sp: -100 to 100.
     */
    public motor(m: number, sp: number): void {
        if (sp >= -100 && sp <= 100 && m >= 1 && m <= 2) {
            let buf = pins.createBuffer(4);
            buf.setNumber(NumberFormat.UInt8LE, 0, m);
            buf.setNumber(NumberFormat.UInt8LE, 1, 0x01);
            buf.setNumber(NumberFormat.Int8LE, 2, sp); // Signed speed
            buf.setNumber(NumberFormat.UInt8LE, 3, 0);
            pins.i2cWriteBuffer(WK_ADDR, buf);
        }
    }

    /**
     * Set servo angle (0-180).
     */
    public servo(sr: number, a: number): void {
        if (sr >= 0 && sr <= 7) {
            a = Math.min(180, Math.max(0, Math.floor(a)));
            let reg = (sr == 7) ? 0x10 : sr + 3;
            let buf2 = pins.createBuffer(4);
            buf2.setNumber(NumberFormat.UInt8LE, 0, reg);
            buf2.setNumber(NumberFormat.UInt8LE, 1, a);
            buf2.setNumber(NumberFormat.UInt8LE, 2, 0);
            buf2.setNumber(NumberFormat.UInt8LE, 3, 0);
            pins.i2cWriteBuffer(WK_ADDR, buf2);
        }
    }

    /**
     * Control onboard LED lights.
     */
    public set_light(light: number): void {
        let buf3 = pins.createBuffer(4);
        buf3.setNumber(NumberFormat.UInt8LE, 0, 0x12);
        buf3.setNumber(NumberFormat.UInt8LE, 1, light);
        buf3.setNumber(NumberFormat.UInt8LE, 2, 0);
        buf3.setNumber(NumberFormat.UInt8LE, 3, 0);
        pins.i2cWriteBuffer(WK_ADDR, buf3);
    }

    /**
     * Move servo toward target with controlled speed.
     */
    public servo_step(target: number, sp: number, idx: number, p: Parameters): void {
        sp = Math.abs(sp);
        target = Math.max(0, Math.min(179, target));
        let err = target - p.s_tg[idx];
        p.s_err[idx] = err;

        if (Math.abs(err) < sp) {
            p.s_tg[idx] += err;
        } else {
            p.s_tg[idx] += (err >= 0) ? sp : -sp;
        }
        this.servo(idx, p.s_tg[idx]);
    }

    /**
     * Move all servos immediately to target state.
     */
    public servo_move(idx: number, para: Parameters): void {
        for (let p = 0; p < para.dof; p++) {
            this.servo(p, para.st_tg[idx][p] + para.s_tr[p]);
        }
        this.idle = true;
    }

    /**
     * Check if servos reached target.
     */
    public is_servo_idle(s_list: number[], p: Parameters): boolean {
        this.idle = s_list.every(i => Math.abs(p.s_err[i]) < 1);
        return this.idle;
    }

    /**
     * Move robot through state sequences.
     */
    public move(p: Parameters, states: number[], sync_list: number[], sp: number, async_list: number[], async_sp: number): number {
        if (sp == 0) return 0;

        this.pos = Math.min(this.pos, states.length - 1);
        this.c_s = states[this.pos];
        let targets = p.st_tg[this.c_s];

        let sp_idx = p.dict_sp[this.c_s] || 1;
        let sps = p.st_spu[sp_idx];

        for (let q of sync_list) {
            this.servo_step(targets[q] + p.s_tr[q] + p.s_ct[q], sp * sps[q], q, p);
        }

        for (let r of async_list) {
            this.servo_step(targets[r] + p.s_tr[r] + p.s_ct[r], async_sp * sps[r], r, p);
        }

        if (this.is_servo_idle(sync_list, p)) {
            this.pos = (this.pos + 1) % states.length;
            this.num_steps += 1;
            return 0;
        }
        return 1;
    }

    /**
     * Eyes ON/OFF control.
     */
    public eyes_ctl(c: number): void {
        pins.digitalWritePin(DigitalPin.P12, c);
        pins.digitalWritePin(DigitalPin.P13, c);
        this.eye_on = (c == 1);
        this.last_bl_ts = control.millis();
    }

    /**
     * Left eye brightness (0-1023).
     */
    public left_eye_bright(b: number): void {
        pins.analogWritePin(AnalogPin.P12, b);
        this.l_e_b = b;
    }

    /**
     * Right eye brightness (0-1023).
     */
    public right_eye_bright(b: number): void {
        pins.analogWritePin(AnalogPin.P13, b);
        this.r_e_b = b;
    }

    /**
     * Blink animation logic.
     */
    public blink(alert_l: number): void {
        let ts_diff = control.millis() - this.last_bl_ts;

        if (this.eye_on) {
            if (ts_diff > this.bl_itl) {
                this.eyes_ctl(0);
            } else {
                let brightness = alert_l * 102;
                this.bl_g = alert_l * 400;
                this.left_eye_bright(brightness);
                this.right_eye_bright(brightness);
            }
        } else {
            if (ts_diff > Math.randomRange(100, 250)) {
                this.eyes_ctl(1);
                if (Math.randomRange(0, 4) == 0) {
                    this.bl_itl = Math.randomRange(100, 250);
                } else {
                    this.bl_itl = Math.randomRange(this.bl_g, this.bl_g * 2);
                }
            }
        }
    }

    /**
     * Pulsing/Flash animation.
     */
    public flash(icr: number = 50): void {
        this.l_e_b += this.eye_icr;

        if (this.l_e_b >= 1023) {
            this.eye_icr = -icr;
            this.l_e_b = 1023;
        } else if (this.l_e_b <= 0) {
            this.eye_icr = icr;
            this.l_e_b = 0;
        }

        this.right_eye_bright(1023 - this.l_e_b);
        this.left_eye_bright(this.l_e_b);
    }
}

/**
 * RobotPu Class for MakeCode
 * Optimized with internal WK and Parameters instances.
 */

class RobotPu {
    // Component Instances
    public pr: Parameters;
    public wk: WK;
    public sonar: HCSR04;
    public np: neopixel.Strip;
    public content: Content;
    public music: MusicLib;

    // Basic identification
    public name: string;
    public sn: string;
    public gst: number;

    // Movement & State
    public last_cmd_ts: number;
    private fw_sp: number = 6;
    private bw_sp: number = -3;
    private sp: number = 0;
    private di: number = 0;
    private h_u_bias: number = 0;
    private h_l_bias: number = 0;
    private alt_l: number = 10;
    private alt_sc: number = 0.9;
    private r_st: number = 26;

    // IMU & Balance
    private bd_pth: number = 0;
    private bd_pth2: number = 0;
    private bd_rl: number = 0;
    private bd_rl2: number = 0;
    private pth: number = 0;
    private rl: number = 0;
    private max_g: number = 1.0;
    private g_thr: number = 2000;

    // State Tracking
    private fell_count: number = 0;
    private last_state: number = 0;
    private groupID: number = 166;

    // Current dance state (sequence of state indices)
    private d_st: number[] = [0];

    // Predefined dance routines
    private d_dict: { [key: number]: number[] } = {
        14: [0, 15, 15, 0, 3, 5, 3],  // Forward-backward movement
        0: [0, 19, 0, 18, 0, 3],      // Side-to-side movement
        5: [3, 5, 2, 5, 3],           // Quick steps
        16: [17, 16, 17, 16, 17]      // Rocking motion
    };

    private d_sp: number = 1.5;           // Dance speed multiplier
    private last_low_b: number = 0;       // Timestamp of last low beat
    private last_high_b: number = 0;      // Timestamp of last high beat
    private dance_l_itv: number = 12;     // Left/right wiggle angle (degrees)
    private dance_u_itv: number = 15;     // Up/down wiggle angle (degrees)

    // Balance & Tilt Offsets
    private l_o_t: number = 0;         // Left tilt offset
    private r_o_t: number = 0;         // Right tilt offset
    private max_rl_ctl: number = 15.0; // Max roll control authority

    /** Current exploration speed (calculated by set_explore_param) */
    private ep_sp: number = 0.0;

    /** Current exploration direction bias (-1.0 to 1.0) */
    private ep_di: number = 0.0;

    /** Index in the ep_dis array representing the clearest path */
    private ep_max_i: number = 0;

    /** Distance threshold: Consider an obstacle "hit" if closer than this (cm) */
    private ep_thr: number = 7.5;

    /** Tilt offset applied during exploration maneuvers */
    private ep_ot: number = 0;

    /** Far threshold: Begin slowing down or planning turns if obstacle is within this (cm) */
    private ep_far: number = 20;

    // Command Dictionary
    public cmdDict: { [key: string]: (v: number) => void };
    // Define the State Dictionary
    private st_dict: { [key: number]: () => void };

    constructor(sn: string, name: string = "peu") {
        // Initialize Core Components inside constructor
        this.pr = new Parameters();
        this.wk = new WK();

        this.sn = sn;
        this.name = name;
        this.gst = 0;
        this.last_cmd_ts = control.millis();

        // Hardware Setup
        this.sonar = new HCSR04(DigitalPin.P2, DigitalPin.P8);
        this.np = neopixel.create(DigitalPin.P16, 4, NeoPixelMode.RGB);
        this.content = new Content();
        this.music = new MusicLib();

        // Audio & Radio Setup
        radio.setGroup(this.groupID);
        billy.voicePreset(BillyVoicePreset.LittleRobot);
        music.setVolume(150);

        // Initialize Command Dictionary
        this.cmdDict = {
            "#puspeed": (v) => this.speed(v),
            "#puturn": (v) => this.turn(v),
            "#puroll": (v) => this.roll(v),
            "#pupitch": (v) => this.pitch(v),
            "#puB": (v) => this.button(v),
            "#pulogo": (v) => this.logo(v),
            "#purs": (v) => this.pose(v)
        };
        // We use arrow functions () => to ensure 'this' refers to the RobotPu instance
        this.st_dict = {
            [-3]: () => this.fall(),
            [-2]: () => this.fetal(),
            [0]: () => this.idle(),
            [1]: () => this.explore(),
            [2]: () => this.jump(),
            [3]: () => this.dance(),
            [4]: () => this.kick(),
            [5]: () => this.joystick()
        };

        this.wk.eyes_ctl(1);
        this.show_channel();
    }

    /**
     * Handles manual movement and stance control from a remote.
     * Ported from joystick() in Python.
     */
    public joystick(): number {
        // 1. If speed is near zero, handle stationary behavior
        if (Math.abs(this.sp) < 0.1) {
            // Smoothly move the head/body to match bias values
            // Servo 4 is waist/roll, Servo 5 is head/pitch
            this.wk.servo_step(90 + this.h_l_bias, 1, 4, this.pr);
            this.wk.servo_step(90 + this.h_u_bias, 1, 5, this.pr);

            // 2. If the turn stick is pushed far left/right while standing, side-step
            if (Math.abs(this.di) > 0.9) {
                return this.side_step(this.di);
            }

            // Otherwise, stay in idle stance
            return this.rest();
        } else {
            // 3. If there is speed, perform the balanced walk
            return this.walk(this.sp, this.di);
        }
    }

    /**
     * Executes a side-stepping (lateral) movement.
     * @param di Directional bias: positive for right, negative for left.
     */
    /**
     * Executes a side-stepping movement using specific state indices.
     * @param di Directional bias: positive for right, negative for left.
     */
    public side_step(di: number): number {
        // 1. Select the gait state sequence based on direction
        // Python: [20, 22, 0, 19] if di > 0 else [18, 21, 23, 0]
        let sts = di > 0 ? [20, 22, 0, 19] : [18, 21, 23, 0];

        // 2. Reset the Control Vector to neutral
        // This clears any persistent tilt or pitch offsets
        this.set_ct([0, 1, 2, 3, 4, 5], [0, 0, 0, 0, 0, 0]);

        // 3. Calculate movement speed based on forward speed multiplier
        let movementSpeed = di * this.fw_sp;

        // 4. Execute the movement via the WK engine
        // Parameters: states, sync_servos (0-3), sync_speed, async_servos (4-5), async_speed
        return this.wk.move(
            this.pr,
            sts,
            [0, 1, 2, 3],
            movementSpeed,
            [4, 5],
            movementSpeed
        );
    }

    public show_channel() {
        basic.showNumber(this.groupID - 160);
    }

    public talk(text: string) {
        billy.say(text);
    }

    /**
     * Triggers the balanced walking gait.
     * @param sp Speed (positive for forward, negative for backward)
     * @param di Directional bias (-1.0 to 1.0)
     */
    public walk(sp: number, di: number): number {
        return this.move_balance(sp, di, this.pr.walk_fw_sts, this.pr.walk_bw_sts);
    }

    /**
     * IMU Balance Calculations using this.pr and this.wk
     */
    private balance_param() {
        let ax = input.acceleration(Dimension.X);
        let ay = input.acceleration(Dimension.Y);
        let az = input.acceleration(Dimension.Z);

        this.max_g = Math.sqrt(ax * ax + ay * ay + az * az);
        this.pth = Math.atan2(ay, -az) * (180 / Math.PI);
        this.rl = Math.asin(ax / (this.max_g || 1)) * (180 / Math.PI);

        // Use this.pr and this.wk for calculations
        let bd_p = this.pth + (this.pr.st_tg[0][5] + this.pr.s_tr[5] - this.pr.s_tg[5]);
        let servo_lft = (this.pr.s_tg[4] - this.pr.st_tg[0][4] - this.pr.s_tr[4]) * (Math.PI / 180);

        this.bd_rl = bd_p * Math.sin(servo_lft) + this.rl * Math.cos(servo_lft);
        this.bd_rl2 = (this.bd_rl + 9 * this.bd_rl2) * 0.1;

        this.bd_pth = bd_p * Math.cos(servo_lft) - this.rl * Math.sin(servo_lft);
        this.bd_pth2 = (this.bd_pth + 9 * this.bd_pth2) * 0.1;
    }

    private set_ct(indx_l: number[], v_l: number[]) {
        let le = Math.min(indx_l.length, v_l.length);
        for (let i = 0; i < le; i++) {
            this.pr.s_ct[indx_l[i]] = v_l[i]; // Reference internal pr
        }
    }

    public move_balance(sp: number, di: number, fw_l: number[], bw_l: number[]) {
        let sts = sp > 0 ? fw_l : bw_l;
        this.balance_param();

        let l_o_t = 0;
        let r_o_t = 0;
        let lf = 0;

        if (this.wk.pos < 2 || this.wk.pos == 6) { // Reference internal wk
            l_o_t = Math.min(this.max_rl_ctl, Math.max(0.0, this.bd_rl * 0.8 - this.pr.w_t));
            lf = -12 * di;
        } else {
            r_o_t = Math.max(-this.max_rl_ctl, Math.min(0.0, this.bd_rl * 0.8 + this.pr.w_t));
            lf = 12 * di;
        }

        let o_t = l_o_t + r_o_t;
        sp /= 1.0 + 0.01 * (Math.abs(this.bd_rl) + Math.abs(this.bd_pth)) + Math.sqrt(Math.abs(o_t * 0.5));

        this.set_ct([0, 1, 2, 3, 4, 5],
            [o_t, lf - o_t, o_t, -lf - o_t, -40 * di - o_t, Math.min(25.0, -2.0 * this.bd_pth2)]);

        // Call internal wk.move
        return this.wk.move(this.pr, sts, [0, 1, 2, 3], sp, [4, 5], sp);
    }

    /**
     * Update robot states based on sensor inputs.
     * Ported from set_states() in Python.
     */
    public update_states(): void {
        // 1. Fall detection using Accelerometer
        if (input.isGesture(Gesture.FreeFall)) {
            this.gst = -2; // Enter fall state
        }

        // 2. Handle automatic state transitions (Inactivity Timeout)
        if (this.gst > 0) { // If in an active state
            this.alt_l = 10; // Reset alert level
            // 2-second timeout to return to idle
            if (control.millis() - this.last_cmd_ts > 2000) {
                this.gst = 0;
            }
        }

        // 3. Balance monitoring and recovery logic
        if (this.gst != -2) { // If not in protective fetal position
            // Check tilt thresholds (equivalent to bd_rl2/bd_pth2 in Python)
            if (Math.abs(this.bd_rl2) > 75 || Math.abs(this.bd_pth2) > 75) {
                this.balance_param(); // Recalculate IMU data
                this.fell_count++;
                this.wk.num_steps = 0; // Reset step count on fall

                if (this.fell_count > 16) {
                    this.gst = -3; // Enter "Help me" recovery state
                }
            } else {
                this.fell_count = 0;
                // Return to previous state after standing up
                if (this.gst == -3) {
                    this.gst = this.last_state;
                    this.talk("Thanks");
                }
            }
        }
    }

    // Behavior States
    private idle() {
        if (Math.randomRange(0, 100) == 0) this.alt_l *= this.alt_sc;
        this.rest();
    }

    private rest() {
        this.balance_param();
        let rl = Math.min(35.0, Math.max(-35.0, this.bd_rl2));
        if (Math.abs(rl) > 5) {
            this.set_ct([0, 1, 2, 3, 4], [rl, rl * -1.0, rl, rl * -1.0, rl * -0.5]);
        }
        if (Math.abs(this.bd_pth2) > 12) {
            this.set_ct([5], [-this.bd_pth2]);
        }
        let sl = input.soundLevel();
        this.pr.st_tg[this.r_st][5] = 90 - sl * 0.3;
        return this.wk.move(this.pr, [this.r_st], [0, 1, 2, 3, 4, 5], 1 + sl * 0.001, [], 0.5);
    }

    /**
     * Handles the robot's behavior when it has fallen and cannot recover.
     * Ported from fall() in Python.
     */
    public fall(): void {
        // 1. Trigger the "Knight Rider" style eye flash effect
        this.wk.flash();

        // 2. Randomly trigger a voice request for help (approx 1 in 500 cycles)
        if (Math.randomRange(0, 500) == 0) {
            // Use pxt-billy to speak the distress message
            this.talk("Help me stand up!");

            // 3. Publish a status code via radio for remote monitoring
            this.s_code("E2");
        }
    }

    /**
     * Set the robot to a compact fetal position for protection or power saving.
     * Ported from fetal() in Python.
     */
    public fetal(): void {
        // 1. Trigger the eye pulsing animation
        this.wk.flash();

        // 2. 0.5% chance to shout for help (random.randint(0, 200) == 0)
        if (Math.randomRange(0, 200) == 0) {
            this.talk("Help me!");
        }

        // 3. Move to the Fetal State (Index 1)
        // states: [1], sync_list: all servos [0-5], speed: 2.0, async: none, async_sp: 0.5
        this.wk.move(this.pr, [1], [0, 1, 2, 3, 4, 5], 2.0, [], 0.5);
    }

    /**
     * Publishes a status or error code via radio.
     * @param code The status/error code string (e.g., "E2", "OK", "BATT").
     */
    public s_code(code: string): void {
        // 1. Construct the message string
        // Python equivalent: f"#puc:{self.sn}:{code}"
        let message = "#puc:" + this.sn + ":" + code;

        // 2. Send the message over the radio
        // This will be received by anything on the same radio group ID
        radio.sendString(message);
    }

    /**
     * Calculates exploration speed and direction based on sonar point-cloud.
     * Ported from set_explore_param() in Python.
     */
    private set_explore_param(): void {
        // 1. Check for obstacles in the "middle" view of the point cloud
        let mid_view = [this.pr.ep_dis[this.pr.ep_mid1], this.pr.ep_dis[this.pr.ep_mid2]];
        let obs_hcsr = Math.min(mid_view[0], mid_view[1]);

        let nd = 0; // New Direction variable

        // 2. Decision Logic based on distance thresholds
        if (obs_hcsr < this.ep_thr + this.ep_far) {
            // Path is getting tight: Look only at middle indices for turn direction
            // Python slice [mid1 : mid2+1]
            let slice = this.pr.ep_dis.slice(this.pr.ep_mid1, this.pr.ep_mid2 + 1);
            nd = this.get_turn_from_sonar(slice, 3);
        } else {
            // Path is clear: Look at the whole point cloud for a better direction
            nd = this.get_turn_from_sonar(this.pr.ep_dis, 5);
        }

        // 3. Overall minimum distance check
        obs_hcsr = Math.min(this.pr.ep_dis[0], Math.min(this.pr.ep_dis[1], Math.min(this.pr.ep_dis[2], this.pr.ep_dis[3])));
        let dis = obs_hcsr - this.ep_thr;

        // 4. Handle "Stuck" logic (if speed is negative)
        if (this.ep_sp < 0) {
            // Turn aggressively to escape the corner
            nd = nd > 0 ? 1 : -1;
            this.ep_di = (this.ep_di * 9 + nd) * 0.1; // Slow smoothing for escape

            dis -= 12 + Math.randomRange(-5, 0);

            // Low probability to shout for help via radio
            if (Math.randomRange(0, 400) == 0) {
                this.talk(this.content.sentences[5]);
                this.s_code("W1"); // Send Warning Code 1
            }
        } else {
            // Normal direction smoothing (Low pass filter)
            this.ep_di = (this.ep_di * 3 + nd) * 0.25;
        }

        // 5. Apply Low-pass filter to Speed
        let target_sp = 0;
        if (dis >= 0) {
            target_sp = Math.min(this.fw_sp, (dis + 5) * 0.8);
        } else {
            target_sp = Math.max(this.bw_sp, (dis - 5) * 0.6);
        }
        this.ep_sp = (this.ep_sp + target_sp) * 0.5;
    }

    /**
     * Map sonar distance readings to a steering direction for auto-pilot.
     * @param ep_dis List of sonar distance readings from left to right
     * @param turn_gain Scaling factor for turn intensity (default: 1.5)
     * @returns Steering direction between -1.0 (left) and 1.0 (right)
     */
    public get_turn_from_sonar(ep_dis: number[], turn_gain: number = 1.5): number {
        // 1. Guard against empty arrays
        if (ep_dis.length == 0) {
            return 0.0;
        }

        // 2. Calculate the total weight (total distance)
        let tw = 0;
        for (let d of ep_dis) {
            tw += d;
        }

        // 3. If everything is zero (no readings), go straight
        if (tw == 0) {
            return 0.0;
        }

        // 4. Calculate Center of Mass (CM)
        let weighted_sum = 0;
        let count = ep_dis.length;

        for (let i = 0; i < count; i++) {
            // Calculate normalized position from -1 (left) to 1 (right)
            // Python: i * 2 / (len(ep_dis) - 1) - 1
            let pos = (count > 1) ? (i * 2 / (count - 1) - 1) : 0;

            // Add weighted position to the sum
            weighted_sum += ep_dis[i] * pos;
        }

        let cm = weighted_sum / tw;

        // 5. Apply turn gain and clamp between -1.0 and 1.0
        let d = cm * turn_gain;
        return Math.max(-1.0, Math.min(1.0, d));
    }

    /**
     * Autonomous exploration with obstacle point-cloud mapping.
     * Updates the distance array and adjusts movement parameters.
     */
    public explore(): number {
        // 1. Determine which index of the target states (s_tg) to check
        // Python: pr.s_tg[1 if wk.pos < 2 else 3]
        let targetIndex = this.wk.pos < 2 ? 1 : 3;
        let angleValue = this.pr.s_tg[targetIndex];

        // 2. Map the angle value to a point-cloud index (0-3)
        // Python: 0 if a > 110 else 1 if a > 90 else 2 if a > 70 else 3
        let d_i = angleValue > 110 ? 0 :
            angleValue > 90 ? 1 :
                angleValue > 70 ? 2 : 3;

        // 3. Update the exploration distance array with a rolling average
        // We multiply by 0.5 to give 50% weight to the new sonar reading
        let currentSonar = this.sonar.distance_cm();
        this.pr.ep_dis[d_i] = (this.pr.ep_dis[d_i] + currentSonar) * 0.5;

        // 4. Update the exploration speed (ep_sp) and direction (ep_di)
        this.set_explore_param();

        // 5. Execute the walk using exploration parameters
        return this.walk(this.ep_sp, this.ep_di);
    }

    /**
     * Executes a specific jumping sequence and manages the auxiliary jump servo.
     * Ported from jump() in Python.
     */
    public jump(): number {
        // 1. Execute the move sequence
        // states: [24, 14, 0, 0]
        // sync_servos (legs): [0, 1, 2, 3] at speed 3
        // async_servos (waist/head): [4, 5] at speed 2
        let md = this.wk.move(
            this.pr,
            [24, 14, 0, 0],
            [0, 1, 2, 3],
            3,
            [4, 5],
            2
        );

        // 2. Check if move completed (md == 0) and gait is at the end (pos == 3)
        if (md == 0 && this.wk.pos == 3) {
            // Transition to Joystick/Manual state
            this.gst = 5;

            // Retract/Reset auxiliary servo 6
            this.wk.servo(6, 0);
        } else {
            // Extend/Activate auxiliary servo 6 during the jump
            this.wk.servo(6, 100);
        }

        return md;
    }

    /**
     * Executes a kick by accelerating the forward walking gait.
     * Returns to joystick mode when the kick completes at specific gait positions.
     */
    public kick(): number {
        // 1. Execute the forward walk states at high speed
        // legs: [0, 1, 2, 3] at speed 3, body/head: [4, 5] at speed 2
        let md = this.wk.move(
            this.pr,
            this.pr.walk_fw_sts,
            [0, 1, 2, 3],
            3,
            [4, 5],
            2
        );

        // 2. Check if the movement step is finished (md == 0)
        // and ensure the gait has reached index 0 or 2 (strike positions)
        if (md == 0 && (this.wk.pos == 0 || this.wk.pos == 2)) {
            // Switch back to Joystick/Manual control state
            this.gst = 5;
        }

        return md;
    }

    /**
     * Set the robot to a neutral standing position.
     * Ported from stand() in Python.
     */
    public stand(): number {
        // 1. Execute transition to neutral state (Index 0)
        // states: [0]
        // sync_list: all servos [0, 1, 2, 3, 4, 5]
        // sync_speed: 2.0 (moderate speed)
        // async_list: [] (none)
        // async_speed: 0.5
        return this.wk.move(
            this.pr,
            [0],
            [0, 1, 2, 3, 4, 5],
            2.0,
            [],
            0.5
        );
    }

    /**
     * Monitors sensors to determine if the robot should exit sleep mode.
     * @returns 1 if the robot should wake up, 0 otherwise.
     */
    public check_wakeup(): number {
        // 1. Calculate tilt deltas (current vs filtered)
        let roll_delta = Math.abs(this.bd_rl - this.bd_rl2);
        let pitch_delta = Math.abs(this.bd_pth - this.bd_pth2);

        // 2. Check for "Wake Up" triggers:
        // - High acceleration (max_g > g_thr)
        // - Loud sound detected
        // - Sudden tilt change > 20 degrees
        if (this.max_g > this.g_thr ||
            input.soundLevel() > 128 || // Check if sound level is "loud" (0-255)
            roll_delta > 20 ||
            pitch_delta > 20) {

            this.alt_l = 10; // Reset alert level to max
            return 1;        // Signal wake up
        }

        // 3. If alert level reaches 0, enter deeper sleep (state -1)
        if (this.alt_l < 1) {
            this.gst = -1;
        }

        return 0; // Remain asleep
    }

    /**
     * Puts the robot into a low-power standby mode.
     * Ported from sleep() in Python.
     */
    public sleep_mode(): void {
        // 1. Refresh IMU data and return to a neutral standing pose
        this.balance_param();
        this.stand();

        // 2. Turn off the 5x5 LED matrix eyes
        this.wk.eyes_ctl(0);

        // 3. Clear the NeoPixel strip to save battery
        this.np.clear();
        this.np.show();

        // 4. Monitor for wake-up triggers (e.g., sound or touch)
        if (this.check_wakeup() == 1) {
            // Return to Idle/Standby state
            this.gst = 0;
            this.talk("I am awake"); // Optional feedback
        }
    }

    /**
     * Main state machine for robot behavior control.
     * Processes the current state (gst) and executes the corresponding behavior.
     */
    public state_machine(): void {
        // 1. Execute the current state's behavior
        // Python: self.st_dict.get(self.gst, self.sleep)()
        let behavior = this.st_dict[this.gst];

        if (behavior) {
            behavior();
        } else {
            // Fallback to sleep if state index is not found
            this.sleep_mode();
        }

        // 2. Handle blinking and state tracking
        if (this.gst >= 0) {
            // Update eye blink animation based on alert level (alt_l)
            this.wk.blink(this.alt_l);

            // Remember last normal state for recovery (e.g., after a fall)
            this.last_state = this.gst;
        }
    }
    /**
     * Executes singing logic using the pxt-billy engine.
     * @param s The phonetic or musical string to be synthesized.
     */
    public sing(s: string): void {
        billy.singShim(s)
    }
    /**
     * Makes the robot introduce itself using text-to-speech.
     * The robot will speak its serial number and name.
     */
    public intro(): void {
        // 1. Combine the identification strings
        this.talk("My name is " + this.sn + " " + this.name);
    }
    /**
     * Adjusts the radio group ID and updates the hardware settings.
     * @param i The amount to adjust the group ID by (positive or negative).
     */
    public incr_group_id(i: number): void {
        // 1. Calculate the new group ID with 0-255 wrapping logic
        this.groupID = (this.groupID + i) % 256;

        // 2. Handle negative results from the modulo (JavaScript specific)
        if (this.groupID < 0) {
            this.groupID += 256;
        }

        // 3. Update the native radio hardware group
        radio.setGroup(this.groupID);

        // 4. Update the 5x5 LED display to show the new channel
        this.show_channel();
    }
    /**
     * Generates a random LED light show on the robot's NeoPixel strip.
     * Ported from random_light() in Python.
     */
    private random_light(): void {
        // 1. Loop through the 4 pixels on the robot's strip
        for (let p = 0; p < 4; p++) {
            // 2. Generate random RGB values (0-128 for moderate brightness)
            let red = Math.randomRange(0, 128);
            let green = Math.randomRange(0, 128);
            let blue = Math.randomRange(0, 128);

            // 3. Set the color for the specific pixel
            // Use neopixel.rgb to combine the values into a single color object
            this.np.setPixelColor(p, neopixel.rgb(red, green, blue));
        }

        // 4. Push the updated colors to the hardware
        this.np.show();
    }
    /**
     * Makes the robot dance with self-balance based on sound analysis.
     */
    public dance(): number {
        let ts = control.millis();
        let ms = input.soundLevel();

        // 1. Check for a musical beat using the MusicLib helper
        let il = this.music.isABeat(ts, ms, 1.1);

        // 2. High-beat logic: Pulse LEDs and flip wiggle direction
        if (ts - this.last_high_b > this.music.period * 0.5) {
            this.dance_l_itv *= -1;
            this.dance_u_itv *= -1;
            this.random_light(); // Trigger NeoPixel animation
            this.last_high_b = ts;
        }

        // 3. Low-beat logic: Change the dance move routine
        if (il && (ts - this.last_low_b > this.music.period * Math.randomRange(8, 16))) {
            // Pick a new move from the approved dance state list
            this.d_st = [this.pr.dance_ok[Math.randomRange(0, this.pr.dance_ok.length - 1)]];
            this.last_low_b = ts;
        }

        // 4. Balance and tilt compensation
        this.balance_param();
        let ft = Math.min(12.0, Math.max(-12.0, this.rl * 0.8 + this.dance_l_itv * 0.2));
        if (Math.abs(ft) < 8) {
            ft = 0;
        }
        let lt = ft + this.dance_l_itv;

        // 5. Apply control vectors to servos
        // Servo 5 (head/body pitch) reacts to sound volume
        this.set_ct([0, 1, 2, 3, 4, 5],
            [ft, lt, ft, lt, this.rl, this.dance_u_itv - ms * 0.001]);

        // 6. Dynamic speed adjustment
        this.d_sp = Math.min(2.5, this.d_sp * 1.015);
        if (this.max_g > 1800) { // If shaking too hard, slow down
            this.d_sp *= 0.9;
        }

        // 7. Execute the movement via the WK instance
        return this.wk.move(this.pr, this.d_st, [0, 1, 2, 3], this.d_sp, [4, 5], this.d_sp);
    }

    // Command Handlers
    public speed(v: number) { this.sp = v * (v > 0 ? this.fw_sp : this.bw_sp); this.gst = 5; }
    public turn(v: number) { this.di = (this.di * 4 + v) * 0.2; }
    public roll(v: number) { this.h_l_bias = (v + this.h_l_bias) * 0.5; }
    public pitch(v: number) { this.h_u_bias = (v * -1 + this.h_u_bias) * 0.5; }
    public button(v: number) { if (v == 0) this.gst = 0; else this.gst = v; }
    public logo(v: number) { this.talk(this.sn); }
    public pose(v: number) { this.r_st = v; this.gst = 0; }
}

let robot = new RobotPu("SN_01", "Peu");
basic.forever(function () {
    robot.update_states();
    robot.state_machine();
    //basic.pause(20)
})

// Register the event listener for incoming string messages
radio.onReceivedString(function (receivedString: string) {
    // 1. Update the timestamp of the last received command
    robot.last_cmd_ts = control.millis();

    // 2. Process #put: Text-to-Speech
    if (receivedString.substr(0, 4) == "#put") {
        robot.talk(receivedString.substr(4));
    }

    // 3. Process #pus: Buffered Singing (6 segments)
    else if (receivedString.substr(0, 4) == "#pus") {
        // Assume s_list is an array of strings defined in the class
        robot.sing(receivedString.substr(4));
    }

    // 4. Process #puhi: Greeting
    else if (receivedString.substr(0, 5) == "#puhi") {
        robot.talk("My friend " + receivedString.substr(5) + " is here");
    }

    // 5. Process #pun: Name/Serial Update
    else if (receivedString.substr(0, 4) == "#pun") {
        robot.sn = receivedString.substr(4);
        robot.intro();
    }
});

// 2. Use it inside the Radio Event
radio.onReceivedValue(function (name: string, value: number) {
    robot.last_cmd_ts = control.millis();

    // 3. Look up the function in the dictionary
    let action = robot.cmdDict[name];

    // 4. If the function exists, execute it (the "noop" equivalent)
    if (action) {
        action(value);
    }
});
// Replace button_a.was_pressed()
input.onButtonPressed(Button.A, function () {
    robot.incr_group_id(1); // Increment radio group
});

// Replace button_b.was_pressed()
input.onButtonPressed(Button.B, function () {
    robot.incr_group_id(-1); // Decrement radio group
});
