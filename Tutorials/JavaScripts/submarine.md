
# 🤖 Robot PU: Submarine Sonar Project Wiki

Welcome to the official project repository for **Robot PU (Pair Up)**. Robot PU is an AI-powered humanoid performer designed for high-performance STEM learning. In this project, we transform PU into a deep-sea navigator using his chest-mounted ultrasonic sensor to mimic submarine sonar.

---

## 📂 1. Introduction to Robot PU

**Robot PU** is an interactive STEM buddy controlled by a micro:bit. He is known for his:

* **Advanced Movement**: Performing complex routines like moonwalks and splits with fluid motion.
* **Autopilot Intelligence**: Using sensors to navigate environments and avoid obstacles.
* **Interactive AI**: Synchronizing his dance moves to music beats and communicating via speech synthesis.

---

## 🌊 2. Project: Submarine Sonar Mode

### Problem Definition

We want to give PU a "voice" for his spatial awareness. Instead of silently avoiding objects, PU will emit a "ping" that changes based on proximity.

### The Solution: Sonic Mapping

We use **Mapping** to convert raw distance data into auditory feedback:

* **Pitch Mapping**: 2cm distance = 2000Hz (High) | 100cm distance = 200Hz (Low).
* **Interval Mapping**: 2cm distance = 100ms (Fast) | 100cm distance = 800ms (Slow).

---

## 🛠️ 3. Hardware Configuration

Robot PU uses an **HC-SR04 Ultrasonic Sensor** located on his chest plate.

| Pin | Function | Description |
| --- | --- | --- |
| **P2** | Trigger (Trig) | Sends the ultrasonic burst. |
| **P8** | Echo | Receives the reflected sound wave. |
| **Internal** | Speaker | Outputs the sonar "pings". |

---

## 💻 4. Implementation Script

Copy this code into the **JavaScript** tab of the [MakeCode Editor](https://makecode.microbit.org/).

```typescript
/**
 * SECTION 1: SENSOR DRIVER
 * This class handles the high-speed timing of PU's chest sonar.
 */
class HCSR04 {
    timeout_us: number;
    trig: DigitalPin;
    echo: DigitalPin;

    constructor(trigPin: DigitalPin = DigitalPin.P2, echoPin: DigitalPin = DigitalPin.P8) {
        this.timeout_us = 30000; // Approx 500cm max range
        this.trig = trigPin;
        this.echo = echoPin;
        pins.digitalWritePin(this.trig, 0);
    }

    distance_cm(): number {
        // Trigger the sensor
        pins.digitalWritePin(this.trig, 0);
        control.waitMicros(5);
        pins.digitalWritePin(this.trig, 1);
        control.waitMicros(10);
        pins.digitalWritePin(this.trig, 0);

        // Listen for the echo
        let t = pins.pulseIn(this.echo, PulseValue.High, this.timeout_us);
        if (t <= 0) t = 500;

        // Convert time to cm (speed of sound calculation)
        return t * 0.0171821;
    }
}

/**
 * SECTION 2: INITIALIZATION
 */
let sonar = new HCSR04(DigitalPin.P2, DigitalPin.P8);
music.setVolume(128); // Set micro:bit hardware volume (0-255)

/**
 * SECTION 3: SUBMARINE SONAR LOOP
 * This runs in its own background loop to keep the sonar active.
 */
basic.forever(function () {
    let distance = sonar.distance_cm(); 

    // Only "Ping" if an object is within 100cm (1 meter)
    if (distance > 2 && distance < 100) {
        
        // Closer = Higher Frequency
        let pitch = Math.map(distance, 2, 100, 2000, 200); 
        
        // Closer = Faster Beeps
        let pulseDelay = Math.map(distance, 2, 100, 100, 800); 

        // Play the ping
        music.playTone(pitch, 50); 
        
        // Wait before the next pulse
        basic.pause(pulseDelay);
    } else {
        // Relax if nothing is detected
        basic.pause(500);
    }
});

```

---

## 🧪 5. Testing & Maintenance
Code: https://makecode.microbit.org/_Ft8biP4kugAF
1. **Deployment**: Upload the script via USB to your Robot PU.
2. **Calibration**: Ensure PU's chest sensor is unobstructed.
3. **Material Test**: Try moving different materials toward PU. Hard surfaces (walls) reflect better than soft surfaces (cloth).
4. **Hardware Note**: For micro:bit V1, connect an external speaker to **Pin 0 and GND**.

---

## 🚀 6. Next Steps

* **Visual Radar**: Plot the distance on the micro:bit LED matrix using `led.plotBarGraph`.
* **Talking Robot**: Use the `pxt-billy` extension to make PU say "Object Detected!".
* **Evasive Dance**: Program PU to "Moonwalk" backward if the sonar detects an object closer than 5cm.

---

*For more information, visit [robotgyms.com/pu](https://robotgyms.com/pu).*

Would you like me to help you create the code for the **Visual Radar** on the LED screen?