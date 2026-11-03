"""art.py - the figures of Scalecrown, as text.

Every figure is 8 pixels wide and is drawn one line of the
television per line of text: '#' is a pixel on, '.' off. The
colour is given per pair of lines (the kernel changes the
colour of a figure every two lines): a colour name before each
pair. Figures face right; the kernel mirrors them with REFP.

COLOURS: name -> NTSC value. The PAL value is the nearest PAL
colour as Stella draws it (palette_stella.json), unless PAL_FIX
gives one.
"""

COLOURS = {
    # figures
    "plume": 0x44, "plume_lo": 0x42,
    "steel_hi": 0x0E, "steel": 0x0C, "steel_lo": 0x08,
    "blade": 0x0E,
    "visor": 0x06,
    "gold_hi": 0x1E, "gold": 0x1C, "gold_lo": 0x1A,
    "tunic": 0x1C,
    "oak": 0x24, "oak_hi": 0x28, "oak_lo": 0x22, "leather": 0xF4,
    "leather_lo": 0xF2,
    "skin": 0x3C,
    "snake_hi": 0x1C, "snake": 0xC8, "snake_lo": 0xD6,
    "snake_belly": 0xDC, "tongue": 0x46,
    "king_hi": 0xBA, "king": 0xB6, "king_lo": 0xB4,
    "king_eye": 0x46, "crown_hi": 0x1E, "crown": 0x2C,
    "gem_red": 0x46, "gem_green": 0xC8, "gem_blue": 0x88,
    "black": 0x00,
    # the venom of the King (bit 1 set: it switches
    # missile 1 on the pair of his mouth), the King's flash
    # (bit 1 clear)
    "venom": 0xCA, "king_flash": 0x0C,
}
PAL_FIX = {}


def fig(text):
    """'colour: ####....' lines -> [(pattern, colour), ...]."""
    out = []
    colour = None
    for ln in text.strip().splitlines():
        ln = ln.strip()
        if not ln:
            continue
        if ":" in ln:
            colour, ln = (s.strip() for s in ln.split(":", 1))
        out.append((ln, colour))
    return out


# --- Sir Roderick, 24 lines, facing right --------------------
# plume, great helm with the visor, yellow surcoat over the
# arms, belt, legs in steel, leather boots

_KNIGHT_TOP = """
plume:    ...##...
          ..###...
plume_lo: .##.....
          ..###...
steel_hi: .#####..
          .######.
steel:    .###..#.
          .######.
steel_lo: ..####..
          ...##...
gold_hi:  ..####..
          .######.
gold:     ##.####.
          #..#####
gold_lo:  #..####.
          ...####.
leather:  ..#####.
          ..####..
"""

KNIGHT_STAND = fig(_KNIGHT_TOP + """
gold:     ..####..
          .######.
steel_lo: .##..##.
          .##..##.
leather:  .##..##.
          ###..###
""")

KNIGHT_WALK1 = fig(_KNIGHT_TOP + """
gold:     ..####..
          .######.
steel_lo: ##....##
          ##....##
leather:  ##.....#
          ###....#
""")

KNIGHT_WALK2 = fig(_KNIGHT_TOP + """
gold:     ..####..
          ..####..
steel_lo: ...##...
          ...##...
leather:  ...###..
          ..####..
""")

# The thrust: the sword arm forward. The blade
# itself is missile 0, beside the hand, on the pair of lines
# coloured "blade"; the missile takes the colour of the pair.
# The kernel turns the missile on and off with the colour of
# each pair: bit 1 of the colour (the lowest bit of the
# brightness) is written to ENAM0 as well. So in this pose
# only the "blade" pair has bit 1 set, on NTSC and on PAL
# (check() and look.figure_colour see to it).

KNIGHT_THRUST = fig("""
plume:    ...##...
          ..###...
plume:    .##.....
          ..###...
steel:    .#####..
          .######.
steel:    .###..#.
          .######.
steel_lo: ..####..
          ...##...
gold:     ..####..
          .######.
blade:    ##.#####
          #..#####
gold:     #..####.
          ...####.
leather:  ..#####.
          ..####..
gold:     ..####..
          .######.
steel_lo: ##....##
          ##....##
leather:  ##.....#
          ###....#
""")
BLADE_POSE = "knight_thrust"
BLADE_COLOUR = "blade"

# The parry: the oak shield raised in front of
# him (the side he faces) against the venom of the Serpent
# King; one colour a pair, so the pairs of the shield are oak.

