"""look.py - what the game must show, in pixels and colours.

The design, written once: which pixel of a room is stone, the
colour of walls and floor on every pair of lines, the colours
of the figures, NTSC and PAL. The generator turns it into the
bytes of the cartridge (build_assets.py); the test bench of
the book draws the expected picture from it.
Neither of them knows how the other works: the order of the
bits of the playfield, the tables in the Superchip RAM and the
interleaved colour tables are only in the generator.
"""
import json
import os

import art
import rooms

HERE = os.path.dirname(os.path.abspath(__file__))
PALETTE = json.load(open(os.path.join(HERE, "palette_stella.json")))

# the HUD: 32 lines above the room (lines from its top)
HUD_LINES = 32
HUD_DIGITS = 2                  # first line of the digits
HUD_BAR = 12                    # first line of the energy bar
HUD_SCORE_COLOUR = 0x1E
HUD_BAR_COLOURS = (0x42, 0x46, 0x44, 0x40)      # from the top
HUD_TEXT = 18                   # first line of the level name
HUD_TEXT_COLOUR = 0x0A


def hud_text_rows(level, key=False):
    """'LEVEL n' in the small letters and, after it, the key
    when Sir Roderick has one: eight letters, 47 pixels,
    from the top: 7 rows and an empty one."""
    return text_rows(f"LEVEL {level}" + ("*" if key else " "))


def game_over_rows():
    """GAME OVER in the place of LEVEL n: two words of
    four letters, 23 pixels each, two pixels apart (48)."""
    rows = []
    for y in range(7):
        words = ["".join(art.SMALL[ch][y] + ("." if i < 3 else "")
                         for i, ch in enumerate(w))
                 for w in ("GAME", "OVER")]
        rows.append(words[0] + ".." + words[1])
    return rows + ["." * 48]


def victory_rows():
    """VICTORY in the place of LEVEL n, centred."""
    return text_rows("VICTORY")


def text_rows(text):
    """A text in the small letters, 48 pixels, centred, from
    the top: 7 rows and an empty one."""
    width = 6 * len(text) - 1
    x0 = (48 - width) // 2
    rows = []
    for y in range(7):
        line = ["."] * 48
        for i, ch in enumerate(text):
            for k, c in enumerate(art.SMALL[ch][y]):
                line[x0 + 6 * i + k] = c
        rows.append("".join(line))
    return rows + ["." * 48]

ROOM_LINES = 160
PAIRS = 80
COURSES = 20                    # 8 lines each
SHADES = (4, 2, 2, 0)           # light, middle, middle, mortar
SHIMMER_FRAMES = 4


def pal_of(ntsc, bit1=None):
    """The PAL colour nearest to an NTSC one, as Stella draws
    them; black stays $00, the value the kernels write. With
    bit1 (0 or 1) only the colours with that bit 1 count."""
    if ntsc == 0:
        return 0
    r, g, b = PALETTE["ntsc"][f"{ntsc:02X}"]
    cands = [kv for kv in PALETTE["pal"].items()
             if bit1 is None or (int(kv[0], 16) >> 1) & 1 == bit1]
    best = min(cands, key=lambda kv: (
        (kv[1][0] - r) ** 2 + (kv[1][1] - g) ** 2 +
        (kv[1][2] - b) ** 2, kv[0]))
    return int(best[0], 16)


def tv_colour(ntsc, tv):
    return ntsc if tv == "ntsc" else pal_of(ntsc)


def figure_colour(name, tv, level=None, blade=None):
    """The value of a colour of a figure. blade (True/False)
    is for the thrust: bit 1 of the value is also the switch
    of the blade (art.py), so on PAL the nearest colour with
    the right bit 1 is taken."""
    v = art.COLOURS[name]
    if level is not None:
        v = rooms.LEVELS[level]["snake"].get(name, v)
    if tv == "pal":
        if blade is not None:
            return pal_of(v, int(blade))
        return art.PAL_FIX.get(name, pal_of(v))
    return v


def pose_colours(name, tv, level=None):
    """The colour of every line of a figure, from the top."""
    lines = art.ALL[name]
    out = []
    for j in range(len(lines)):
        cname = lines[j - j % 2][1]
        blade = (cname == art.BLADE_COLOUR) \
            if name == art.BLADE_POSE else None
        out.append(figure_colour(cname, tv, level, blade))
    return out


