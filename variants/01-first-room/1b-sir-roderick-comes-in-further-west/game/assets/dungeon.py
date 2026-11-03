"""dungeon.py - the Crypt of Scales: the 16 rooms, their
things, their serpents and the throne room.

The plan of the crypt, as the game draws it: a
4 x 4 grid, each row a level (an ever deeper floor), room r at
row r // 4, column r % 4.

A room is 20 x 10 blocks (8 pixels x 16 lines); only the left
half is written, the right half is its mirror (the playfield is
reflected). '#' is stone, '.' is floor, 'T' a torch in a niche
of the top wall (rooms.py, look.py).

The ways out of a room, the same in every room:
- east and west: block rows 4-5 at the edges of the screen;
  through them Sir Roderick goes to the room beside, at the
  same height;
- stairs: the south gap, blocks 8-11 of row 9, leads to the
  north gap of the room below (r + 4), at the same column; up
  the same way;
- plugs: the playfield is reflected, so a room has the opening
  on both sides; at the two ends of a level (columns 0 and 3
  of the grid) the outer one is closed by the ball, drawn in
  the colour of the wall over block column 0 or 19, and the
  collision map has stone there;
- the north gap of room 1 is the broken gate of Oakhaven, by
  which Sir Roderick came in: nothing is above it (gate: no
  stair is drawn in it);
- the stairs are drawn: three stone treads in the
  gap and below it (rooms.STAIR_TREADS), narrower towards
  the gap; they are only drawn, Sir Roderick walks on them.

The things of the plan:
- chest (x, top): the chest of the level's key, drawn by
  player 1 at that column and top line; when Sir Roderick
  touches it, it opens (it stays open) and he has the key;
- door: a level's door. In levels 1-3 the grate on the stair
  down (look.py draws its bars over the south gap, in the
  playfield); in level 4 the golden gate, drawn by player 1
  over the east opening of room 14 (GATE). Closed, the
  collision map has stone there (walls(r, closed=True)); he
  opens it by standing in front of it (DOOR_ZONE) with the
  key of the level, which is used up; it stays open;
- plate k: the spikes, two plates in the middle of the
  corridor (rooms.PLATE_COURSES), half cells k to k + 3 and
  their mirror, down and up in turn (rules.py); only drawn:
  he walks over them, and a raised plate under his feet
  hurts;
- the thing of a room, which player 1 shows when it shows
  only one: the chest where there is one, the gate in room
  14, otherwise the first guard (thing()).
The bits of what is open (one byte of the game): chest of
level n at bit n - 1, door of level n at bit n + 3.

guards: the serpents of the room (or the Serpent King), on
player 1: kind ("serpent", "king"), top line (odd), start
column, the columns it goes between (it starts towards the
left and turns at the ends: rules.py has the speed).

Two things on player 1:
- the room is cut in two bands of lines by the seam: from
  line 8c + 4 to 8c + 9 (the end of course c, the start of
  course c + 1) player 1 draws nothing and the kernel moves
  it to the serpent of the band below (seam()); band A ends
  above line 8c + 3, band B starts below line 8c + 10;
- band B, below the seam: the first guard ("S0"); band A,
  above: the thing of the room (chest, gate) and the second
  guard ("S1"). A room without a seam has its thing and its
  only guard in band A;
- two things in band A share lines (the serpent guards the
  chest, or crawls in the corridor of the gate): player 1
  shows them on alternate frames (the flicker), and only
  there;
- a serpent may be in the corridor (block rows 4-5), along
  the top wall (top line 15: its head over the last line of
  the wall, the floor of row 1 under the rest) or along the
  bottom wall (top line 127, the same against row 7);
- the HMOVE of the seam blanks pixels 0-7 of line 8c + 7 (the
  comb): the seam is never in the courses of the openings
  (8-11), where column 0 is floor.

The throne room (room 15, THRONE): its own
kernel (bank 2) draws it, with player 1 for the Serpent King or
the crown and missile 1 for the venom:
- the King, twice as wide, in the middle of the room in front
  of the throne (his column fixed), goes up and down between
  two top lines; his mouth is the pair of lines MOUTH below
  his top line, where the venom flies from;
- the venom flies along the lines of his mouth until it meets
  stone (the free pixels of each row of blocks: venom_span),
  Sir Roderick, or the edge of the screen;
- beaten, the King gives his place to the crown on the throne,
  drawn four times as wide over the throne's 32 pixels; struck,
  it shows its pieces (crown_broken): VICTORY.
"""

