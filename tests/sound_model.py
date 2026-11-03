"""sound_model.py - the sound of milestones 0.3-0.8, frame by frame.

What the sound player must write to the TIA, worked out again in
Python from the design (score.py, sfx.py, the rules of the design
and the comments of sound.asm), not from music.py or the
6507 code. The tests compare, after every frame, the six sound
registers of the cartridge with these.

The rules:
- three modes: 0 MUSIC, 1 SOUND FX, 2 SILENT; when the mode
  changes both voices are silenced, any effect stops, and the
  music starts again from its first step;
- the songs (0.8): the theme, GAME OVER, VICTORY (score.SONGS,
  in score.SONG_ORDER; the game keeps 2 x the song). When the
  game starts a song it is as if the mode changed (silence, the
  music from its first step, no effect): this is the silence
  after an end and after a restart. The theme loops; the songs
  that end (end=True) play once, then each voice rests for
  ever;
- MUSIC: voice 0 plays the bass, voice 1 the melody. A step is
  a sixteenth note at score.BPM: 9 frames on NTSC, 8 and 7 in
  turn on PAL (the exact number of frames, rounded so that the
  steps never drift). At the start of a step a voice whose note
  is over takes the next one (at the end of its list it goes
  back to its start) and sets AUDC (the instrument's) and AUDF
  (the nearest pitch on NTSC: the same AUDF on PAL). Every
  frame the volume is the instrument's envelope at the frame
  of the note (60 frames a second; on PAL frame k takes entry
  k * 60 / 50; the last value holds), 0 in a rest and in the
  last frame of every note;
- SOUND FX: voice 1 silent; an effect asked for starts at once
  (a new one replaces the one playing) on voice 0, a frame of
  (AUDC, AUDF, AUDV) at a time; after its last frame AUDV 0;
- SILENT: both volumes 0.
"""
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "game",
                                "assets"))
import score                                    # noqa: E402
import sfx                                      # noqa: E402

FPS = {"ntsc": 60, "pal": 50}
DIV = {4: 2, 12: 6, 8: 1}
NTSC_AUDIO = 3579545.0 / 114
LETTERS = "C C# D D# E F F# G G# A A# B".split()


def pitch(tok):
    m = re.fullmatch(r"([A-G]#?)(-?\d)", tok)
    return 12 * (int(m.group(2)) + 1) + LETTERS.index(m.group(1))


def best_audf(n, audc):
    want = 440.0 * 2 ** ((n - 69) / 12)
    return min(range(32), key=lambda f: abs(math.log2(
        NTSC_AUDIO / (f + 1) / DIV[audc] / want)))


def voice_events(v, song="theme"):
    """[(instrument, (AUDC, AUDF) or None, steps)] of voice v of
    a song, and where the voice goes back to after its last
    event: its "loop" (the start if none); a song that ends
    has a rest of 255 steps more, and goes back to it."""
    out, t, ins, loop = [], 0, None, 0
    sg = score.SONGS[song]
    for item in sg["orders"][v]:
        if item == "loop":
            loop = len(out)
            continue
        if item.startswith("t"):
            t = int(item[1:])
            continue
        for tok in score.PATTERNS[item].split():
            if tok[0] == "@":
                ins = tok[1:]
                continue
            note, steps = tok.split("/")
            if note == "r":
                out.append((ins, None, int(steps)))
            else:
                c = score.INSTRUMENTS[ins]["audc"]
                out.append((ins, (c, best_audf(pitch(note) + t, c)),
                            int(steps)))
    if sg.get("end"):
        loop = len(out)
        out.append((ins, None, 255))
    return out, loop


def at_tv(frames60, tv):
    if tv == "ntsc":
        return list(frames60)
    n = -(-len(frames60) * FPS[tv] // 60)
    return [frames60[k * 60 // FPS[tv]] for k in range(n)]


def steps_of(tv):
    """Frames of the steps, one cycle: the n-th step ends at the
    frame nearest to n x the exact length."""
    num, den = 60 * FPS[tv], score.BPM * 4      # frames a step
    out, n = [], 0
    while True:
        a = (2 * (n + 1) * num + den) // (2 * den)
        b = (2 * n * num + den) // (2 * den)
        out.append(a - b)
        n += 1
        if (n * num) % den == 0:
            return out


_TABLES = {}


def tables(tv):
    """The fixed data of a television, made once (kept out of
    the Sound objects, which the tests copy every frame)."""
    if tv not in _TABLES:
        _TABLES[tv] = dict(
            events=[voice_events(v, song) for song in
                    score.SONG_ORDER for v in (0, 1)],
            env={k: at_tv(i["env"], tv)
                 for k, i in score.INSTRUMENTS.items()},
            fx=[at_tv(sfx.EFFECTS[k], tv) for k in sfx.ORDER],
            steps=steps_of(tv))
    return _TABLES[tv]


class Sound:
    def __init__(self, tv):
        self.tv = tv
        self.reg = dict(C0=0, F0=0, V0=0, C1=0, F1=0, V1=0)
        self.smode = 0
        self.song = 0
        self.reset_music()
        self.fxp = None                 # [effect, frame] or None
        self.ins = [None, None]
        self.note = [None, None]
        self.envi = [0, 0]

    def reset_music(self):
        self.clock = 0
        self.step_i = 0
        self.pos = [0, 0]
        self.left = [0, 0]

    def frame(self, mode, request, song=0, restart=False):
        """One frame: the mode, the effect asked (0: none, 1: the
        first of sfx.ORDER ...), the song (2 x its index in
        score.SONG_ORDER) and whether the game started it in
        this frame. Returns the registers."""
        t = tables(self.tv)
        r = self.reg
        self.song = song
        if mode != self.smode or restart:
            self.smode = mode
            r["V0"] = r["V1"] = 0
            self.fxp = None
            self.reset_music()
        if mode == 2:
            r["V0"] = r["V1"] = 0
        elif mode == 1:
            r["V1"] = 0
            if request:
                self.fxp = [request - 1, 0]
            if self.fxp and self.fxp[1] < len(t["fx"][self.fxp[0]]):
                r["C0"], r["F0"], r["V0"] = \
                    t["fx"][self.fxp[0]][self.fxp[1]]
                self.fxp[1] += 1
            else:
                r["V0"] = 0
                self.fxp = None
        else:
            self.music()
        return dict(r)

    def music(self):
        t = tables(self.tv)
        r = self.reg
        if self.clock == 0:
            self.clock = t["steps"][self.step_i]
            self.step_i = (self.step_i + 1) % len(t["steps"])
            for v in (0, 1):
                if self.left[v] == 0:
                    ev, loop = t["events"][self.song + v]
                    if self.pos[v] == len(ev):
                        self.pos[v] = loop
                    ins, note, n = ev[self.pos[v]]
                    self.pos[v] += 1
                    self.ins[v], self.note[v] = ins, note
                    self.left[v], self.envi[v] = n, 0
                    if note:
                        r[f"C{v}"], r[f"F{v}"] = note
                self.left[v] -= 1
        self.clock -= 1
        for v in (0, 1):
            vol = 0
            if self.note[v] and not (self.left[v] == 0 and
                                     self.clock == 0):
                e = t["env"][self.ins[v]]
                vol = e[min(self.envi[v], len(e) - 1)]
                if self.envi[v] < len(e) - 1:
                    self.envi[v] += 1
            r[f"V{v}"] = vol
