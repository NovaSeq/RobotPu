# 🗣️ Lesson: Giving Robot PU a Voice

In this lesson, we will transform **Robot PU** from a silent dancer into a talking companion! You will learn how to install a "speech engine," generate long descriptive sentences, and create a "Mood Switcher" using the micro:bit buttons.

---

## 1. Background Setup

**Robot PU** is an AI-powered humanoid buddy that uses a **micro:bit** for its brain. To make him talk, we use a special code library called **pxt-billy**.

This library uses "Speech Synthesis" to build words out of digital sounds in real-time. It is based on a classic engine called SAM (Software Automatic Mouth).

---

## 2. Problem Definition

To make Robot PU a great communicator, we need to solve three challenges:

* **The Voice Box**: Teaching the micro:bit how to synthesize speech.
* **Advanced Vocabulary**: Moving beyond simple phrases to long, interesting sentences.
* **Personality Toggles**: Changing PU's voice from a happy Elf to a grumpy Robot on command.

---

## 3. Basic Idea of Solutions

1. **Extensions**: We will use the MakeCode Extension UI to search for and add `pxt-billy`.
2. **Complex Data Structures**: We will expand our `Content` class with adjectives and conjunctions to create longer sentences.
3. **State Management**: We will use a variable to track PU's "mood" and change his vocal preset accordingly.

---

## 4. Implementation

### Step A: Add the Extension

You must teach MakeCode how to speak before the code will work:

1. Open your project at [makecode.microbit.org](https://makecode.microbit.org/).
2. Click **Extensions** at the bottom of the toolbox.
3. Paste this URL into the search bar: `https://github.com/adamish/pxt-billy`.
4. Select the **billy** extension to add it.

### Step B: The Complete Script

Copy and paste this code into your **JavaScript** tab. It includes the advanced word generator and the Button B mood switcher.

```typescript
/**
 * SECTION 1: ADVANCED CONTENT GENERATOR
 */
class Content {
    loc: string[];
    act: string[];
    sub: string[];
    obj: string[];
    adj: string[]; 
    conj: string[];

    constructor() {
        this.sub = ["I", "He", "She", "They", "Robot PU"];
        this.act = ["liked", "saw", "heard", "felt", "loves"];
        this.obj = ["me", "you", "the dance", "the song", "the code"];
        this.loc = ["here", "there", "up", "down", "in the lab"];
        this.adj = ["shiny", "happy", "weird", "fast", "super"];
        this.conj = ["and", "but", "because", "so"];
    }

    private choice(arr: string[]): string {
        return arr[Math.floor(Math.random() * arr.length)];
    }

    // Generates a long: [Sub] [Act] [Adj] [Obj] [Conj] [Loc]
    cute_words(): string {
        return this.choice(this.sub) + " " +
            this.choice(this.act) + " " +
            this.choice(this.adj) + " " +
            this.choice(this.obj) + " " +
            this.choice(this.conj) + " " +
            this.choice(this.loc) + ".";
    }
}

/**
 * SECTION 2: INITIALIZATION
 */
let generator = new Content();
let puMood = 0; // 0 = Elf, 1 = Robot
music.setVolume(150); // Set global volume (0-255)
billy.voicePreset(BillyVoicePreset.Elf); // Start as an Elf

/**
 * SECTION 3: INTERACTION
 */

// BUTTON A: Talk!
input.onButtonPressed(Button.A, function () {
    let phrase = generator.cute_words();
    basic.showIcon(IconNames.SmallSquare); // "Open mouth"
    billy.say(phrase); // Blocking speech command
    basic.showIcon(IconNames.Asleep); // "Close mouth"
});

// BUTTON B: Switch Mood (Elf <-> Robot)
input.onButtonPressed(Button.B, function () {
    if (puMood == 0) {
        puMood = 1;
        billy.voicePreset(BillyVoicePreset.Robot);
        basic.showIcon(IconNames.Angry);
        billy.say("I am a grumpy robot");
    } else {
        puMood = 0;
        billy.voicePreset(BillyVoicePreset.Elf);
        basic.showIcon(IconNames.Happy);
        billy.say("I am a happy elf");
    }
    basic.pause(500);
    basic.showIcon(IconNames.Asleep);
});

```
### How the "Sentence Factory" Works
To help kids understand how **Robot PU** generates sentences, it is best to think of it like a **"Sentence Factory"** or a game of **"Mad Libs."** Below is the updated explanation section for your LearnDash page.
Robot PU doesn't just remember full sentences; he builds them from scratch every time you press a button. This is called **Procedural Generation**.

### The Ingredients (The Lists)

Inside the `Content` class, we create several lists of "parts of speech." Think of these as bins in a factory:

* **Subjects (`sub`)**: Who is doing the action?
* **Actions (`act`)**: What is happening?
* **Adjectives (`adj`)**: What does the thing look like?
* **Objects (`obj`)**: What is being acted upon?
* **Conjunctions (`conj`)**: A "glue" word to connect ideas.
* **Locations (`loc`)**: Where is it happening?

### The Robot's Choice (The `choice` function)

The robot has a secret helper function called `choice`. Whenever PU needs a word, he closes his eyes and picks one random item from a bin.

```typescript
private choice(arr: string[]): string {
    return arr[Math.floor(Math.random() * arr.length)];
}

```

### The Assembly Line (The `cute_words` function)

Finally, PU takes those random choices and glues them together in a specific order with spaces in between.

**The Formula:** `[Subject] + [Action] + [Adjective] + [Object] + [Conjunction] + [Location]`

**An Example Assembly:**

1. **Subject**: "Robot PU"
2. **Action**: "loves"
3. **Adjective**: "shiny"
4. **Object**: "the code"
5. **Conjunction**: "because"
6. **Location**: "in the lab"

**Final Output:** *"Robot PU loves shiny the code because in the lab."*

Even though the grammar might be a little silly, it ensures that Robot PU has thousands of possible things to say, making him feel much more "alive"!

---

## 5. Testing
Code: https://makecode.microbit.org/S81118-63767-88308-72596
1. **Download** the code to your Robot PU.
2. **Toggle Moods**: Press **Button B**. Does PU's face change? Does his voice sound different?
3. **Generate Sentences**: Press **Button A**. Are the sentences longer than before? Does the voice match the mood you picked?
4. **Hardware Check**: On micro:bit V2, sound comes from his chest. On V1, ensure headphones/speakers are on **Pin 0**.

---

## 6. What Can Be Done Next?

* **More Moods**: Add a third state for `BillyVoicePreset.Dalek` to make PU sound like a metallic villain.
* **Touch Interaction**: Use the micro:bit V2 **Touch Logo** to trigger a "Giggle" sound or a special greeting.
* **Chatty Sonar**: Update your sonar code so that when an object is closer than 10cm, PU shouts "Too close!" in his current mood voice.

---

*For more information, visit [robotgyms.com/pu](https://robotgyms.com/pu).*