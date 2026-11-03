"""music.py - score.py and sfx.py made into bytes for the TIA.

    python3 game/assets/music.py        (prints the tuning)

build() returns the lines of generated/bank5.asm and the facts
for the tests:

- the note table: one entry for each (instrument, pitch) of the
  score, with AUDC (the instrument's) and the AUDF that gives
  the nearest pitch on NTSC:
      f = colour clock / 114 / (AUDF + 1) / divider(AUDC)
  (dividers: AUDC 4 -> 2, AUDC 12 -> 6; the colour clock is
  3 579 545 Hz on NTSC, 3 546 894 on PAL). PAL uses the same
  AUDF: every note is 15.9 cents lower, all by the same amount,
  so the two voices stay in tune with each other (the nearest
  PAL note one by one would put E3 a quarter tone above E4);
- the two voices of each song (score.SONG_ORDER: the
  theme and the two pieces of the end) as byte streams: $FE n
  chooses instrument n, then a note (index in the note table,
  0 a rest) and its length in steps; $FF goes back to the loop
  point. A song that ends (score: end=True) ends each voice
  with a rest of 255 steps, and its loop point is that rest:
  after the song, silence for ever. VS_LO, VS_HI and VLOOP
  are indexed by 2 x song + voice; SONG_THEME, SONG_GAMEOVER,
  SONG_VICTORY are 2 x the song (the value of song in the
  RAM);
- the step: a sixteenth note at score.BPM, in frames of each
  television: on NTSC 9, on PAL 8 and 7 in turn (7.5 on
  average); STEPLEN is the repeating pattern;
- the envelopes of the instruments and the effects, written at
  60 frames a second: on PAL frame k takes the entry playing at
  the moment k / 50 s (entry k * 60 / 50).
Every table that differs between NTSC and PAL is written twice,
chosen with IF PAL.
"""
import math
import os
import re
import sys
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import score                                          # noqa: E402
import sfx                                            # noqa: E402

NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A",
         "A#", "B"]
CLOCK = {"ntsc": 3579545.0, "pal": 3546894.0}
FPS = {"ntsc": 60, "pal": 50}
DIVIDER = {4: 2, 5: 2, 12: 6, 13: 6, 1: 15, 6: 31, 14: 93}
MAX_CENTS = 25          # a worse NTSC note stops the build


def midi(tok):
    m = re.fullmatch(r"([A-G]#?)(-?\d)", tok)
    if not m:
        raise ValueError(f"not a note: {tok}")
    return 12 * (int(m.group(2)) + 1) + NAMES.index(m.group(1))


def name(n):
    return f"{NAMES[n % 12]}{n // 12 - 1}"


def tia_hz(audc, audf, tv):
    return CLOCK[tv] / 114 / (audf + 1) / DIVIDER[audc]


def nearest(n, audc, tv):
    """(AUDF, Hz, cents) of the TIA note nearest to MIDI n."""
    want = 440.0 * 2 ** ((n - 69) / 12)
    best = None
    for f in range(32):
        g = tia_hz(audc, f, tv)
        c = 1200 * math.log2(g / want)
        if best is None or abs(c) < abs(best[2]):
            best = (f, g, c)
    return best


def events(voice, song="theme"):
    """[(instrument, MIDI or None, steps)] of a voice of a song,
    and the index of its loop point."""
    out, loop, t, ins = [], 0, 0, None
    for item in score.SONGS[song]["orders"][voice]:
        if item == "loop":
            loop = len(out)
            continue
        if re.fullmatch(r"t[+-]\d+", item):
            t = int(item[1:])
            continue
        for tok in score.PATTERNS[item].split():
            if tok.startswith("@"):
                ins = tok[1:]
                continue
            note, steps = tok.split("/")
            n = None if note == "r" else midi(note) + t
            out.append((ins, n, int(steps)))
    return out, loop


def step_pattern(tv):
    """Frames of each step, repeating: Bresenham on the exact
    number of frames of a sixteenth note."""
    f = Fraction(60 * FPS[tv], score.BPM * 4)
    pat, i = [], 0
    while True:
        a = math.floor((i + 1) * f + Fraction(1, 2))
        b = math.floor(i * f + Fraction(1, 2))
        pat.append(a - b)
        i += 1
        if (i * f).denominator == 1:
            return pat


