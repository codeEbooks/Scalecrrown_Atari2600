"""rooms.py - how a room is drawn: the levels and the map.

A room is 20 x 10 blocks (8 pixels x 16 lines); dungeon.py
writes only the left half, the right half is its mirror (the
playfield is reflected). '#' is stone, '.' is floor, 'T' a
torch in a niche of the top wall (stone with a hole that the
flame fills: the background colour of those lines is the
colour of the flame).

The look of a room is not in the map but in three rules, the
same for every room:

- stone courses: every block row is two courses of 8 lines;
  in a course the walls take four shades, one per pair of
  lines: light, middle, middle, dark (the mortar);
- joints: where a wall is at least three blocks long, a joint
  4 pixels wide every 16 pixels, shifted by 8 pixels from one
  course to the next (the floor colour shows through; not in
  the top wall of a room with torches, where the flame colour
  would show);
- light: the floor and the walls get brighter near the light
  of the level (a line of the room) and darker away from it;
- stairs: where a gap in the bottom wall leads down,
  three treads of stone on alternate courses, the one
  nearest the room widest and the one in the gap narrowest
  (STAIR_TREADS), centred on the gap: a stair seen from
  above, going down into the gap; a gap in the top wall that
  leads up has the same treads upside down. They are only
  drawn: the map is floor there, Sir Roderick walks on them.

LEVELS gives what a level shares (one set of
colours a level, so its rooms share the colour tables of the
cartridge): the hue and the brightness range of walls and
floor (NTSC values; PAL is the nearest colour, as for the
figures), the line of the light, the water that shimmers, the
colours of the serpents.

The same map says where Sir Roderick can walk: walls() is the
collision map, '#' and 'T' stop him, and so
does the plug of a room at the end of a level (dungeon.py).
"""

LEVELS = {
    # hue of the walls, their brightness from dark to light,
    # hue of the floor, its brightness from dark to light, the
    # line of the light, water, the colours of the serpents
    1: dict(name="The Upper Crypt", wall=0x00, wall_lum=(4, 12),
            floor=0x80, floor_lum=(0, 6), light=80, shimmer=False,
            snake=dict(snake_hi=0x1C, snake_lo=0xD6)),
    2: dict(name="The Ossuary", wall=0x20, wall_lum=(4, 12),
            floor=0xF0, floor_lum=(0, 4), light=40, shimmer=False,
            snake=dict(snake_hi=0x3A, snake_lo=0x34)),
    3: dict(name="The Sunken Halls", wall=0x90, wall_lum=(2, 10),
            floor=0xA0, floor_lum=(0, 6), light=80, shimmer=True,
            snake=dict(snake_hi=0xCC, snake_lo=0xC4)),
    4: dict(name="The Scaled Court", wall=0x60, wall_lum=(2, 10),
            floor=0x40, floor_lum=(0, 4), light=40, shimmer=False,
            snake=dict(snake_hi=0x1E, snake_lo=0x44)),
}

# the treads of a stair, from the room towards the gap: the
# half width of each in cells of 4 pixels (a tread every
# other course: three on six courses, 48 lines)
STAIR_TREADS = (3, 2, 1)

# the versions of a course: the cells that
# change with the state of a thing (look.stone draws them)
# - the grate, closed: bars over the south gap, in the two
#   courses of the bottom wall (half cells 16-19; open, the
#   gap with the treads of its stair);
# - the spikes: two plates of 4 cells in the middle of the
#   corridor, courses 9 and 10 (lines 72-87, a course of
#   floor above and below them); down, two studs in the
#   lower course; up, teeth in the upper course over a bar.
GRATE_COURSES = (18, 19)
GRATE = ".#.#"
PLATE_COURSES = (9, 10)
PLATE_DOWN = ("....", "#.#.")
PLATE_UP = ("#.#.", "####")

# the flame of a torch, top to bottom, one colour a pair of
# lines (8 pairs: the 16 lines of the top wall)
FLAME = (0x40, 0x42, 0x44, 0x36, 0x38, 0x2A, 0x1C, 0x1E)


def half_rows(room):
    return [r for r in room["half"].split() if r]


def full_map(room):
    """The 20 x 10 map of characters."""
    return [list(r + r[::-1]) for r in half_rows(room)]


def torches(room):
    return any("T" in r for r in half_rows(room))


def stairs(room):
    """(down, up): a stair in the bottom wall, in the top wall
    (a gap in the wall; the broken gate is not a stair)."""
    rows = half_rows(room)
    down = rows[9][8] == rows[9][9] == "."
    up = rows[0][8] == rows[0][9] == "." and not room.get("gate")
    return down, up


def grate(room):
    """A door on the stair down: the grate of levels 1-3."""
    return bool(room.get("door")) and stairs(room)[0]


def walls(room, plug=None):
    """10 rows x 20 blocks, True where Sir Roderick cannot go:
    stone and torches, and block column 0 (plug "west") or 19
    (plug "east") where the ball closes the opening. The
    collision map of the cartridge, from the same text as the
    playfield."""
    w = [[ch != "." for ch in row] for row in full_map(room)]
    if plug:
        c = 0 if plug == "west" else 19
        for row in w:
            row[c] = True
    return w
