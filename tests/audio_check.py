"""audio_check.py - what Stella plays, against the sound model.

    check(stella, rom, tv, out_dir) -> dict

1. tools/record_audio.py records the title in Stella, at its
   normal speed, from power-on (the MUSIC mode): about 24
   seconds, the eight bars and the start of the second time;
2. tests/model.py (with sound_model.py) gives the six sound
   registers of every frame of the same title, and
   tests/tia_audio.py makes the sound of them;
3. the recording is aligned with the model's sound: the start
   on 15 seconds (0.9: on 5 seconds the march matched itself
   two beats later too), then every two seconds (the loudness
   of 5 ms slices, correlated), and again within 50 ms around
   every note: Stella at its normal speed
   keeps time with the sound card, not with the frames, and
   slides by some hundredths of a second;
4. for every note of the melody longer than 0.45 s, in the
   middle 60 % of the note: the frequency of the strongest
   peak within 50 cents of the TIA frequency (FFT with a Hann
   window, 2^18 points), and the likeness of the two spectra
   (80-3000 Hz, cosine of the smoothed magnitudes).
Passes when every measured note is within MAX_CENTS of the TIA
frequency and every likeness is at least MIN_LIKE. If a recording
does not pass, a second one is made (ATTEMPTS); the result keeps
what every attempt gave.

The WAV and MP3 of the recording, and the WAV of the model,
stay in out_dir, for listening.
"""
import math
import os
import subprocess
import sys
import wave

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import model                                    # noqa: E402
import tia_audio                                # noqa: E402

MAX_CENTS = 15
MIN_LIKE = 0.7
SECONDS = 24
HOP = 220                       # 5 ms at 44 100 Hz
START_WINDOW = 3000             # 15 s of slices to find the start
AUDIO = {"ntsc": 3579545.0 / 114, "pal": 3546894.0 / 114}
FRAME_CLOCKS = {"ntsc": 524, "pal": 624}


def _read(path):
    import numpy as np
    w = wave.open(path)
    return np.frombuffer(w.readframes(w.getnframes()),
                         dtype="<i2").astype(float) / 32767


def _env(x, np):
    n = len(x) // HOP
    return np.sqrt((x[:n * HOP].reshape(n, HOP) ** 2).mean(1))


ATTEMPTS = 2


def check(stella, rom, tv, out_dir, record=True):
    """Records and measures; when a recording does not pass,
    Stella records once more (ATTEMPTS in all): a recording at
    normal speed depends on the timing of the computer (a slow
    start of Stella has misaligned one in 21 October 2026,
    every note against its neighbour). The result says how
    many recordings it took, and what the first ones gave."""
    tries = []
    for n in range(ATTEMPTS if record else 1):
        r = check_once(stella, rom, tv, out_dir, record)
        tries.append(dict(passed=r["passed"],
                          worst_cents=r.get("worst_cents"),
                          least_like=r.get("least_like"),
                          why=r["why"][:3]))
        if r["passed"] or not r.get("recorded"):
            break
    r["attempts"] = tries
    return r