GRID = 4
START = dict(room=1, x=41, top=17, facing="right")

ROOMS = [
    # --- level 1, The Upper Crypt: open, pillars ----------
    dict(name="RUBBLE HALL", level=1, key=1, chest=(5, 19),
         spikes=False,
         serpents=2,             # one along the top wall
         guards=[dict(kind="serpent", top=65, x=104,
                      path=(32, 128)),
                 dict(kind="serpent", top=15, x=96,
                      path=(48, 112))],
         half="""
##########
#.........
#.##...#..
#.#.......
..........
..........
#......##.
#.##...##.
#.........
##########
"""),
    dict(name="THE BROKEN GATE", level=1, spikes=False,
         serpents=0, guards=[], gate=True,
         half="""
########..
#.........
#..##.....
#..##..##.
..........
..........
#..##..##.
#..##.....
#.........
##########
"""),
    dict(name="PILLAR WALK", level=1, spikes=True, plate=8,
         serpents=2,             # one along the top wall
         guards=[dict(kind="serpent", top=77, x=112,
                      path=(48, 128)),
                 dict(kind="serpent", top=15, x=88,
                      path=(32, 120))],
         half="""
##########
#.........
#..#...#..
#..#...#..
..........
..........
#..#...#..
#..#...#..
#.........
##########
"""),
    dict(name="THE IRON STAIR", level=1, door=1, spikes=False,
         serpents=2,             # one along the top wall
         guards=[dict(kind="serpent", top=73, x=96,
                      path=(40, 120)),
                 dict(kind="serpent", top=15, x=80,
                      path=(24, 128))],
         half="""
##########
#.........
#.####....
#.........
..........
..........
#.........
#..##.##..
#..##.#...
########..
"""),
    # --- level 2, The Ossuary: niches, torches ------------
    dict(name="BONE NICHE", level=2, key=2, chest=(5, 19),
         spikes=False,
         serpents=2,
         guards=[dict(kind="serpent", top=77, x=112,
                      path=(40, 128)),
                 dict(kind="serpent", top=15, x=80,
                      path=(53, 93))],
         half="""
##T###T###
#.#.#.#...
#.........
#...##....
..........
..........
#...##....
#.........
#.#.#.#...
##########
"""),
    dict(name="THE NARROW STEPS", level=2, door=2, spikes=True,
         plate=12,
         serpents=2,             # one along the top wall
         guards=[dict(kind="serpent", top=65, x=120,
                      path=(48, 132)),
                 dict(kind="serpent", top=15, x=104,
                      path=(40, 120))],
         half="""
###T###T##
#.........
#.###..###
#.###..###
..........
..........
#..##..#..
#..##..#..
#......#..
########..
"""),
    dict(name="SHED SKINS", level=2, spikes=True, plate=6,
         serpents=2,
         guards=[dict(kind="serpent", top=77, x=104,
                      path=(32, 128)),
                 dict(kind="serpent", top=15, x=96,
                      path=(16, 133))],
         half="""
#T###T###T
#.........
#.###..##.
#.#....##.
..........
..........
#.#....##.
#.###..##.
#.........
##########
"""),
    dict(name="THE LANDING", level=2, spikes=False, serpents=0,
         guards=[],
         half="""
########..
#.........
#.##......
#.##..##..
..........
..........
#.##..##..
#.##......
#.........
##########
"""),
    # --- level 3, The Sunken Halls: pools, water ----------
    dict(name="THE DROWNED STAIR", level=3, door=3, spikes=True,
         plate=14,
         serpents=2,
         guards=[dict(kind="serpent", top=127, x=100,
                      path=(16, 133)),
                 dict(kind="serpent", top=69, x=40,
                      path=(24, 128))],
         half="""
##########
#.........
#..##..##.
#..##..##.
..........
..........
#..##..#..
#..##..#..
#.........
########..
"""),
    dict(name="COLD LANDING", level=3, spikes=False, serpents=2,
         # one along the bottom wall (the stair comes in
         # at the top), below the seam
         guards=[dict(kind="serpent", top=127, x=64,
                      path=(16, 133)),
                 dict(kind="serpent", top=77, x=120,
                      path=(40, 132))],
         half="""
########..
#.........
#.###..#..
#.###..#..
..........
..........
#.###..##.
#.###..##.
#.........
##########
"""),
    dict(name="REED GALLERY", level=3, spikes=True, plate=8,
         serpents=2,
         guards=[dict(kind="serpent", top=127, x=64,
                      path=(16, 133)),
                 dict(kind="serpent", top=77, x=104,
                      path=(32, 128))],
         half="""
##########
#.........
#.#.#..#..
#.#.#..#..
..........
..........
#.#.#..#..
#.#.#..#..
#.........
##########
"""),
    dict(name="FANG CISTERN", level=3, key=3, chest=(141, 19),
         spikes=True, plate=13,
         serpents=2,
         guards=[dict(kind="serpent", top=77, x=112,
                      path=(40, 128)),
                 dict(kind="serpent", top=15, x=96,
                      path=(64, 133))],
         half="""
##########
#.........
#.##.##.##
#.##.##.##
..........
..........
#.##.##.##
#.##.##.##
#.........
##########
"""),
    # --- level 4, The Scaled Court: purple stone, torches -
    dict(name="LAST LANDING", level=4, spikes=False, serpents=2,
         # one along the bottom wall (the stair comes in
         # at the top), below the seam
         guards=[dict(kind="serpent", top=127, x=100,
                      path=(16, 133)),
                 dict(kind="serpent", top=77, x=112,
                      path=(40, 132))],
         half="""
########..
#.........
#.####.#..
#.#....#..
..........
..........
#.#.####..
#.#.......
#.........
##########
"""),
    dict(name="HALL OF COILS", level=4, key=4, chest=(73, 19),
         spikes=True, plate=5,
         serpents=2,
         guards=[dict(kind="serpent", top=77, x=104,
                      path=(32, 128)),
                 dict(kind="serpent", top=15, x=104,
                      path=(16, 133))],
         half="""
##T####T##
#.........
#..##.....
#..##.###.
..........
..........
#..##.###.
#..##.....
#.........
##########
"""),
    dict(name="THE GILDED GATE", level=4, spikes=True, plate=12,
         serpents=2, door=4,
         guards=[dict(kind="serpent", top=127, x=64,
                      path=(16, 133)),
                 dict(kind="serpent", top=77, x=104,
                      path=(40, 128))],
         half="""
###T##T###
#.........
#.#.......
#.#..####.
..........
..........
#.#..####.
#.#.......
#.........
##########
"""),
    dict(name="THRONE OF SCALES", level=4, spikes=False,
         serpents=0,
         guards=[dict(kind="king", top=25, x=68,
                      path=(68, 68))],
         half="""
###T####T#
#.......##
#..#......
#.........
..........
..........
#.........
#..#......
#.........
##########
"""),
]

