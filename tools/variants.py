"""variants.py - the guided variants and the breaks of the chain
of the book: for each step two changes the reader is
led to make (a variant: the game changes and keeps its time) and
one that breaks something on purpose (a break: what goes wrong
and why). tools/make_variants.py makes and proves each of them.

A change is a list of lines of the step's folder replaced, each
written as it is and as it becomes (one line each, found once).
What is claimed, proved against the step itself (the same
inputs: the head of the step's route, tests/verify_chain.py, up
to the picture named by `until`, and 30 frames more):
  timing   True: every frame 262/312 lines, VSYNC of 228 cycles,
           the writes to the TIA in their windows; False: not so
  seam     False: the seam of player 1 is not where it must be
  ram      the game differs, first in one of these variables
           ("same": never; the scratch of the kernels and the
           pointers to the tables, which move when the code or the
           data change size, are not the game)
  picture  a picture of Stella differs from the step's
  audio    the sound registers differ
"""

VARIANTS = [
    # --- step 1: the first room ---------------------------------
    dict(id="1a", step=1, kind="variant",
         title="The Upper Crypt in blue",
         text="The floor of level 1 takes another hue: one number "
              "in rooms.py, and build_assets.py writes new colour "
              "tables; the kernel does not change.",
         change=[("game/assets/rooms.py",
                  "            floor=0xC0, floor_lum=(0, 6), light=80, "
                  "shimmer=False,",
                  "            floor=0x80, floor_lum=(0, 6), light=80, "
                  "shimmer=False,")],
         until="40 frames later",
         claims=dict(timing=True, ram="same", picture=True)),
    dict(id="1b", step=1, kind="variant",
         title="Sir Roderick comes in further west",
         text="The column where he starts, in dungeon.py: new_game "
              "takes it from START_X.",
         change=[("game/assets/dungeon.py",
                  'START = dict(room=1, x=73, top=17, facing="right")',
                  'START = dict(room=1, x=41, top=17, facing="right")')],
         until="40 frames later",
         claims=dict(timing=True, ram=["kx"], picture=True)),
    dict(id="1x", step=1, kind="break",
         title="A WSYNC forgotten",
         text="Take out the WSYNC at the top of each course: line "
              "A0 starts where line B3 ends, its stores land in the "
              "wrong cycles (colours and playfield change in the "
              "middle of the lines), and the frame loses a line: "
              "261, and the television loses the picture.",
         change=[("game/src/room_kernel.asm",
                  "k_top:  sta     WSYNC",
                  "k_top:")],
         until="40 frames later",
         claims=dict(timing=False, picture=True)),
    # --- step 2: Sir Roderick -----------------------------------
    dict(id="2a", step=2, kind="variant",
         title="A faster walk",
         text="90 pixels a second instead of 60 (rules.py): the "
              "whole part and the fraction a frame change for "
              "each television.",
         change=[("game/assets/rules.py",
                  "WALK_PX_S = 60          # pixels a second, left and "
                  "right",
                  "WALK_PX_S = 90          # pixels a second, left and "
                  "right")],
         until="thrust right",
         claims=dict(timing=True, ram=["kx", "hacc", "kdist",
                                       "kpose"], picture=True)),
    dict(id="2b", step=2, kind="variant",
         title="A longer thrust",
         text="0.4 seconds instead of 0.2 (rules.py): THRUST_FRAMES.",
         change=[("game/assets/rules.py",
                  "THRUST_S = 0.2          # the thrust of the sword, "
                  "seconds",
                  "THRUST_S = 0.4          # the thrust of the sword, "
                  "seconds")],
         until="thrust right",
         claims=dict(timing=True, ram=["thrust"])),
    dict(id="2x", step=2, kind="break",
         title="The HMOVE forgotten",
         text="Take out the HMOVE of HUD line 28: RESP0 puts Sir "
              "Roderick at the coarse column only, 15 pixels at a "
              "time; the fine move never comes.",
         change=[("game/src/hud.asm",
                  "        sta     HMOVE           ;  2",
                  "")],
         until="walking right",
         claims=dict(timing=True, ram="same", picture=True)),
    # --- step 3: the dungeon ------------------------------------
    dict(id="3a", step=3, kind="variant",
         title="The water shimmers twice as fast",
         text="prep_room takes bit 2 of the frame counter instead "
              "of bit 3 to choose the colour table of the water.",
         change=[("game/src/main.asm",
                  "        and     #8",
                  "        and     #4")],
         until=9,
         claims=dict(timing=True, ram="same", picture=True)),
    dict(id="3b", step=3, kind="variant",
         title="A red score",
         text="The colour of the digits of the HUD, in look.py.",
         change=[("game/assets/look.py",
                  "HUD_SCORE_COLOUR = 0x1E",
                  "HUD_SCORE_COLOUR = 0x46")],
         until="from the west",
         claims=dict(timing=True, ram="same", picture=True)),
    dict(id="3x", step=3, kind="break",
         title="The 48-pixel line three cycles early",
         text="Take out the NOP of HUD48: the last four writes of "
              "each line come three cycles before the beam leaves "
              "the copies they change, and the digits break up.",
         change=[("game/src/hud.asm",
                  "        nop",
                  "")],
         until="from the west",
         claims=dict(timing=True, ram="same", picture=True)),
    # --- step 4: keys and doors ---------------------------------
    dict(id="4a", step=4, kind="variant",
         title="Richer chests",
         text="1 500 points for a chest (rules.py): CHEST_BCD.",
         change=[("game/assets/rules.py",
                  "CHEST_POINTS = 500",
                  "CHEST_POINTS = 1500")],
         until="room 0: the chest open",
         claims=dict(timing=True, ram=["score", "score+1",
                                       "score+2"], picture=True)),
    dict(id="4b", step=4, kind="variant",
         title="The spikes stay up longer",
         text="Two seconds up instead of one (rules.py): SPK_UP.",
         change=[("game/assets/rules.py",
                  "SPIKES_UP_S = 1.0",
                  "SPIKES_UP_S = 2.0")],
         until="room 3: no key",
         claims=dict(timing=True, ram=["spk", "spup"])),
    dict(id="4x", step=4, kind="break",
         title="PF2 never written in the room",
         text="Take out the store of PF2 at the end of line B3, the "
              "only one in the room since player 1 came into the "
              "kernel: every course keeps the PF2 of the first, and "
              "the middle of the room is wrong.",
         change=[("game/src/room_kernel.asm",
                  "        sty     PF2             ; 61+ after the right "
                  "half",
                  "")],
         until="room 0: the chest open",
         claims=dict(timing=True, ram="same", picture=True)),
    # --- step 5: the serpents -----------------------------------
    dict(id="5a", step=5, kind="variant",
         title="Slower serpents in the first level",
         text="20 pixels a second instead of 38 (rules.py): CRAWL.",
         change=[("game/assets/rules.py",
                  "SERPENT_PX_S = {1: 38, 2: 42, 3: 46, 4: 49}",
                  "SERPENT_PX_S = {1: 20, 2: 42, 3: 46, 4: 49}")],
         until="room 2: bitten",
         claims=dict(timing=True, ram=["SC+65", "SC+60", "SC+61",
                                       "SC+62", "SC+63", "SC+66",
                                       "zcoarse"])),
    dict(id="5b", step=5, kind="variant",
         title="A softer bite",
         text="A bite takes one unit instead of three (rules.py): "
              "BITE_DAMAGE.",
         change=[("game/assets/rules.py",
                  "BITE_DAMAGE = 3          # easier: 2",
                  "BITE_DAMAGE = 1          # easier: 2")],
         until="room 2: bitten",
         claims=dict(timing=True, ram=["energy"], picture=True)),
    dict(id="5x", step=5, kind="break",
         title="The seam without RESP1",
         text="Take out the RESP1 of the seam: player 1 is never "
              "moved to the serpent of the band below, which is "
              "drawn at the column of the thing above.",
         change=[("game/src/room_kernel.asm",
                  "        sta     RESP1           ; 19 + 5 x zcoarse "
                  "(24-69)",
                  "")],
         until="room 2: the serpent killed",
         claims=dict(timing=True, seam=False, ram="same",
                     picture=True)),
    # --- step 6: the Serpent King -------------------------------
    dict(id="6a", step=6, kind="variant",
         title="Five blows beat the King",
         text="KING_HITS 5 (rules.py), and a time between two spits "
              "for each blow (SPIT_S has one for each).",
         change=[("game/assets/rules.py",
                  "KING_HITS = 10          # blows of the sword to beat "
                  "him",
                  "KING_HITS = 5           # blows of the sword to beat "
                  "him"),
                 ("game/assets/rules.py",
                  "SPIT_S = (1.6, 1.5, 1.4, 1.3, 1.2, 1.1, 1.0, 0.9, "
                  "0.8, 0.7)",
                  "SPIT_S = (1.6, 1.4, 1.2, 1.0, 0.8)")],
         until="room 15: the King beaten",
         claims=dict(timing=True, ram=["SC+74", "score", "score+1",
                                       "score+2", "SC+70"])),
    dict(id="6b", step=6, kind="variant",
         title="Slower venom",
         text="90 pixels a second instead of 112 (rules.py): "
              "VEN_INT and VEN_FRAC.",
         change=[("game/assets/rules.py",
                  "VENOM_PX_S = 112         # easier: 90",
                  "VENOM_PX_S = 90          # easier: 90")],
         until="room 15: the venom from behind",
         claims=dict(timing=True, ram=["SC+71", "SC+73"])),
    dict(id="6x", step=6, kind="break",
         title="The venom never switched on",
         text="Store the venom's bit at $2D, an address the TIA "
              "does not use, instead of ENAM1 ($1E), in the lines B "
              "of the throne kernel: the same cycles, the venom "
              "flies and wounds in the logic, but nothing draws it. "
              "(Taking the store out would also bring every store "
              "after it three cycles earlier: the PF2 at the end of "
              "the line comes at cycle 59, which the tests forbid.)",
         change=[("game/src/throne_kernel.asm",
                  "        sta     ENAM1           ; 20 the venom: bit 1",
                  "        sta     $2D             ; 20 the venom: bit 1")],
         until="room 15: the King spits",
         claims=dict(timing=True, ram="same", picture=True)),
    # --- step 7: the sound --------------------------------------
    dict(id="7a", step=7, kind="variant",
         title="A faster theme",
         text="140 beats a minute instead of 100 (score.py): the "
              "steps of STEPLEN are shorter.",
         change=[("game/assets/score.py",
                  "BPM = 100",
                  "BPM = 140")],
         # (the route of step 7 plays in SOUND FX from its fourth
         # frame: the theme is heard again at the end, MUSIC
         # chosen with SELECT)
         until="SELECT in the game: the music again",
         claims=dict(timing=True, ram=["mclock", "mstep"],
                     audio=True)),
    dict(id="7b", step=7, kind="variant",
         title="A higher blip for a serpent killed",
         text="The first frames of the effect of a kill with a "
              "lower AUDF (sfx.py): the blip starts higher.",
         change=[("game/assets/sfx.py",
                  '    "kill": [(12, 16, 12), (12, 13, 12), '
                  '(12, 10, 11),',
                  '    "kill": [(12, 12, 12), (12, 9, 12), '
                  '(12, 6, 11),')],
         # (the route's blows land at once: the effect heard is
         # the kill, which takes the place of the swish)
         until="a corridor",
         claims=dict(timing=True, ram="same", audio=True)),
    dict(id="7x", step=7, kind="break",
         title="A hiss left on",
         text="Make ef_end return at once: the last volume of an "
              "effect stays in AUDV0, and its hiss goes on until "
              "the next effect.",
         change=[("game/src/sound.asm",
                  "ef_end: lda     #0",
                  "ef_end: rts")],
         until="the grate closed",
         claims=dict(timing=True, ram=["sfxi"], audio=True)),
    # --- step 8: the title and the end screens ------------------
    dict(id="8a", step=8, kind="variant",
         title="The end screen waits longer for the button",
         text="Two seconds instead of one (rules.py): END_FRAMES.",
         change=[("game/assets/rules.py",
                  "END_S = 1.0",
                  "END_S = 2.0")],
         until="back to the title after VICTORY",
         claims=dict(timing=True, ram=["won", "screen"])),
    dict(id="8b", step=8, kind="variant",
         title="A longer GAME OVER",
         text="Everything stops for two seconds instead of one "
              "before the end screen (rules.py): GO_FRAMES.",
         change=[("game/assets/rules.py",
                  "GAME_OVER_S = 1.0",
                  "GAME_OVER_S = 2.0")],
         until="the GAME OVER screen",
         claims=dict(timing=True, ram=["over", "screen"],
                     picture=True)),
    dict(id="8x", step=8, kind="break",
         title="The lament never starts",
         text="Take out the $FF in smode at GAME OVER: the song "
              "changes, but the player does not see a new song and "
              "goes on reading the streams from where they were.",
         change=[("game/src/things.asm",
                  "        sta     smode           ; silences what "
                  "played)",
                  "")],
         until="the GAME OVER screen",
         claims=dict(timing=True, ram=["smode", "mclock", "mstep",
                                       "vpos", "vleft", "venv",
                                       "vins", "vnote", "sfxi"],
                     audio=True)),
    # --- step 9: the hunt ---------------------------------------
    dict(id="9a", step=9, kind="variant",
         title="A gentler sprint",
         text="The serpents that chase him sprint a little slower "
              "(rules.py): SPRI and SPRF.",
         change=[("game/assets/rules.py",
                  "SPRINT_PX_S = {1: 50, 2: 52, 3: 54, 4: 56}",
                  "SPRINT_PX_S = {1: 40, 2: 44, 3: 48, 4: 50}")],
         until="room 2: the serpent killed",
         claims=dict(timing=True, ram=["SC+77", "SC+60", "SC+61",
                                       "SC+62", "SC+63", "SC+66",
                                       "zcoarse"])),
    dict(id="9b", step=9, kind="variant",
         title="They come back sooner",
         text="Two seconds instead of four after a serpent dies "
              "(rules.py): RESPAWN_FRAMES.",
         change=[("game/assets/rules.py",
                  "RESPAWN_S = 4.0",
                  "RESPAWN_S = 2.0")],
         until="room 2: the serpent back",
         claims=dict(timing=True, ram=["SC+75", "SC+76"])),
    dict(id="9x", step=9, kind="break",
         title="A serpent that never comes back",
         text="Take out the jsr respawn: the count of a dead "
              "serpent reaches 0 and nothing happens.",
         change=[("game/src/things.asm",
                  "        jsr     respawn",
                  "")],
         until="room 2: the serpent back",
         claims=dict(timing=True, ram=["SC+64", "SC+60", "SC+61",
                                       "SC+62", "SC+63", "SC+66",
                                       "zcoarse"], picture=True)),
]
