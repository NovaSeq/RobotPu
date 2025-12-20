# 🚢 Lesson: Robot PU the Submarine Sonar Operator

In this lesson, we will promote **Robot PU** to the rank of Submarine Sonar Operator! You will learn how to turn PU's chest sensor into a high-tech tracking system that talks to you and sounds a "Red Alert" when an object gets too close.

---

## 1. Background Setup (Introduction)

**Robot PU** is an interactive humanoid buddy equipped with an **ultrasonic sonar sensor** right on his chest. This sensor works just like the sonar on a submarine: it sends out high-frequency sound waves and listens for them to bounce back. By measuring the time it takes for the echo to return, PU can "see" in the dark.

---

## 2. Problem Definition

A professional sonar operator needs to react differently based on how close a target is. We need to:

1. **Constantly Scan**: Keep the sonar "pinging" so we always have live data.
2. **Report Findings**: Use a digital voice to tell us the exact distance in centimeters.
3. **Sound the Alarm**: If an object enters the "Danger Zone," PU must switch to a loud siren and shout a warning.

---

## 3. Basic Idea of Solutions

* **The Sonar Driver**: We use a custom `HCSR04` class to handle the Trigger (P2) and Echo (P8) pins on PU's chest.
* **Mathematical Mapping**: We use `Math.map` to turn distance into sound. Closer objects create higher-pitched and faster "pings".
* **Logic Zones**: We use `if-else` statements to create three states: **Danger** (Red Alert), **Detection** (Voice Reporting), and **Clear Skies** (Idle).

---

## 4. Implementation

### Step A: Add the Extension

To make PU talk, you must add the speech library:

1. Open **Extensions** in the MakeCode editor.
2. Search for: `https://github.com/adamish/pxt-billy`.
3. Select **billy** to add it to your project.

### Step B: The Operator Script

Copy this complete script into your **JavaScript** tab:

```typescript
/** * HCSR04 Driver Class for Robot PU's Chest Sonar
 */
class HCSR04 {
    trig: DigitalPin; echo: DigitalPin;
    constructor(t: DigitalPin, e: DigitalPin) {
        this.trig = t; this.echo = e;
        pins.digitalWritePin(this.trig, 0);
    }
    distance_cm(): number {
        pins.digitalWritePin(this.trig, 0);
        control.waitMicros(5);
        pins.digitalWritePin(this.trig, 1);
        control.waitMicros(10);
        pins.digitalWritePin(this.trig, 0);
        let t = pins.pulseIn(this.echo, PulseValue.High, 30000);
        return (t <= 0) ? 500 : t * 0.0171821;
    }
}

// 1. Setup the Hardware and Voice
let sonarDevice = new HCSR04(DigitalPin.P2, DigitalPin.P8);
billy.voicePreset(BillyVoicePreset.LittleRobot);
music.setVolume(150);

basic.forever(function () {
    // Round the distance to avoid stuttering
    let distance = Math.round(sonarDevice.distance_cm());

    // --- SONAR PING LOGIC ---
    // Higher pitch and faster beeps as objects get closer
    let pitch = Math.map(distance, 2, 100, 2000, 200);
    let pulseDelay = Math.map(distance, 2, 100, 100, 800);
    music.playTone(pitch, 50);
    basic.pause(pulseDelay);

    // --- CASE 1: DANGER ZONE (Too Close!) ---
    if (distance > 0 && distance < 6) {
        music.setVolume(255); // Max Volume for emergency!
        basic.showIcon(IconNames.Skull);
        music.playMelody("C5 P C5 P C5 P C5 P", 500);
        billy.say("Danger, stop!");
    }
    // --- CASE 2: DETECTION ZONE (Reporting Distance) ---
    else if (distance >= 6 && distance < 20) {
        music.setVolume(220); // Normal reporting volume
        basic.showIcon(IconNames.Target);
        billy.say("Distance " + distance);
        basic.pause(500);
    }
    // --- CASE 3: CLEAR SKIES ---
    else {
        music.setVolume(150);
        basic.showIcon(IconNames.Asleep);
        basic.pause(500);
    }
});

```

