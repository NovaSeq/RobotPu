import random

class Content:
    def __init__(self):
        self.notes = ["#70REYY", "#62MIYY", "#58FAOR", "#52SOHW", "#46LAOR", "#42TIYY", "#39DOWW",
                      "#35REYY", "#31MIYY", "#29FAOR", "#26SOHW", "#23LAOR", "#21TIYY", "#20DOWW"]
        self.chord = [[0, 3, 5], [0, 2, 4, 6], [0, 2, 4, 7], [0, 1, 2, 3]]
        self.pattern = [[0, 0, 0, 0], [0, 0, 1], [0, 1, 0], [1, 0, 0], [1, 1], [3]]
        self.loc = ["here", "there", "up", "down", "left", "right", "front", "back", ""]
        self.act = ["liked", "saw", "heard", "felt", ""]
        self.sub = ["I", "He", "She", "They", ""]
        self.obj = ["me", "you", "him", "her", "them", "it", "the dance", "the song", ""]
        self.sentences = ["I am so tired.", "Let's go, go, go!", "Be careful!", "Life lies in motion.",
                          "Let's pair up!", "I am stuck!", "New song:", "Easy peasy!", "I like my backpack",
                          "I love you", "You are the best!", 'yeh!', 'woohoo!']

    def compose_song(self):
        song, b = [], len(self.notes)
        c, w = random.choice(self.chord), random.choice(self.pattern)
        i = 0
        while i < 16:
            k = random.randint(0, b - 1)
            for j in w:
                m = (k + random.choice(c) + random.choice([-1, 0, 0, 0, 0, 1])) % b
                n = self.notes[m]
                if j >= 1 and random.randint(0, 8) == 0:
                    song.extend([n] + [self.notes[(m + random.choice([-1, 0, 1])) % b] for _ in range(j)])
                else:
                    song.append(n + n[-1] * 4 * j)
                i += j + 1
            c, w = random.choice(self.chord), random.choice(self.pattern)
        return "".join(song)

    def cute_words(self):
        return "{} {} {} {}.".format(random.choice(self.sub),
                                     random.choice(self.act),
                                     random.choice(self.obj),
                                     random.choice(self.loc))