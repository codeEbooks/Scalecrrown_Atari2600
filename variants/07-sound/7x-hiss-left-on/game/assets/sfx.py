"""sfx.py - the sound effects of Scalecrown, for the TIA.

Written for this game. An effect is a list of frames at 60
frames a second: (AUDC, AUDF, AUDV) for each frame. On PAL (50
frames a second) music.py takes, for frame k, the entry that is
playing at the same moment, k * 60 / 50: the effect lasts the
same time on both televisions.

Effects play on voice 0 in the SOUND FX mode; the music and
the effects never sound together (the modes are exclusive).

AUDC 8 is the noise of the 9-bit counter; a lower AUDF is a
higher, thinner hiss. The effects: the sword; the chest, the
door and the hurt of the spikes; the bite, the blow that kills
a serpent and GAME OVER; for the Serpent King his spit, the
parry of the shield, a blow on him, his end, and VICTORY (the
crown breaks, a fanfare); and the steps of a stair. AUDC 4
and 12 are pure tones (divided by 2 and by 6), AUDC 7 a buzz,
AUDC 15 a low rumble. All the effects together stay under 255
frames (music.py: three tables, one byte a frame each).
"""

EFFECTS = {
    # the thrust of the sword: a short, bright swish that falls
    # and fades, about 0.2 seconds (the thrust is 0.2 s)
    "sword": [(8, 1, 12), (8, 1, 13), (8, 2, 12), (8, 2, 11),
              (8, 3, 10), (8, 3, 9), (8, 4, 8), (8, 5, 7),
              (8, 6, 5), (8, 7, 4), (8, 8, 3), (8, 9, 2)],
    # the chest opens: E5 G5 B5 E6 rising, the last one fades
    "chest": [(4, 23, 10)] * 4 + [(4, 19, 11)] * 4 +
             [(4, 15, 12)] * 4 + [(4, 11, 12)] * 4 +
             [(4, 11, 10), (4, 11, 8), (4, 11, 6), (4, 11, 4),
              (4, 11, 2)],
    # a door opens: the clank of the lock, then a low call
    # that rises
    "door": [(8, 24, 15), (8, 24, 13), (8, 28, 10), (8, 31, 6)] +
            [(12, 23, 10)] * 3 + [(12, 19, 10)] * 3 +
            [(12, 15, 11)] * 3 + [(12, 11, 11)] * 6 +
            [(12, 11, 8), (12, 11, 6), (12, 11, 4), (12, 11, 2)],
    # the spikes hurt: a short buzz that falls
    "hurt": [(7, 20, 12), (7, 20, 10), (7, 24, 8), (7, 24, 6),
             (7, 28, 4), (7, 28, 2)],
    # a serpent bites: a sharp hiss, then a low thud
    "bite": [(8, 4, 15), (8, 4, 13), (8, 7, 11), (15, 12, 10),
             (15, 16, 8), (15, 20, 6), (15, 24, 4), (15, 28, 2)],
    # the sword kills a serpent: a blip that rises, then a
    # hiss that fades (it is gone)
    "kill": [(12, 16, 12), (12, 13, 12), (12, 10, 11),
             (12, 8, 10), (8, 3, 10), (8, 2, 8), (8, 1, 6),
             (8, 1, 4), (8, 0, 2)],
    # GAME OVER: B5 A5 G5 F#5 falling to E5, which fades
    "gameover": [(4, 15, 12)] * 6 + [(4, 17, 11)] * 6 +
                [(4, 19, 10)] * 6 + [(4, 20, 9)] * 6 +
                [(4, 23, 10)] * 8 +
                [(4, 23, v) for v in (8, 6, 5, 4, 3, 2, 1)],
}

# --- the Serpent King -------------------------
# the spit: a short wet hiss that falls
EFFECTS["spit"] = [(8, 6, 10), (8, 8, 9), (8, 10, 8), (8, 12, 6),
                   (8, 14, 4), (8, 16, 2)]
# the parry: the venom on the oak shield, a bright knock
EFFECTS["parry"] = [(4, 4, 14), (4, 4, 12), (4, 5, 10), (4, 5, 8),
                    (4, 6, 6), (4, 6, 4), (4, 7, 3), (4, 7, 2)]
# a blow on the King: a thud, then his growl
EFFECTS["king_hit"] = [(15, 10, 15), (15, 12, 13), (15, 14, 11),
                       (3, 20, 10), (3, 22, 9), (3, 24, 8),
                       (3, 26, 6), (3, 28, 4), (3, 30, 3),
                       (3, 31, 2)]
# the King beaten: a long growl that falls and fades
EFFECTS["king_dies"] = [(3, 8 + i // 2, 15 - i // 2)
                        for i in range(24)]
# VICTORY: the crown breaks (a crash), then E5 G5 B5 E6 rising,
# the last one held and fading
EFFECTS["victory"] = [(8, 2, 15), (8, 3, 13), (8, 4, 11),
                      (8, 6, 9), (8, 8, 7), (8, 10, 5), (8, 12, 4),
                      (8, 14, 3)] + \
    [(4, 23, 12)] * 6 + [(4, 19, 12)] * 6 + [(4, 15, 12)] * 6 + \
    [(4, 11, 13)] * 14 + [(4, 11, v) for v in (10, 8, 6, 4, 2)]

# --- the stairs ---------------------------------------------
# a stair, down or up: three steps on the stone, low thuds
# (AUDC 15), each a little deeper, with silence between them
EFFECTS["stair"] = [(15, 10, 11), (15, 10, 7), (0, 0, 0), (0, 0, 0),
                    (15, 14, 10), (15, 14, 6), (0, 0, 0), (0, 0, 0),
                    (15, 18, 9), (15, 18, 5), (15, 18, 2)]

# effect numbers in the cartridge: 0 is "no effect"
ORDER = ["sword", "chest", "door", "hurt", "bite", "kill",
         "gameover", "spit", "parry", "king_hit", "king_dies",
         "victory", "stair"]