KNIGHT_PARRY = fig("""
plume:    ...##...
          ..###...
plume_lo: .##.....
          ..###...
steel_hi: .#####..
          .######.
steel:    .###..#.
          .######.
steel_lo: ..####..
          ...##...
oak_hi:   ..######
          .#######
oak:      .#######
          .#######
oak:      ..######
          ..######
oak_lo:   ...#####
          ....###.
gold:     ..####..
          .######.
steel_lo: .##..##.
          .##..##.
leather:  .##..##.
          ###..###
""")

# --- the serpent, 16 lines, facing right ---------------------
# a banded serpent raised on its coils

SERPENT_A = fig("""
snake_hi:  ..###...
           .#####..
snake_hi:  .##.###.
           .#######
snake_lo:  ..##.#..
           ...##...
snake_hi:  ....##..
           ....##..
snake_lo:  ...##...
           ..##....
snake_hi:  ..##.##.
           .##..###
snake_lo:  .##...##
           .##..##.
snake_hi:  ..#####.
           ...###..
""")

SERPENT_B = fig("""
snake_hi:  ..###...
           .#####..
snake_hi:  .##.###.
           .#####.#
snake_lo:  ..##....
           ...##...
snake_hi:  ...##...
           ....##..
snake_lo:  ....##..
           ...##...
snake_hi:  ..##.##.
           .##..###
snake_lo:  ##...##.
           ##..##..
snake_hi:  .#####..
           ..###...
""")

# --- the Serpent King, 40 lines, drawn twice as wide ---------
# the crown, the hood with two eyes (holes: the floor shows
# through), the red mouth, the body in an S, the coils

_KING_TOP = """
crown_hi:  ...#.#.#
           ...#####
crown:     ...#####
           ..######
king_hi:   .#######
           ########
king:      ##.##.##
           ########
king:      ########
           .######.
"""

_KING_BODY = """
king:      ...##...
           ...##...
king_hi:   ...###..
           ..####..
king:      ..####..
           ..###...
king_lo:   ..##....
           .##.....
king:      .##.....
           .##.....
king_lo:   ..##....
           ...##...
king:      ....##..
           ....###.
king_lo:   .....##.
           ....###.
king:      ..#####.
           .###..##
king_lo:   ##.....#
           ##....##
"""

KING_A = fig(_KING_TOP + """
king_eye:  ..####..
           ...##...
""" + _KING_BODY + """
king:      .#######
           ..#####.
king_lo:   .######.
           ##.....#
king:      #######.
           .######.
king_lo:   ..####..
           ........
""")

KING_B = fig(_KING_TOP + """
king_eye:  .#.##.#.
           .#....#.
""" + _KING_BODY + """
king:      .######.
           ..######
king_lo:   ..######
           .##....#
king:      ########
           .######.
king_lo:   ..####..
           ........
""")

# --- the Scalecrown, 8 lines ---------------------------------

CROWN = fig("""
crown_hi:  #..##..#
           #..##..#
crown:     ##.##.##
           ########
gem_red:   #.#..#.#
           ########
crown:     ########
           .######.
""")

# the crown struck: its pieces, where it was
CROWN_BROKEN = fig("""
crown_hi:  #....#..
           .#.....#
crown:     ...#.#..
           #.......
gem_red:   ..#....#
           .#..#...
crown:     #.##..##
           .##.###.
""")

# --- the chest, open and closed; the gate -------
# the chest of the cover: oak with gold bands and a keyhole,
# 12 lines; open, the lid stands behind and the inside is dark

CHEST = fig("""
oak_hi:   .######.
          ########
oak:      ########
          ########
gold_hi:  ########
          ###..###
oak:      ########
          ########
oak_lo:   ########
          ########
gold:     ########
          ##....##
""")

CHEST_OPEN = fig("""
oak_hi:   .######.
          #......#
oak_lo:   #......#
          ########
black:    .######.
          .######.
gold_hi:  ########
          ###..###
oak:      ########
          ########
gold:     ########
          ##....##
""")

# the golden gate over the east opening of room 14: 34 lines,
# from the last line of the wall above the opening to the
# first line of the wall below it; a rail every four lines
GATE = []
for _i in range(17):
    if _i % 2 == 0:
        GATE += [("########", "gold_hi"), ("#..##..#", "gold_hi")]
    else:
        GATE += [("#..##..#", "gold"), ("#..##..#", "gold")]
GATE[-1] = ("########", "gold_hi")

