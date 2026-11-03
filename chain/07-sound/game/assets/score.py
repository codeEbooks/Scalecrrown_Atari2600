"""score.py - the Scalecrown theme, for the two TIA voices.

Everything here was written for this game: the melody and the
bass line. Nothing was sampled or copied from other music.

The theme is in E minor and 4/4, at 100 beats a minute: a slow,
dark march under the crypt, the bass on eighth notes, the melody
above it, in two parts: part A, eight bars, and part B (eight
bars that go up to C and G major and come back on B, the bass
in quarter notes). Two pieces for the end screens follow: a
lament for GAME OVER (three bars, falling) and a fanfare
for VICTORY (four bars in E major: the minor of the crypt turns
major), which play once and then stay silent.

The key was chosen on the notes the TIA has: a TIA note is
the colour clock / 114
/ (AUDF + 1) / the divider of AUDC, so only some pitches exist.
In E minor every note of the melody (AUDC 4, divider 2) and of
the bass (AUDC 12, divider 6) is within 20 cents of the right
pitch on NTSC (part A within 18.4; the rest adds G3 and C#6,
19.3 and 19.7 cents off); on PAL all of them are 16 cents
lower, the same for both voices, so the two voices stay in tune
with each other. music.py writes the tables and prints the
error of every note.

Format:
- one step is a sixteenth note; BPM gives the tempo, the same in
  seconds on NTSC and PAL;
- notes: C, C#, D, D#, E, F, F#, G, G#, A, A#, B and the octave
  (C4 is middle C); "E5/4" lasts four steps, "r/2" is a rest;
- "@lead" chooses the instrument of the notes that follow;
- order lists: pattern names, "t+5" / "t-4" transpositions in
  semitones for that voice, "loop" (where the voice goes back to
  at the end; the start if there is none);
- songs: the theme loops; a song with end=True plays once
  and then rests for ever (music.py ends each of its voices with
  a rest that loops on itself).
"""

BPM = 100

# AUDC: the waveform (4: pure tone, divider 2, the high voice;
# 12: pure tone, divider 6, an octave and a fifth lower).
# env: the volume (AUDV, 0-15) of each frame of a note at 60
# frames a second; the last value holds. Every note is silent in
# its last frame, so that two equal notes are heard as two.
INSTRUMENTS = {
    "lead": dict(audc=4, env=[12, 11, 10, 9, 9, 8, 8, 8, 7]),
    "bass": dict(audc=12, env=[10, 9, 8, 7, 6]),
}

PATTERNS = {
    # the melody, part A, over Em | C | Am | B | Em | C | Am B | Em
    "lead_a": "@lead E5/4 B4/2 E5/2 G5/4 F#5/2 E5/2 "
              "G5/6 A5/2 G5/4 E5/4 "
              "A5/4 C6/4 B5/2 A5/2 G5/4 "
              "F#5/8 D#5/4 B4/4 "
              "E5/4 G5/2 B5/2 C6/4 B5/2 G5/2 "
              "A5/6 G5/2 E5/4 C5/4 "
              "C5/4 A5/4 F#5/4 D#5/4 "
              "E5/12 r/4",

    # the bass, one bar for each chord, eighth notes
    "bass_em": "@bass E3/2 E3/2 B3/2 E3/2 E3/2 B3/2 E4/2 B3/2",
    "bass_c": "@bass C4/2 C4/2 E4/2 C4/2 C4/2 E4/2 C4/2 E4/2",
    "bass_am": "@bass A3/2 A3/2 E4/2 A3/2 A3/2 E4/2 A4/2 E4/2",
    "bass_b": "@bass B3/2 B3/2 F#3/2 B3/2 B3/2 F#4/2 B3/2 D#4/2",
    "bass_am_b": "@bass A3/2 A3/2 E4/2 A3/2 B3/2 B3/2 F#3/2 D#4/2",
    "bass_end": "@bass E3/2 E3/2 B3/2 E3/2 E3/4 r/4",
}

PATTERNS.update({
    # part B of the theme, over C | G | Am | Em | C | D | B |
    # B7, back to part A
    "lead_b": "@lead E5/4 G5/4 C6/6 B5/2 "
              "B5/4 G5/4 D5/8 "
              "A5/4 C6/4 B5/2 A5/2 E5/4 "
              "G5/12 r/4 "
              "E5/2 G5/2 C6/4 C6/2 B5/2 A5/4 "
              "A5/4 F#5/4 D5/8 "
              "D#5/4 F#5/4 B5/8 "
              "A5/4 F#5/4 D#5/4 B4/4",
    # the bass of part B, quarter notes
    "bassq_c": "@bass C4/4 G3/4 C4/4 G3/4",
    "bassq_g": "@bass G3/4 D4/4 G3/4 D4/4",
    "bassq_am": "@bass A3/4 E4/4 A3/4 E4/4",
    "bassq_em": "@bass E3/4 B3/4 E3/4 B3/4",
    "bassq_d": "@bass D4/4 A3/4 D4/4 F#3/4",
    "bassq_b": "@bass B3/4 F#3/4 B3/4 F#3/4",
    "bassq_b7": "@bass B3/4 D#4/4 F#4/4 A4/4",
    # GAME OVER: a lament, Em | Am B | Em, falling
    "lead_over": "@lead B5/6 A5/2 G5/4 E5/4 "
                 "C6/4 A5/4 F#5/4 D#5/4 "
                 "E5/8 B4/8",
    "bass_over": "@bass E3/8 B3/8 A3/8 B3/8 E3/16",
    # VICTORY: a fanfare in E major, E | A | F# B | E
    "lead_win": "@lead B4/2 E5/2 G#5/2 B5/6 G#5/2 B5/2 "
                "C#6/4 B5/2 A5/2 G#5/4 F#5/4 "
                "F#5/2 G#5/2 A5/2 B5/2 C#6/4 A5/4 "
                "B5/4 G#5/2 B5/2 E6/8",
    "bass_win": "@bass E3/4 B3/4 E4/4 B3/4 "
                "A3/4 E4/4 C#4/4 E4/4 "
                "F#3/4 C#4/4 B3/4 D#4/4 "
                "E3/8 E4/8",
})

# the theme, 16 bars: parts A and B, then the voices go back to
# their start
ORDERS = [
    # voice 0: the bass
    ["bass_em", "bass_c", "bass_am", "bass_b",
     "bass_em", "bass_c", "bass_am_b", "bass_end",
     "bassq_c", "bassq_g", "bassq_am", "bassq_em",
     "bassq_c", "bassq_d", "bassq_b", "bassq_b7"],
    # voice 1: the melody
    ["lead_a", "lead_b"],
]
BARS = 16

# the songs of the cartridge, in this order: the theme
# (the title and the game), GAME OVER, VICTORY
SONGS = {
    "theme": dict(orders=ORDERS, bars=BARS),
    "gameover": dict(orders=[["bass_over"], ["lead_over"]], bars=3,
                     end=True),
    "victory": dict(orders=[["bass_win"], ["lead_win"]], bars=4,
                    end=True),
}
SONG_ORDER = ["theme", "gameover", "victory"]