import rooms                                          # noqa: E402
import rules                                          # noqa: E402

GAP = (8, 9)            # blocks of the north and south gaps (half)
SIDE_ROWS = (4, 5)      # block rows of the east and west openings


# player 1 in a room without a guard: an empty figure, moving
# between columns 0 and 2 like any guard (nothing shows)
NO_GUARD = dict(kind="none", top=1, x=1, path=(0, 2))


def guard(r):
    """The first guard of room r (NO_GUARD in a room without
    one)."""
    g = ROOMS[r]["guards"]
    return g[0] if g else NO_GUARD


# --- chests, doors, spikes --------------------

# the golden gate: player 1 over the east opening of room 14,
# block column 19 (first pixel 152), from line 63 to line 96
GATE = dict(room=14, x=149, top=63)
CHEST_H = 12
# where he stands to open a door, (first, last) column and
# (first, last) top line: in front of a grate, his box inside
# the gap's columns and as low as the closed grate lets him;
# in front of the gate, inside the opening's rows, as far
# east as the closed gate lets him
DOOR_ZONE = {"grate": ((61, 85), (119, 135)),
             "gate": ((141, 149), (65, 71))}


def chest_bit(level):
    return 1 << (level - 1)


def door_bit(level):
    return 0x10 << (level - 1)


def door(r):
    """'grate', 'gate' or None."""
    if not ROOMS[r].get("door"):
        return None
    return "gate" if r == GATE["room"] else "grate"