ALL = {
    "knight_stand": KNIGHT_STAND,
    "knight_walk1": KNIGHT_WALK1,
    "knight_walk2": KNIGHT_WALK2,
    "knight_thrust": KNIGHT_THRUST,
    "knight_parry": KNIGHT_PARRY,
    "serpent_a": SERPENT_A,
    "serpent_b": SERPENT_B,
    "king_a": KING_A,
    "king_b": KING_B,
    "crown": CROWN,
    "crown_broken": CROWN_BROKEN,
    "chest": CHEST,
    "chest_open": CHEST_OPEN,
    "gate": GATE,
    # a room without a guard, the gate open:
    # player 1 draws nothing
    "none": [],
}

# --- the digits of the HUD, 6 x 8 in a column of 8 -----------

DIGITS = [g.split() for g in """
.####. ##..## ##..## ##..## ##..## ##..## ##..## .####.
..##.. .###.. ..##.. ..##.. ..##.. ..##.. ..##.. .####.
.####. ##..## ....## ...##. ..##.. .##... ##.... ######
.####. ##..## ....## ..###. ....## ....## ##..## .####.
...##. ..###. .####. ##.##. ###### ...##. ...##. ...##.
###### ##.... #####. ....## ....## ....## ##..## .####.
.####. ##.... ##.... #####. ##..## ##..## ##..## .####.
###### ....## ...##. ..##.. .##... .##... .##... .##...
.####. ##..## ##..## .####. ##..## ##..## ##..## .####.
.####. ##..## ##..## ##..## .##### ....## ....## .####.
""".strip().splitlines()]

# --- the HUD and the sound modes: small letters 5 x 7 ----------

SMALL = {k: v.split() for k, v in {
    "L": "#.... #.... #.... #.... #.... #.... #####",
    "E": "##### #.... #.... ####. #.... #.... #####",
    "V": "#...# #...# #...# #...# .#.#. .#.#. ..#..",
    "1": "..#.. .##.. ..#.. ..#.. ..#.. ..#.. .###.",
    "2": ".###. #...# ....# ...#. ..#.. .#... #####",
    "3": ".###. #...# ....# ..##. ....# #...# .###.",
    "4": "...#. ..##. .#.#. #..#. ##### ...#. ...#.",
    " ": "..... ..... ..... ..... ..... ..... .....",
    # the sound modes on the title
    "M": "#...# ##.## #.#.# #.#.# #...# #...# #...#",
    "U": "#...# #...# #...# #...# #...# #...# .###.",
    "S": ".#### #.... #.... .###. ....# ....# ####.",
    "C": ".###. #...# #.... #.... #.... #...# .###.",
    "O": ".###. #...# #...# #...# #...# #...# .###.",
    "N": "#...# ##..# #.#.# #..## #...# #...# #...#",
    "D": "####. #...# #...# #...# #...# #...# ####.",
    "F": "##### #.... #.... ####. #.... #.... #....",
    "X": "#...# #...# .#.#. ..#.. .#.#. #...# #...#",
    "T": "##### ..#.. ..#.. ..#.. ..#.. ..#.. ..#..",
    "I": ".###. ..#.. ..#.. ..#.. ..#.. ..#.. .###.",
    # the key Sir Roderick carries, after LEVEL n
    "*": ".###. #...# .###. ..#.. ..##. ..#.. ..##.",
    # GAME OVER
    "G": ".###. #...# #.... #.### #...# #...# .###.",
    "A": ".###. #...# #...# ##### #...# #...# #...#",
    "R": "####. #...# #...# ####. #.#.. #..#. #...#",
    # VICTORY
    "Y": "#...# #...# .#.#. ..#.. ..#.. ..#.. ..#..",
}.items()}

# --- the title: letters 7 x 7, drawn on two lines each -------

LETTERS = {k: v.split() for k, v in {
    "S": ".#####. ##...## ##..... .#####. .....## ##...## .#####.",
    "C": ".#####. ##...## ##..... ##..... ##..... ##...## .#####.",
    "A": "..###.. .##.##. ##...## ##...## ####### ##...## ##...##",
    "L": "##..... ##..... ##..... ##..... ##..... ##..... #######",
    "E": "####### ##..... ##..... ######. ##..... ##..... #######",
    "R": "######. ##...## ##...## ######. ##.##.. ##..##. ##...##",
    "O": ".#####. ##...## ##...## ##...## ##...## ##...## .#####.",
    "W": "##...## ##...## ##...## ##.#.## ##.#.## ####### .##.##.",
    "N": "##...## ###..## ####.## ##.#### ##..### ##...## ##...##",
    # GAME OVER (the end screen)
    "G": ".#####. ##...## ##..... ##.#### ##...## ##...## .#####.",
    "M": "##...## ###.### ####### ##.#.## ##...## ##...## ##...##",
    "V": "##...## ##...## ##...## ##...## .##.##. ..###.. ...#...",
}.items()}

