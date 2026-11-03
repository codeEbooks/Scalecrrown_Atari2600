"""tia_audio.py - the sound of the TIA, made from its registers.

A small model, to listen to what the program writes and to
compare it with what Stella plays. It is not an emulator of the
whole chip: it knows the waveforms Scalecrown uses.

The TIA makes its sound at the audio clock, the colour clock /
114: two ticks every line (31 399.5 Hz on NTSC, 31 113.1 on
PAL). Each voice divides it by AUDF + 1; every time the divider
runs out, the waveform chosen by AUDC takes a step:
- AUDC 4, 5: pure tone, the output turns over at every step
  (a square wave of clock / 114 / (AUDF + 1) / 2);
- AUDC 12, 13: pure tone, turning over every third step
  (divider 6);
- AUDC 8: the 9-bit noise counter;
- AUDC 0, 11: the output stays at 1 (silent unless AUDV
  changes);
- anything else: the 4-bit counter (a buzz), enough for this
  model.
The output of a voice is AUDV when the waveform is 1, else 0;
the two voices are added. The registers are taken at the start
of every frame (they change in the overscan, between frames).

    render(frames, tv) -> (samples 0..1 at the audio clock, rate)
    to_wav(samples, rate, path, out_rate=44100)
"""
import struct
import wave

CLOCK = {"ntsc": 3579545.0, "pal": 3546894.0}
LINES = {"ntsc": 262, "pal": 312}


def _poly(bits, taps):
    """The sequence of an LFSR of `bits` bits."""
    n = (1 << bits) - 1
    s = n
    out = []
    for _ in range(n):
        out.append(s & 1)
        fb = ((s >> taps[0]) ^ (s >> taps[1])) & 1
        s = (s >> 1) | (fb << (bits - 1))
    return out


POLY4 = _poly(4, (0, 1))
POLY9 = _poly(9, (0, 4))


class Voice:
    def __init__(self):
        self.div = 0
        self.third = 0
        self.out = 1
        self.p4 = 0
        self.p9 = 0

    def tick(self, audc, audf):
        """One audio clock; returns the output bit."""
        self.div += 1
        if self.div <= audf:
            return self.out
        self.div = 0
        c = audc & 15
        if c in (0, 11):
            self.out = 1
        elif c in (4, 5):
            self.out ^= 1
        elif c in (12, 13):
            self.third += 1
            if self.third == 3:
                self.third = 0
                self.out ^= 1
        elif c == 8:
            self.p9 = (self.p9 + 1) % len(POLY9)
            self.out = POLY9[self.p9]
        else:
            self.p4 = (self.p4 + 1) % len(POLY4)
            self.out = POLY4[self.p4]
        return self.out


def render(frames, tv):
    """frames: [(AUDC0, AUDF0, AUDV0, AUDC1, AUDF1, AUDV1)], one
    per frame. Returns samples (0..1) at the audio clock."""
    per_frame = 2 * LINES[tv]
    v = [Voice(), Voice()]
    out = []
    for c0, f0, a0, c1, f1, a1 in frames:
        for _ in range(per_frame):
            s = a0 * v[0].tick(c0, f0) + a1 * v[1].tick(c1, f1)
            out.append(s / 30.0)
    return out, CLOCK[tv] / 114


def resample(samples, rate, out_rate):
    n = int(len(samples) * out_rate / rate)
    out = []
    for i in range(n):
        x = i * rate / out_rate
        k = int(x)
        t = x - k
        a = samples[k]
        b = samples[k + 1] if k + 1 < len(samples) else a
        out.append(a + (b - a) * t)
    return out


def to_wav(samples, rate, path, out_rate=44100):
    """16-bit mono WAV, the DC taken away."""
    s = resample(samples, rate, out_rate)
    mean = sum(s) / max(1, len(s))
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(out_rate)
        w.writeframes(b"".join(
            struct.pack("<h", max(-32767, min(32767, int(
                (x - mean) * 52000)))) for x in s))