def thing(r, opened=0):
    """Player 1 in room r, showing one thing, with the bits
    `opened`: the chest (open or closed), the gate (nothing
    once open), or
    the first guard. kind, top, x, path; a thing that stays
    has a path of one column."""
    rm = ROOMS[r]
    if rm.get("chest"):
        x, top = rm["chest"]
        op = opened & chest_bit(rm["level"])
        return dict(kind="chest_open" if op else "chest",
                    top=top, x=x, path=(x, x))
    if door(r) == "gate":
        op = opened & door_bit(rm["level"])
        return dict(kind="none" if op else "gate",
                    top=GATE["top"], x=GATE["x"],
                    path=(GATE["x"], GATE["x"]))
    return guard(r)


def thing_bit(r):
    """The bit of `opened` that the thing of room r sets."""
    rm = ROOMS[r]
    if rm.get("chest"):
        return chest_bit(rm["level"])
    if door(r):
        return door_bit(rm["level"])
    return 0


def zone(r):
    """((first, last) column, (first, last) top line) where
    Sir Roderick touches the thing of room r, or None. The
    chest: his 8 x 24 box overlaps its 8 x CHEST_H box (the
    columns and lines he can have)."""
    rm = ROOMS[r]
    if rm.get("chest"):
        x, top = rm["chest"]
        return ((max(rules.X_MIN, x - 7), min(rules.X_MAX, x + 7)),
                (max(rules.TOP_MIN, top - rules.KNIGHT_H + 1),
                 min(rules.TOP_MAX, top + CHEST_H - 1)))
    if door(r):
        return DOOR_ZONE[door(r)]
    return None


def plate_zones(r):
    """The columns where the middle of his feet is over one of
    the two plates of room r, and the top lines where his
    feet (the last 8 lines of his box) touch the plates'
    lines: ([(first, last), (first, last)], (first, last))."""
    k = ROOMS[r].get("plate")
    if k is None:
        return None
    mid = rules.FIRST_PIXEL + rules.KNIGHT_W // 2   # kx + 7
    left = (4 * k, 4 * k + 15)
    right = (159 - left[1], 159 - left[0])
    c0, c1 = rooms.PLATE_COURSES
    lines = (8 * c0, 8 * c1 + 7)
    return ([(a - mid, b - mid) for a, b in (left, right)],
            (lines[0] - rules.KNIGHT_H + 1,
             lines[1] - (rules.KNIGHT_H - 8)))


# --- the throne room ------------------------
# the King's column (twice as wide: pixels 72-87, the middle of
# the screen), the top lines he goes between (odd: a figure
# starts on a line B), where he starts; his mouth: the pair of
# lines MOUTH below his top line; the crown: column (four times
# as wide: pixels 64-95, the throne's) and top line
THRONE = dict(room=15, x=68, top=(25, 103), start=25, mouth=10,
              crown=dict(x=60, top=33), head=14)
# the blade strikes the King only on his head (the crown,
# the hood, the mouth and the two lines below it: his first
# `head` lines), where the venom flies: low beside him, his
# blade on the coils, he cannot strike him safe from the venom
KING_W = 16
CROWN_W = 32
CROWN_H = 8
WIDE_OFFSET = 4         # a wide player's first pixel: column + 4


def throne(r):
    return r == THRONE["room"]


def king_pixels():
    x0 = THRONE["x"] + WIDE_OFFSET
    return x0, x0 + KING_W - 1


def spit_left():
    """The venom flies left (and the King faces left) when Sir
    Roderick's column is below this: his middle left of the
    King's."""
    a, b = king_pixels()
    return (a + b + 1) // 2 - (rules.FIRST_PIXEL + rules.KNIGHT_W // 2)


def crown_box():
    """(first pixel, last pixel, first line, last line)."""
    c = THRONE["crown"]
    x0 = c["x"] + WIDE_OFFSET
    return x0, x0 + CROWN_W - 1, c["top"], c["top"] + CROWN_H - 1


def venom_start(right):
    """The venom's first pixel when it leaves the King's mouth:
    beside him, on the side it flies to (8 pixels wide)."""
    a, b = king_pixels()
    return b + 1 if right else a - 8