# --- the end screens: VICTORY in letters 6 x 7, so that
# its seven letters fill the 48 pixels (one pixel between them)

NARROW = {k: v.split() for k, v in {
    "V": "##..## ##..## ##..## ##..## ##..## .####. ..##..",
    "I": ".####. ..##.. ..##.. ..##.. ..##.. ..##.. .####.",
    "C": ".####. ##..## ##.... ##.... ##.... ##..## .####.",
    "T": "###### ..##.. ..##.. ..##.. ..##.. ..##.. ..##..",
    "O": ".####. ##..## ##..## ##..## ##..## ##..## .####.",
    "R": "#####. ##..## ##..## #####. ##.##. ##..## ##..##",
    "Y": "##..## ##..## ##..## .####. ..##.. ..##.. ..##..",
}.items()}

# the crown of the title: 24 x 10, drawn twice as wide and
# on two lines each (48 x 20)
EMBLEM = """
#..........##..........#
##.........##.........##
##........####........##
###......######......###
####....##.##.##....####
#####..####..####..#####
########################
#..##..##..##..##..##..#
########################
.######################.
""".split()


# the crown broken (the VICTORY screen): the two halves
# of the emblem apart, the right one a row lower, 24 x 11
def _broken():
    left = [r[:11] for r in EMBLEM] + ["." * 11]
    right = ["." * 11] + [r[13:] for r in EMBLEM]
    return [a + ".." + b for a, b in zip(left, right)]


EMBLEM_BROKEN = _broken()


def check():
    bad = []
    for d, g in enumerate(DIGITS):
        if len(g) != 8 or any(len(r) != 6 for r in g):
            bad.append(f"digit {d}")
    for k, g in LETTERS.items():
        if len(g) != 7 or any(len(r) != 7 for r in g):
            bad.append(f"letter {k}")
    for k, g in SMALL.items():
        if len(g) != 7 or any(len(r) != 5 for r in g):
            bad.append(f"small letter {k}")
    if len(EMBLEM) != 10 or any(len(r) != 24 for r in EMBLEM):
        bad.append("emblem")
    for k, g in NARROW.items():
        if len(g) != 7 or any(len(r) != 6 for r in g):
            bad.append(f"narrow letter {k}")
    if len(EMBLEM_BROKEN) != 11 or \
            any(len(r) != 24 for r in EMBLEM_BROKEN):
        bad.append("broken emblem")
    for name, f in ALL.items():
        if len(f) % 2:
            bad.append(f"{name}: odd number of lines")
        for i, (p, c) in enumerate(f):
            if len(p) != 8 or set(p) - set("#."):
                bad.append(f"{name} line {i}: {p!r}")
            if c not in COLOURS:
                bad.append(f"{name} line {i}: colour {c}")
            if i % 2 and c != f[i - 1][1]:
                bad.append(f"{name} line {i}: colour inside a pair")
    # the thrust: bit 1 of the NTSC colour of a pair says
    # whether the blade is drawn on it
    blade = [c == BLADE_COLOUR for _, c in ALL[BLADE_POSE]]
    if sum(blade) != 2:
        bad.append("thrust: one pair of blade lines")
    for i, (p, c) in enumerate(ALL[BLADE_POSE]):
        if bool(COLOURS[c] & 2) != blade[i]:
            bad.append(f"thrust line {i}: bit 1 of {c}")
    # the venom switches missile 1 (bit 1), the King's
    # flash must not; the King's mouth: the pair of KING_MOUTH
    if not COLOURS["venom"] & 2 or COLOURS["king_flash"] & 2:
        bad.append("bit 1 of the venom and of the King's flash")
    for n in ("king_a", "king_b"):
        if [c for _, c in ALL[n]][KING_MOUTH:KING_MOUTH + 2] != \
                [KING_MOUTH_COLOUR] * 2:
            bad.append(f"{n}: the mouth")
    return bad


# the pair of the King's mouth, from his top line
KING_MOUTH = 10
KING_MOUTH_COLOUR = "king_eye"


if __name__ == "__main__":
    print(check() or "art OK")