def resample(frames60, tv):
    """A list written at 60 frames a second, for this TV."""
    if tv == "ntsc":
        return list(frames60)
    n = math.ceil(len(frames60) * FPS[tv] / 60)
    return [frames60[k * 60 // FPS[tv]] for k in range(n)]


def hexs(vals):
    return ",".join(f"${v:02X}" for v in vals)


def table(label, vals, per=11):
    out = [label] if label else []
    for i in range(0, len(vals), per):
        out.append(f"        .byte {hexs(vals[i:i + per])}")
    return out


def check():
    bad = []
    if list(score.SONGS) != score.SONG_ORDER or \
            score.SONG_ORDER[0] != "theme":
        bad.append("the songs: the theme first, SONG_ORDER")
    for song, sg in score.SONGS.items():
        lens = []
        for v in range(2):
            ev, _ = events(v, song)
            lens.append(sum(s for _, _, s in ev))
            if any(i not in score.INSTRUMENTS for i, _, _ in ev):
                bad.append(f"{song} voice {v}: unknown instrument")
            if any(not 1 <= s <= 255 for _, _, s in ev):
                bad.append(f"{song} voice {v}: a length out of "
                           "1-255")
        if len(sg["orders"]) != 2 or len(set(lens)) != 1 or \
                lens[0] != sg["bars"] * 16:
            bad.append(f"{song}: voices of {lens} steps, not "
                       f"{sg['bars'] * 16}")
    for name_, ins in score.INSTRUMENTS.items():
        if ins["audc"] not in DIVIDER or not ins["env"] or \
                any(not 0 <= x <= 15 for x in ins["env"]):
            bad.append(f"instrument {name_}")
    for k, e in sfx.EFFECTS.items():
        if any(not (0 <= c <= 15 and 0 <= f <= 31 and 0 <= v <= 15)
               for c, f, v in e):
            bad.append(f"effect {k}")
    return bad


def build():
    """Lines of bank5.asm, and the facts for the tests."""
    ins_names = list(score.INSTRUMENTS)
    voices = [(song, v, events(v, song)) for song in score.SONG_ORDER
              for v in (0, 1)]
    notes = []                       # (instrument, MIDI)
    for _, _, (ev, _) in voices:
        for ins, n, _ in ev:
            if n is not None and (ins, n) not in notes:
                notes.append((ins, n))
    notes.sort(key=lambda x: (ins_names.index(x[0]), x[1]))
    info = dict(bpm=score.BPM, instruments=ins_names, notes=[],
                songs=score.SONG_ORDER, streams=[], loops=[],
                step={}, env={}, sfx={}, tuning={})
    lines = ["; generated by music.py - bank 5: the music and the",
             "; effects (score.py, sfx.py)", ""]
    audf = [nearest(n, score.INSTRUMENTS[i]["audc"], "ntsc")[0]
            for i, n in notes]
    for tv in ("ntsc", "pal"):
        rows, worst = [], 0.0
        for (ins, n), f in zip(notes, audf):
            audc = score.INSTRUMENTS[ins]["audc"]
            g = tia_hz(audc, f, tv)
            c = 1200 * math.log2(g / (440.0 * 2 ** ((n - 69) / 12)))
            rows.append(dict(instrument=ins, note=name(n), audc=audc,
                             audf=f, hz=round(g, 2),
                             cents=round(c, 1)))
            worst = max(worst, abs(c))
        info["tuning"][tv] = dict(notes=rows, worst=round(worst, 1))
    if info["tuning"]["ntsc"]["worst"] > MAX_CENTS:
        raise SystemExit("a note more than "
                         f"{MAX_CENTS} cents off on NTSC")
    # the note table: index 0 is the rest
    lines += ["; the notes: AUDC and AUDF (index 0: a rest)"]
    lines += table("NOTE_C", [0] + [score.INSTRUMENTS[i]["audc"]
                                    for i, _ in notes])
    lines += table("NOTE_F", [0] + audf)
    # the streams: each song, each voice
    labels = []
    for song, v, (ev, loop) in voices:
        data, cur, pos_of = [], None, []
        for i, (ins, n, s) in enumerate(ev):
            pos_of.append(len(data))
            if i == loop:
                cur = None      # the loop chooses its instrument
            if ins != cur:
                data += [0xFE, ins_names.index(ins)]
                cur = ins
            idx = 0 if n is None else notes.index((ins, n)) + 1
            data += [idx, s]
        lp = pos_of[loop]
        if score.SONGS[song].get("end"):
            lp = len(data)      # the end: a rest, for ever
            data += [0, 255]
        data.append(0xFF)
        lab = f"V_{song.upper()}{v}"
        labels.append(lab)
        lines += [f"; {song}, voice {v}: $FE instrument, note "
                  "and steps,", "; $FF loop"]
        lines += table(lab, data)
        info["streams"].append(data)
        info["loops"].append(lp)
        if len(data) > 255:
            raise SystemExit(f"{song} voice {v}: more than 255 "
                             "bytes")
    lines += ["; the streams by 2 x song + voice"]
    for lab, op in (("VS_LO", "<"), ("VS_HI", ">")):
        lines.append(lab)
        for i in range(0, len(labels), 2):
            lines.append("        .byte   " + ", ".join(
                op + x for x in labels[i:i + 2]))
    lines += table("VLOOP", info["loops"])
    for i, song in enumerate(score.SONG_ORDER):
        lines.append(f"SONG_{song.upper()} = {2 * i}")
    # steps and envelopes, each television
    for tv in ("ntsc", "pal"):
        lines.append("        IF " + ("!PAL" if tv == "ntsc"
                                     else "PAL"))
        pat = step_pattern(tv)
        info["step"][tv] = pat
        lines += table("STEPLEN", pat)
        lines.append(f"STEPS_N = {len(pat)}")
        data, start, last = [], [], []
        info["env"][tv] = {}
        for i in ins_names:
            e = resample(score.INSTRUMENTS[i]["env"], tv)
            info["env"][tv][i] = e
            start.append(len(data))
            last.append(len(e) - 1)
            data += e
        lines += table("ENV_START", start)
        lines += table("ENV_LAST", last)
        lines += table("ENV_DATA", data)
        # effects: three tables, AUDC, AUDF and AUDV of
        # each frame, indexed by the frame; an AUDC of $FF
        # ends an effect, and index 0 is an empty effect
        sc, sf, sv, so = [0xFF], [0], [0], []
        info["sfx"][tv] = {}
        for k in sfx.ORDER:
            fr = resample(sfx.EFFECTS[k], tv)
            info["sfx"][tv][k] = fr
            so.append(len(sc))
            for c, f, v in fr:
                sc.append(c)
                sf.append(f)
                sv.append(v)
            sc.append(0xFF)
            sf.append(0)
            sv.append(0)
        if len(sc) > 256:
            raise SystemExit("effects: more than 256 frames")
        lines += table("SFX_START", so)
        lines += table("SFX_C", sc)
        lines += table("SFX_F", sf)
        lines += table("SFX_V", sv)
        lines.append("        ENDIF")
    for i, k in enumerate(sfx.ORDER, 1):
        lines.append(f"SFX_{k.upper()} = {i}")
    info["notes"] = [dict(instrument=i, note=name(n))
                     for i, n in notes]
    return lines, info


if __name__ == "__main__":
    bad = check()
    if bad:
        sys.exit("\n".join(bad))
    _, inf = build()
    for tv in ("ntsc", "pal"):
        t = inf["tuning"][tv]
        print(f"{tv}: steps {inf['step'][tv]}, worst "
              f"{t['worst']} cents")
        for r in t["notes"]:
            print(f"  {r['instrument']:5s} {r['note']:4s} AUDC "
                  f"{r['audc']:2d} AUDF {r['audf']:2d} "
                  f"{r['hz']:8.2f} Hz {r['cents']:+6.1f}")