def venom_span(top):
    """(first, last) pixel the venom may cover when the King's
    top line is `top`: on both lines of his mouth, around him,
    up to the first stone block (or the plug) on each side, or
    the edge of the screen."""
    w = walls(THRONE["room"])
    a, b = king_pixels()
    lo, hi = 0, 159
    for line in (top + THRONE["mouth"], top + THRONE["mouth"] + 1):
        row = w[line // 16]
        x = a - 1
        while x >= 0 and not row[x // 8]:
            x -= 1
        lo = max(lo, x + 1)
        x = b + 1
        while x <= 159 and not row[x // 8]:
            x += 1
        hi = min(hi, x - 1)
    return lo, hi


def throne_shows():
    """What player 1 shows in the throne room, as (kind, top
    line): the King at every top line, the crown and its
    pieces."""
    t0, t1 = THRONE["top"]
    c = THRONE["crown"]
    return [("king", t) for t in range(t0, t1 + 1, 2)] + \
        [("crown", c["top"]), ("crown_broken", c["top"])]


# --- two things on player 1 -------------------

SERPENT_H = 16
# the courses where a seam may be: not those of the openings
# (block rows 4-5), where the comb of the HMOVE would show on
# the floor of column 0; and not the last two (the kernel ends
# there)
SEAM_COURSES = [c for c in range(18) if not 8 <= c <= 11]
# around the seam of course c: band A is read down to line
# 8c + 3 and ends above it; band B is read from line 8c + 10
# and starts below it
SEAM_FIRST, SEAM_LAST = 3, 10


def height(kind):
    return {"serpent": SERPENT_H, "king": 40, "chest": CHEST_H,
            "chest_open": CHEST_H, "gate": 34, "none": 0}[kind]


def has_seam(r):
    """A seam when a thing or a second guard is above the
    first guard."""
    rm = ROOMS[r]
    g = rm["guards"]
    return bool(g) and g[0]["kind"] == "serpent" and (
        len(g) == 2 or bool(rm.get("chest")) or door(r) == "gate")


def band_a(r):
    """The things of band A (above the seam, or the whole room
    without one), as (kind, top, x, path) dicts: the thing of
    the room first (closed), then a guard. Two of them take
    turns (the flicker)."""
    out = []
    t = thing_item(r)
    if t:
        out.append(t)
    g = ROOMS[r]["guards"]
    if has_seam(r):
        if len(g) == 2:
            out.append(g[1])
    elif g:
        out.append(g[0])
    return out


def band_b(r):
    """The guard below the seam, or None."""
    return ROOMS[r]["guards"][0] if has_seam(r) else None


def thing_item(r):
    """The chest or the gate of room r, closed, or None."""
    rm = ROOMS[r]
    if rm.get("chest"):
        x, top = rm["chest"]
        return dict(kind="chest", top=top, x=x, path=(x, x))
    if door(r) == "gate":
        return dict(kind="gate", top=GATE["top"], x=GATE["x"],
                    path=(GATE["x"], GATE["x"]))
    return None


def seam(r):
    """The course c of the seam of room r (the first one that
    leaves band A above line 8c + 3 and band B below line
    8c + 10), or None."""
    if not has_seam(r):
        return None
    low = max(o["top"] + height(o["kind"]) - 1 for o in band_a(r))
    top = band_b(r)["top"]
    for c in SEAM_COURSES:
        if low < 8 * c + SEAM_FIRST and top > 8 * c + SEAM_LAST:
            return c
    raise SystemExit(f"room {r}: no course for the seam")


# where player 1 shows nothing in a room without a thing (the
# empty figure; any line would do)
NONE_TOP = 1
# the column of a guard a room does not have (it never shows
# or moves; the arithmetic of the seam wants a column from 3)
ABSENT_X = 16


def open_kind(kind):
    return {"chest": "chest_open", "gate": "none"}[kind]


def p1_shows(r):
    """Everything player 1 can show in room r, as (band, kind,
    top line): the thing closed and open; the guard of band A
    (or nothing, where there is no thing, when it is dead or
    there is none); the guard of band B, alive or dead. The
    throne room has its own kernel: throne_shows."""
    if throne(r):
        return []
    out = []
    t = thing_item(r)
    if t:
        out += [("A", t["kind"], t["top"]),
                ("A", open_kind(t["kind"]), t["top"])]
    else:
        out.append(("A", "none", NONE_TOP))
    return out


def windows(r):
    """The lines player 1 is read in for band A and band B:
    ((first, last), (first, last) or None)."""


def comb_line(r):
    """The line of the room where the HMOVE of the seam blanks
    pixels 0-7, or None."""
    c = seam(r)
    return None if c is None else 8 * c + 7


def serpent_on_floor(r, g):
    """Along its whole path the serpent's lines below its top
    one are floor (the top line, its head, may be the last
    line of the wall above)."""
    w = walls(r)
    a, b = g["path"]
    for x in range(a, b + 1):
        for line in range(g["top"] + 1, g["top"] + height(g["kind"])):
            for px in range(x + 3, x + 11):
                if w[line // 16][px // 8]:
                    return False
    return True


def plug(r):
    """The side closed by the ball: the outer opening of the
    rooms at the two ends of a level."""
    return {0: "west", GRID - 1: "east"}.get(r % GRID)


def gap(r, row):
    """True if the top (row 0) or bottom (row 9) wall of room
    r is open at the gap."""
    rows = rooms.half_rows(ROOMS[r])
    return all(rows[row][c] == "." for c in GAP)


def exits(r):
    """The room beyond each way out of room r (None: none)."""
    col = r % GRID
    south = r + GRID if gap(r, 9) else None
    north = r - GRID if r >= GRID and gap(r - GRID, 9) else None
    return dict(east=r + 1 if col < GRID - 1 else None,
                west=r - 1 if col > 0 else None,
                south=south, north=north)


def walls(r, closed=False):
    """The collision map of room r; closed: with its door
    closed (stone in the grate's gap, or over the opening the
    gate closes)."""
    w = rooms.walls(ROOMS[r], plug(r))
    if closed and door(r) == "grate":
        for c in range(8, 12):
            w[9][c] = True
    if closed and door(r) == "gate":
        for row in SIDE_ROWS:
            w[row][19] = True
    return w


def check():
    """The rules of the maps; the rest (the knight can go from
    every way in to every way out, the guards stay on the
    floor, the plan) is checked by the test bench of the
    book."""
    bad = []
    if len(ROOMS) != GRID * GRID:
        bad.append("16 rooms")
    for r, rm in enumerate(ROOMS):
        n = f"room {r}"
        rows = rooms.half_rows(rm)
        if len(rows) != 10 or any(len(x) != 10 for x in rows):
            bad.append(f"{n}: 10 rows of 10 blocks")
            continue
        if any(set(x) - set("#.T") for x in rows):
            bad.append(f"{n}: only # . T")
        if any("T" in x for x in rows[1:]):
            bad.append(f"{n}: torches only in the top wall")
        if rm["level"] != r // GRID + 1:
            bad.append(f"{n}: level")
        for i, x in enumerate(rows):
            want = "." if i in SIDE_ROWS else "#"
            if x[0] != want:
                bad.append(f"{n}: the edge, row {i}")
        for i in (0, 9):
            wall = [c for k, c in enumerate(rows[i])
                    if k not in GAP]
            if "." in wall or (rows[i][GAP[0]] == ".") != \
                    (rows[i][GAP[1]] == "."):
                bad.append(f"{n}: the wall of row {i}")
        if gap(r, 9) and (r + GRID >= len(ROOMS) or
                          not gap(r + GRID, 0)):
            bad.append(f"{n}: a stair down to no north gap")
        if gap(r, 0) and r >= GRID and not gap(r - GRID, 9):
            bad.append(f"{n}: a north gap under no stair")
        if gap(r, 0) and r < GRID and r != START["room"]:
            bad.append(f"{n}: only the broken gate opens on top")
        if bool(rm.get("gate")) != (r == START["room"]):
            bad.append(f"{n}: the broken gate is the start room")
        for g in rm["guards"]:
            if g["kind"] == "king":
                continue            # THRONE, below
            if g["top"] % 2 == 0 or not \
                    g["path"][0] < g["x"] <= g["path"][1]:
                bad.append(f"{n}: guard")
        if [g["kind"] for g in rm["guards"]].count("king") != \
                (r == len(ROOMS) - 1):
            bad.append(f"{n}: the Serpent King is in the last room")
        # chests, doors, plates
        if bool(rm.get("chest")) != bool(rm.get("key")):
            bad.append(f"{n}: a chest where a key is")
        if rm.get("key") not in (None, rm["level"]) or \
                rm.get("door") not in (None, rm["level"]):
            bad.append(f"{n}: the key and door of its level")
        if rm["spikes"] != ("plate" in rm):
            bad.append(f"{n}: plates where the spikes are")
        if door(r) == "grate" and not gap(r, 9):
            bad.append(f"{n}: a grate on no stair")
        if rm.get("chest"):
            x, top = rm["chest"]
            w = walls(r)
            if top % 2 == 0 or any(
                    w[line // 16][px // 8]
                    for line in range(top, top + CHEST_H)
                    for px in range(x + 3, x + 11)):
                bad.append(f"{n}: the chest on the floor")
        k = rm.get("plate")
        if k is not None:
            if not (4 <= k and k + 3 <= 11 or 12 <= k and
                    k + 3 <= 17):
                bad.append(f"{n}: a plate inside PF1 or PF2, "
                           "apart from its mirror")
            c0, c1 = rooms.PLATE_COURSES
            m = rooms.full_map(rm)
            if any(m[c // 2][cell // 2] != "."
                   for c in range(c0 - 1, c1 + 2)
                   for cell in range(k - 1, k + 5)):
                bad.append(f"{n}: a plate on open floor")
        # the serpents of the plan, two things on player 1
        snakes = [g for g in rm["guards"] if g["kind"] == "serpent"]
        if len(snakes) != rm["serpents"] or len(rm["guards"]) > 2:
            bad.append(f"{n}: the serpents of the plan, two at most")
        for g in snakes:
            if not serpent_on_floor(r, g):
                bad.append(f"{n}: a serpent off the floor")
            if g["path"][0] < 16 or g["path"][1] > rules.X_MAX - 16:
                bad.append(f"{n}: a serpent too near an edge "
                           "where he comes in")
        try:
            c = seam(r)
        except SystemExit as e:
            bad.append(str(e))
            continue
        a = band_a(r)
        if len(a) > 2:
            bad.append(f"{n}: three things in band A")
        if len(a) == 2:
            (t0, h0), (t1, h1) = ((o["top"], height(o["kind"]))
                                  for o in a)
            if t0 + h0 <= t1 or t1 + h1 <= t0:
                bad.append(f"{n}: two things take turns but share "
                           "no lines")
        if c is not None and (band_b(r)["kind"] != "serpent" or
                              c not in SEAM_COURSES or
                              band_b(r)["path"][0] < 3):
            bad.append(f"{n}: the seam (and the guard below it "
                       "from column 3)")
    for lv in (1, 2, 3, 4):
        if sum(1 for rm in ROOMS if rm.get("key") == lv) != 1 or \
                sum(1 for rm in ROOMS if rm.get("door") == lv) != 1:
            bad.append(f"level {lv}: one key and one door")
    if door(GATE["room"]) != "gate" or GATE["top"] % 2 == 0:
        bad.append("the golden gate")
    # the throne room
    t0, t1 = THRONE["top"]
    rm = ROOMS[THRONE["room"]]
    if not throne(len(ROOMS) - 1) or rm["guards"][0]["kind"] != "king" \
            or rm["guards"][0]["x"] != THRONE["x"]:
        bad.append("the King in the throne room, at THRONE's column")
    if t0 % 2 == 0 or t1 % 2 == 0 or not t0 <= THRONE["start"] <= t1 \
            or THRONE["start"] % 2 == 0 or THRONE["mouth"] % 2:
        bad.append("the King's top lines: odd; the mouth a pair")
    w = walls(THRONE["room"])
    a, b = king_pixels()
    if (a + b) // 2 != 79 or a % 8 or (b + 1) % 8:
        bad.append("the King in the middle of the room")
    # below the throne's row the King's column is floor
    for line in range(16 * 2, t1 + 40):
        for px in range(a, b + 1):
            if w[line // 16][px // 8]:
                bad.append(f"the King's column: stone at line {line}")
                break
    if t1 + 40 > 144 or t0 + 40 <= 32:
        bad.append("the King between the throne and the bottom wall")
    for top in range(t0, t1 + 1, 2):
        lo, hi = venom_span(top)
        if not lo <= venom_start(False) or \
                not venom_start(True) + 7 <= hi:
            bad.append(f"the venom leaves the King at {top}")
    x0, x1, c0, c1 = crown_box()
    if (x0, x1) != (64, 95) or c0 % 2 == 0:
        bad.append("the crown over the throne (pixels 64-95)")
    return bad