def king_colours(tv, spit=False, flash=False):
    """The colour of every line of the Serpent King, from the
    top. Spitting (the venom flies), bit 1 is the switch
    of missile 1: set only on the pair of his mouth, which takes
    the venom's colour; the other pairs lose it (one step
    darker, on both televisions).
    Flashing (a blow), every pair is the flash colour, which
    has no bit 1."""
    lines = art.ALL["king_a"]
    out = []
    for j in range(len(lines)):
        cname = lines[j - j % 2][1]
        mouth = art.KING_MOUTH <= j < art.KING_MOUTH + 2
        if spit and mouth:
            v = art.COLOURS["venom"]
            out.append(v if tv == "ntsc" else pal_of(v, 1))
            continue
        if flash:
            v = art.COLOURS["king_flash"]
            out.append(v if tv == "ntsc" else pal_of(v, 0))
            continue
        v = figure_colour(cname, tv)
        out.append(v & 0xFD if spit and v & 2 else v)
    return out


# --- the stone of a room -------------------------------------

def stone(room, frame=0, stairs=True, closed=False, raised=False):
    """40 x 20 cells (4 pixels x 8 lines): True is stone.

    A torch ('T') is a block of stone whose lower course is
    open; in odd frames of the flicker the flame also opens
    the right cell of the upper course. The treads of the
    stairs (rooms.STAIR_TREADS) are drawn over the gaps, and
    have no joints. closed: the grate of the
    room (if it has one) over its south gap; the plates of
    the spikes, down or raised."""
    m = rooms.full_map(room)
    out = []
    for c in range(COURSES):
        row = m[c // 2]
        half = []
        for k in range(20):
            ch = row[k // 2]
            if ch == "T":
                open_ = c == 1 or (c == 0 and frame % 2 and
                                   k % 2 == 1)
                half.append(not open_)
            else:
                half.append(ch != ".")
        new = list(half)
        for k in range(20):
            if (k + 2 * (c % 2)) % 4 != 3:
                continue
            if c < 2 and rooms.torches(room):
                continue        # the flames would show through
            # inside a wall run of at least 3 blocks (6 cells)
            # with stone on both sides
            lo = k
            while lo > 0 and half[lo - 1]:
                lo -= 1
            hi = k
            while hi < 19 and half[hi + 1]:
                hi += 1
            if half[k] and hi - lo + 1 >= 6 and lo < k < hi:
                new[k] = False
        out.append(new + new[::-1])
    if stairs:
        down, up = rooms.stairs(room)
        n = 2 * len(rooms.STAIR_TREADS)
        for i, w in enumerate(rooms.STAIR_TREADS):
            # the courses of the treads, from the room's side
            for c in ([COURSES - n + 2 * i] if down else []) + \
                    ([n - 1 - 2 * i] if up else []):
                half = out[c][:20]
                for k in range(16, 20):
                    half[k] = k >= 20 - w
                out[c] = half + half[::-1]
    if closed and rooms.grate(room):
        for c in rooms.GRATE_COURSES:
            half = out[c][:20]
            for i, ch in enumerate(rooms.GRATE):
                half[16 + i] = ch == "#"
            out[c] = half + half[::-1]
    if room.get("plate") is not None:
        k = room["plate"]
        pat = rooms.PLATE_UP if raised else rooms.PLATE_DOWN
        for c, p in zip(rooms.PLATE_COURSES, pat):
            half = out[c][:20]
            for i, ch in enumerate(p):
                half[k + i] = ch == "#"
            out[c] = half + half[::-1]
    return out


def light(level, pair):
    """0..1: how much light reaches pair of lines `pair` in a
    room of the level."""
    line = 2 * pair + 1
    d = abs(line - rooms.LEVELS[level]["light"])
    return max(0.0, 1.0 - d / 120.0)


def _lum(lo, hi, f):
    return int(round((lo + (hi - lo) * f) / 2.0)) * 2


def pair_colours(level, torch=False, shimmer=0):
    """[(COLUPF, COLUBK)] for the 80 pairs of a room of the
    level, NTSC values: with torch, the flame is the floor of
    the top wall (it shows through the niches); shimmer (0 or
    1) is the frame of the water. The rooms of a level share
    these colours."""
    lv = rooms.LEVELS[level]
    frame = 2 * shimmer
    out = []
    for p in range(PAIRS):
        f = light(level, p)
        wlo, whi = lv["wall_lum"]
        base = _lum(wlo, whi - 4, f)
        wall = lv["wall"] | min(14, base + SHADES[p % 4])
        flo, fhi = lv["floor_lum"]
        fl = _lum(flo, fhi, f)
        if lv["shimmer"] and (p + frame) % 4 == 0:
            fl = min(14, fl + 2)
        floor = lv["floor"] | fl
        if torch and p < 8:
            floor = rooms.FLAME[p]
        out.append((wall, floor))
    return out


def room_picture(room, tv, frame=0, shimmer=0, plug=None,
                 closed=False, raised=False):
    """160 x 160 values of the room without figures: frame is
    the frame of the torches' flicker, shimmer the one of the
    water; plug ("west", "east") the side where the ball, in
    the colour of the wall, covers block column 0 or 19 from
    top to bottom (dungeon.py); closed: the grate is closed;
    raised: the plates of the spikes are up."""
    st = stone(room, frame, closed=closed, raised=raised)
    cols = pair_colours(room["level"], rooms.torches(room),
                        shimmer)
    pic = []
    for line in range(ROOM_LINES):
        wall, floor = cols[line // 2]
        wall, floor = tv_colour(wall, tv), tv_colour(floor, tv)
        row = st[line // 8]
        pic.append([wall if row[x // 4] else floor
                    for x in range(160)])
        if plug:
            x0 = 0 if plug == "west" else 152
            pic[-1][x0:x0 + 8] = [wall] * 8
    return pic


def figure_lines(name):
    """[(8-bit pattern, colour name)] from the top."""
    return [(int(p.replace("#", "1").replace(".", "0"), 2), c)
            for p, c in art.ALL[name]]


# --- the title -----------------------------------------------
# 192 lines (PAL: 18 black lines more above and below). The
# background is a glow, the two stone pillars carry torches,
# and three blocks 48 pixels wide are drawn with the two
# players: the crown and the two halves of the name.

TITLE_LINES = 192
TITLE_BLOCKS = (("emblem", 46), ("SCALE", 74), ("CROWN", 92))
# the sound mode: one of three 48-pixel lines of small
# letters, below the name; SELECT changes it
MODE_TOP = 114
MODES = ("MUSIC", "SOUND FX", "SILENT")
MODE_COLOUR = 0x0C
# the duel below the name: lines 128-131 place the players
# (the decor stays as on line 127), then 41 lines of figures
TITLE_SETUP = 128
TITLE_SCENE = 132
SCENE_H = 41
SCENE_KNIGHT = dict(name="knight_stand", x=36, mirror=False)
SCENE_KING = dict(name="king_a", x=98, mirror=True)
LOGO_COLOURS = (0x1E, 0x1E, 0x1C, 0x1C, 0x1A, 0x2A, 0x28, 0x28,
                0x38, 0x38, 0x36, 0x46, 0x44, 0x44)


def title_block_lines(name):
    """Rows of 48 characters, from the top; the last is empty
    so that the players are empty after the block."""
    if name in MODES:
        return text_rows(name)
    if name == "emblem":
        rows = []
        for r in art.EMBLEM:
            wide = "".join(ch * 2 for ch in r)
            rows += [wide, wide]
    else:
        rows = []
        for y in range(7):
            line = ["."] * 48
            for i, ch in enumerate(name):
                for k, c in enumerate(art.LETTERS[ch][y]):
                    line[2 + 9 * i + k] = c
            rows += ["".join(line)] * 2
    return rows + ["." * 48]


def title_block_colours(name):
    """One colour per line of a block, from the top (NTSC)."""
    n = len(title_block_lines(name))
    if name in MODES:
        return [MODE_COLOUR] * (n - 1) + [0]
    if name == "emblem":
        out = []
        for i in range(n):
            r = i // 2
            out.append(0x44 if r == 7 else
                       (0x1E, 0x1E, 0x1C, 0x1C, 0x1A, 0x1A, 0x2A,
                        0x44, 0x2A, 0x28, 0x28)[min(r, 10)])
        return out
    return list(LOGO_COLOURS) + [0]


def title_decor():
    """Per line, from the top: (COLUBK, COLUPF, stone cells of
    the left half (20 cells of 4 pixels))."""
    out = []
    for line in range(TITLE_LINES):
        # lines 0-3 are black (the players are placed there);
        # the glow: purple above, black in the middle, a red
        # ember below
        if line < 4:
            out.append((0x00, 0x00, [False] * 20))
            continue
        if line < 46:
            bg = 0x60 | min(6, (46 - line) // 8 * 2)
        elif line < TITLE_SCENE:
            bg = 0x00       # black: hides the HMOVE comb of
        else:               # line 130 (see title_kernel.asm)
            bg = 0x40 | min(4, (line - TITLE_SCENE) // 14 * 2)
        cells = [False] * 20
        pfc = 0x08
        if 16 <= line < 30:                 # flame
            k = line - 16
            width = (1, 1, 2, 2, 3, 3, 3, 4, 4, 4, 3, 3, 2, 2)[k]
            for c in range(3 - width // 2, 3 - width // 2 + width):
                cells[c] = True
            pfc = (0x40, 0x42, 0x44, 0x46, 0x36, 0x38, 0x3A, 0x2A,
                   0x2C, 0x1C, 0x1E, 0x1E, 0x0E, 0x0E)[k]
        elif 30 <= line < 36:               # bowl of the torch
            for c in range(1, 6):
                cells[c] = True
            pfc = 0x26 if line < 33 else 0x24
        elif 36 <= line < 186:              # the pillar
            for c in range(2, 5):
                cells[c] = True
            pfc = 0x06 if (line // 8) % 2 else 0x08
        out.append((bg, pfc, cells))
    return out


def title_picture(tv, x0, mode=0):
    """The expected title, 160 x 192 values, with the blocks at
    column x0 and the sound mode `mode`."""
    dec = title_decor()
    pic = []
    for line in range(TITLE_LINES):
        bg, pfc, cells = dec[line]
        row = cells + cells[::-1]
        pic.append([tv_colour(pfc, tv) if row[x // 4] else
                    tv_colour(bg, tv) for x in range(160)])
    # the duel: the decor stays as on line TITLE_SETUP - 1
    for line in range(TITLE_SETUP, TITLE_SCENE + SCENE_H):
        pic[line] = list(pic[TITLE_SETUP - 1])
    for fig, wide, off in ((SCENE_KING, True, 4),
                           (SCENE_KNIGHT, False, 3)):
        lines = figure_lines(fig["name"])
        y0 = TITLE_SCENE + SCENE_H - 1 - len(lines)
        for j, (bits, cname) in enumerate(lines):
            col = figure_colour(lines[j - j % 2][1], tv)
            for i in range(8):
                b = 7 - i if fig["mirror"] else i
                if bits & (0x80 >> b):
                    for w in range(2 if wide else 1):
                        x = fig["x"] + off + (2 * i + w if wide
                                              else i)
                        pic[y0 + j][x] = col
    # during a block the decor stays as on the line before it
    for name, top in TITLE_BLOCKS + ((MODES[mode], MODE_TOP),):
        rows = title_block_lines(name)
        cols = title_block_colours(name)
        for i, r in enumerate(rows):
            line = top + i
            pic[line] = list(pic[top - 1])
            for x, ch in enumerate(r):
                if ch == "#":
                    pic[line][x0 + x] = tv_colour(cols[i], tv)
    return pic


def scene_tables(tv):
    """Bottom first, SCENE_H entries: knight graphics and
    colours, king graphics and colours (the bottom line is
    empty so that the players are empty after the duel)."""
    out = []
    for fig in (SCENE_KNIGHT, SCENE_KING):
        lines = figure_lines(fig["name"])
        g = [0] * SCENE_H
        c = [0] * SCENE_H
        for j, (bits, cname) in enumerate(lines):
            k = len(lines) - j       # index from the bottom
            g[k] = bits
            c[k] = figure_colour(lines[j - j % 2][1], tv)
        out += [g, c]
    return out


# --- the end screens -----------------------------------
# GAME OVER and VICTORY: 192 lines like the title, drawn by
# bank 6 (ends_kernel.asm). The decor is the title's (the
# same pillars and torches) in other colours: GAME OVER cold,
# the torches burnt down to embers; VICTORY warm, the flames
# bright. Blocks of 48 pixels as on the title: the crown
# (whole on GAME OVER: the curse goes on; broken on
# VICTORY), the words, the score in the digits of the HUD
# (copied into the Superchip RAM each frame), and a scene:
# the Serpent King alone, or Sir Roderick and the pieces of
# the crown.

END_KINDS = ("gameover", "victory")
END_BLOCKS = {
    "gameover": (("emblem", 46), ("GAME", 74), ("OVER", 92),
                 ("score", 114)),
    "victory": (("emblem_broken", 45), ("VICTORY", 83),
                ("score", 114)),
}
# the scene: player 0 and player 1 (column, figure, mirror,
# NUSIZ1: 5 twice as wide, 7 four times), at the bottom of
# the 41 lines of the title's scene
END_SCENES = {
    "gameover": dict(p0=None,
                     p1=dict(name="king_a", x=68, mirror=True,
                             nus=5)),
    "victory": dict(p0=dict(name="knight_stand", x=56,
                            mirror=False),
                    p1=dict(name="crown_broken", x=72,
                            mirror=False, nus=7)),
}
GAMEOVER_COLOURS = (0x0E, 0x0E, 0x0C, 0x0C, 0x0A, 0x9A, 0x98,
                    0x98, 0x96, 0x96, 0x94, 0x84, 0x82, 0x82)


def word_rows(word, narrow=False):
    """A word in the letters of the title (7 x 7, 9 pixels
    apart, centred) or, narrow, in the letters of VICTORY
    (6 x 7, 7 pixels apart): rows of 48 from the top, each
    on two lines, and an empty line."""
    font, pitch = (art.NARROW, 7) if narrow else (art.LETTERS, 9)
    wide = len(font[word[0]][0])
    x0 = (48 - (pitch * (len(word) - 1) + wide)) // 2
    rows = []
    for y in range(7):
        line = ["."] * 48
        for i, ch in enumerate(word):
            for k, c in enumerate(font[ch][y]):
                line[x0 + pitch * i + k] = c
        rows += ["".join(line)] * 2
    return rows + ["." * 48]


def score_rows(score):
    """The score in the digits of the HUD, 6 x 8 in columns of
    8 pixels, from the top, and an empty line."""
    text = f"{score:06d}"
    rows = []
    for y in range(8):
        rows.append("".join(art.DIGITS[int(ch)][y] + ".."
                            for ch in text))
    return rows + ["." * 48]


def end_block_lines(name, score=0):
    """Rows of a block of an end screen, from the top; the last
    is empty."""
    if name == "score":
        return score_rows(score)
    if name in ("emblem", "emblem_broken"):
        rows = []
        for r in (art.EMBLEM if name == "emblem"
                  else art.EMBLEM_BROKEN):
            wide = "".join(ch * 2 for ch in r)
            rows += [wide, wide]
        return rows + ["." * 48]
    return word_rows(name, narrow=name == "VICTORY")


def end_block_colours(name):
    """One colour per line of a block of an end screen, from
    the top (NTSC)."""
    n = len(end_block_lines(name))
    if name == "score":
        return [HUD_SCORE_COLOUR] * (n - 1) + [0]
    if name == "emblem":
        return title_block_colours("emblem")
    if name == "emblem_broken":
        return [title_block_colours("emblem")[min(i, 19)]
                for i in range(n - 1)] + [0]
    if name in ("GAME", "OVER"):
        return list(GAMEOVER_COLOURS) + [0]
    return list(LOGO_COLOURS) + [0]


def end_decor(kind):
    """The title's decor in the colours of an end screen, per
    line from the top: (COLUBK, COLUPF, stone cells)."""
    out = []
    for line, (bg, pfc, cells) in enumerate(title_decor()):
        if line < 4:
            out.append((bg, pfc, cells))
            continue
        if kind == "gameover":
            if line < 46:               # a cold, dark glow
                bg = 0x90 | min(4, (46 - line) // 10 * 2)
            elif line >= TITLE_SCENE:   # and a dark floor
                bg = 0x80 | min(2, (line - TITLE_SCENE) // 20 * 2)
            if 16 <= line < 30:         # embers, not flames
                pfc = (0x40, 0x40, 0x40, 0x40, 0x40, 0x40, 0x42,
                       0x42, 0x42, 0x44, 0x44, 0x42, 0x42,
                       0x40)[line - 16]
            elif 30 <= line < 36:       # the bowl
                pfc = 0x22 if line < 33 else 0x20
            elif 36 <= line < 186:      # the pillar, darker
                pfc = 0x04 if (line // 8) % 2 else 0x06
        else:
            if line < 46:               # a golden glow
                bg = 0x20 | min(8, (46 - line) // 6 * 2)
            elif line >= TITLE_SCENE:   # and a warm floor
                bg = 0x30 | min(6, (line - TITLE_SCENE) // 8 * 2)
            if 16 <= line < 30:         # the flames, bright
                pfc = (0x1E, 0x1E, 0x1E, 0x1E, 0x0E, 0x0E, 0x0E,
                       0x0E, 0x1E, 0x1E, 0x2E, 0x2E, 0x2C,
                       0x2C)[line - 16]
            elif 30 <= line < 36:
                pfc = 0x2A if line < 33 else 0x28
            elif 36 <= line < 186:
                pfc = 0x08 if (line // 8) % 2 else 0x0A
        out.append((bg, pfc, cells))
    return out


def end_scene_tables(kind, tv):
    """Bottom first, SCENE_H entries: player 0 graphics and
    colours, player 1 graphics and colours."""
    out = []
    sc = END_SCENES[kind]
    for key in ("p0", "p1"):
        fig = sc[key]
        g = [0] * SCENE_H
        c = [0] * SCENE_H
        if fig:
            lines = figure_lines(fig["name"])
            cols = (king_colours(tv) if fig["name"].startswith("king")
                    else pose_colours(fig["name"], tv))
            for j, (bits, _) in enumerate(lines):
                k = len(lines) - j       # index from the bottom
                g[k] = bits
                c[k] = cols[j]
        out += [g, c]
    return out


def end_picture(kind, tv, x0, score):
    """The expected end screen, 160 x 192 values, the blocks at
    column x0."""
    dec = end_decor(kind)
    pic = []
    for line in range(TITLE_LINES):
        bg, pfc, cells = dec[line]
        row = cells + cells[::-1]
        pic.append([tv_colour(pfc, tv) if row[x // 4] else
                    tv_colour(bg, tv) for x in range(160)])
    for line in range(TITLE_SETUP, TITLE_SCENE + SCENE_H):
        pic[line] = list(pic[TITLE_SETUP - 1])
    sc = END_SCENES[kind]
    for key, off in (("p1", 4), ("p0", 3)):
        fig = sc[key]
        if not fig:
            continue
        f = {5: 2, 7: 4}.get(fig.get("nus"), 1)
        lines = figure_lines(fig["name"])
        cols = (king_colours(tv) if fig["name"].startswith("king")
                else pose_colours(fig["name"], tv))
        y0 = TITLE_SCENE + SCENE_H - 1 - len(lines)
        for j, (bits, _) in enumerate(lines):
            for i in range(8):
                b = 7 - i if fig["mirror"] else i
                if bits & (0x80 >> b):
                    for w in range(f):
                        pic[y0 + j][fig["x"] + (off if f > 1 else 3)
                                    + f * i + w] = cols[j]
    for name, top in END_BLOCKS[kind]:
        rows = end_block_lines(name, score)
        cols = end_block_colours(name)
        for i, r in enumerate(rows):
            line = top + i
            pic[line] = list(pic[top - 1])
            for x, ch in enumerate(r):
                if ch == "#":
                    pic[line][x0 + x] = tv_colour(cols[i], tv)
    return pic