def check_once(stella, rom, tv, out_dir, record=True):
    import numpy as np
    os.makedirs(out_dir, exist_ok=True)
    wav = os.path.join(out_dir, f"stella_title_{tv}.wav")
    if record:
        r = subprocess.run([sys.executable, os.path.join(
            ROOT, "tools", "record_audio.py"), "--stella", stella,
            "--seconds", str(SECONDS), rom, wav],
            capture_output=True, text=True)
        if r.returncode or not os.path.exists(wav):
            return dict(tv=tv, recorded=False, why=["no recording: "
                        + (r.stderr or r.stdout)[-200:]],
                        passed=False)
    rec = _read(wav)
    # the model: the title from power-on, nothing pressed
    g = model.Game(tv)
    frames = []
    fps = AUDIO[tv] / FRAME_CLOCKS[tv]
    for _ in range(int(SECONDS * fps) + 60):
        g.step()
        a = g.audio
        frames.append((a["C0"], a["F0"], a["V0"], a["C1"], a["F1"],
                       a["V1"]))
    smp, rate = tia_audio.render(frames, tv)
    tia_audio.to_wav(smp, rate, os.path.join(
        out_dir, f"model_title_{tv}.wav"))
    exp = np.array(tia_audio.resample(smp, rate, 44100))
    exp -= exp.mean()
    er, ee = _env(rec, np), _env(exp, np)
    if len(er) < 1600:
        return dict(tv=tv, recorded=True, seconds=len(rec) / 44100,
                    why=["recording too short"], passed=False)
    # the start: the best of 400 slices (2 s), comparing 15
    # seconds (0.9: with 5 seconds the march matched itself as
    # well 1.2 s later, two beats, and in some recordings that
    # won by a few thousandths: every note was then measured
    # 1.2 s off)
    win = min(START_WINDOW, len(ee), len(er) - 400)
    best = max(((np.corrcoef(er[o:o + win], ee[:win])[0, 1], o)
                for o in range(0, min(400, len(er) - win))))
    offs, prev = [(0, best[1])], best[1]
    for t0 in range(400, len(ee) - 400, 400):
        cand = []
        for d in range(-40, 41):
            o = prev + d
            if t0 + o < 0 or t0 + o + 400 > len(er):
                continue
            cand.append((np.corrcoef(er[t0 + o:t0 + o + 400],
                                     ee[t0:t0 + 400])[0, 1], o))
        if cand and max(cand)[0] > 0.5:
            prev = max(cand)[1]
            offs.append((t0, prev))
    xs = [o[0] for o in offs]
    ys = [o[1] for o in offs]
    # the notes of the melody (voice 1)
    notes, cur = [], None
    for k, fr in enumerate(frames):
        key = (fr[3], fr[4])
        if cur is None or key != cur[0] or fr[5] == 0:
            if cur and cur[2] - cur[1] >= int(0.45 * fps):
                notes.append(cur)
            cur = (key, k, k) if fr[5] else None
        else:
            cur = (cur[0], cur[1], k)
    N = 1 << 18
    freqs = np.fft.rfftfreq(N, 1 / 44100)
    band = (freqs > 80) & (freqs < 3000)
    ker = np.ones(31) / 31
    rows, why = [], []
    for (c, f), k0, k1 in notes:
        want = AUDIO[tv] / (f + 1) / {4: 2, 12: 6}[c]
        t0, t1 = k0 / fps, (k1 + 1) / fps
        a, b = t0 + 0.2 * (t1 - t0), t1 - 0.2 * (t1 - t0)
        # the slide here: the one of the nearest two seconds,
        # then the best within 50 ms over this note and the
        # notes around it (1 s of loudness)
        o = int(round(float(np.interp(a * 44100 / HOP, xs, ys))))
        h0 = max(0, int(t0 * 44100 / HOP) - 100)
        h1 = h0 + 200
        cand = [(np.corrcoef(er[h0 + o + d:h1 + o + d],
                             ee[h0:h1])[0, 1], o + d)
                for d in range(-10, 11)
                if 0 <= h0 + o + d and h1 + o + d <= len(er)
                and h1 <= len(ee)]
        if cand:
            o = max(cand)[1]
        o *= HOP
        s0, s1 = int(a * 44100 + o), int(b * 44100 + o)
        if s1 > len(rec) or int(b * 44100) > len(exp):
            continue
        seg = rec[s0:s1]
        sp = np.abs(np.fft.rfft(seg * np.hanning(len(seg)), N))
        near = (freqs > want * 2 ** (-50 / 1200)) & \
            (freqs < want * 2 ** (50 / 1200))
        got = float(freqs[np.argmax(sp * near)])
        cents = 1200 * math.log2(got / want)
        e0, e1 = int(a * 44100), int(b * 44100)
        se = np.abs(np.fft.rfft(exp[e0:e1] * np.hanning(e1 - e0), N))
        x = np.convolve(sp[band], ker, "same")
        y = np.convolve(se[band], ker, "same")
        like = float(np.dot(x, y) / np.linalg.norm(x) /
                     np.linalg.norm(y))
        rows.append(dict(t=round(t0, 2), audf=f, want=round(want, 2),
                         got=round(got, 2), cents=round(cents, 1),
                         like=round(like, 3)))
        if abs(cents) > MAX_CENTS:
            why.append(f"{t0:.2f} s: {cents:+.1f} cents")
        if like < MIN_LIKE:
            why.append(f"{t0:.2f} s: likeness {like:.2f}")
    if len(rows) < 15:
        why.append(f"only {len(rows)} notes measured")
    slide = (ys[-1] - ys[0]) * HOP / 44100
    return dict(tv=tv, recorded=True, seconds=round(len(rec) / 44100,
                                                     1),
                start=round(best[1] * HOP / 44100, 3),
                start_likeness=round(float(best[0]), 3),
                slide_seconds=round(slide, 3), notes=rows,
                worst_cents=max((abs(r["cents"]) for r in rows),
                                default=None),
                mean_cents=round(sum(r["cents"] for r in rows) /
                                 max(1, len(rows)), 2),
                least_like=min((r["like"] for r in rows),
                               default=None),
                why=why, passed=not why)


if __name__ == "__main__":
    import json
    print(json.dumps(check(sys.argv[1], sys.argv[2], sys.argv[3],
                           sys.argv[4]), indent=1))