---

## 5. Technical Explanation: How it Works

### 🕵️ The Sonar Driver

The `HCSR04` class acts as the "translator" between the micro:bit and the physical world. It sends a precisely timed 10-microsecond pulse to Pin 2, which triggers the sensor to scream an ultrasonic sound. It then waits on Pin 8 for the echo to return. The code calculates distance using the constant `0.0171821`, which accounts for the speed of sound and the fact that the sound has to travel to the object and back.

### 📊 Understanding Mapping

We use `Math.map` to create an **inverse relationship**. Usually, as a number goes up, its output goes up. However, in sonar, we want the opposite: as distance goes **down**, we want the pitch and speed to go **up**. This creates the "urgent" submarine sound that tells you a collision is coming.

### 🗣️ Why do we use `Math.round()`?

Ultrasonic sensors can be "jittery". They might report 15.2cm one millisecond and 14.8cm the next. By using `Math.round()`, we turn these into a solid "15," which prevents Robot PU from sounding confused or stuttering when he speaks the distance.

---

## 6. Testing & Next Steps
Code: https://makecode.microbit.org/S81118-63767-88308-72596
1. **Download** the code to your Robot PU.
2. **Tracking Test**: Hold your hand 15cm from PU's chest. He should say "Distance 15".
3. **The Red Alert**: Move your hand very close (under 6cm). PU should turn up his volume and shout "Danger, stop!".

**What can be done next?**

* **Automatic Evasion**: When "Danger" is detected, add a command to make PU moonwalk backward.
* **Visual Radar**: Use `led.plotBarGraph` to show the distance on the screen alongside the pings.

Adding a **Visual Radar** to Robot PU allows you to see the distance on the 5x5 LED matrix while hearing the sonar pings. We use the `led.plotBarGraph` command, which automatically lights up the LEDs like a progress bar based on the distance value.

### 🛠️ Visual Radar Implementation

Replace your current `basic.forever` loop with this updated version. It includes the logic to display the distance on PU's face.

```typescript
basic.forever(function () {
    // Round the distance for stable readings
    let distance = Math.round(sonarDevice.distance_cm());

    // --- VISUAL RADAR ---
    // Plots a bar graph on the 5x5 LED matrix
    // We use 50cm as the 'max' value for the graph
    led.plotBarGraph(distance, 50);

    // --- SONAR PING LOGIC ---
    let pitch = Math.map(distance, 2, 100, 2000, 200);
    let pulseDelay = Math.map(distance, 2, 100, 100, 800);
    music.playTone(pitch, 50);
    basic.pause(pulseDelay);

    // --- CASE 1: DANGER ZONE (< 6cm) ---
    if (distance > 0 && distance < 6) {
        music.setVolume(255);
        // The skull icon will temporarily override the bar graph
        basic.showIcon(IconNames.Skull); 
        music.playMelody("C5 P C5 P C5 P C5 P", 500);
        billy.say("Danger, stop!");
    }
    // --- CASE 2: DETECTION ZONE (6cm - 20cm) ---
    else if (distance >= 6 && distance < 20) {
        music.setVolume(220);
        billy.say("Distance " + distance);
        basic.pause(500);
    }
    // --- CASE 3: CLEAR SKIES ---
    else {
        music.setVolume(150);
        // No icon here so the Bar Graph stays visible
    }
});

```

---

### 🧐 How it Works

* **`led.plotBarGraph(value, high)`**: This command takes the current `distance` and compares it to the `high` value (50cm in this case). If the distance is 50cm or more, the whole screen lights up; if it's 10cm, only the bottom row lights up.
* **Visual Feedback**: This creates a "Radar" effect where you can see the bars drop as you get closer to Robot PU's chest.
* **Icon Overriding**: Commands like `basic.showIcon` will temporarily draw over the bar graph. Once the icon sequence finishes, the `forever` loop will draw the bar graph again on the next scan.

### 🚀 What's Next?


