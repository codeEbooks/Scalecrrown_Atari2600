"""build_assets.py - the data of Scalecrown.

    python3 game/assets/build_assets.py

From art.py (figures, digits, letters, emblem), dungeon.py and
rooms.py (the 16 rooms and their things), look.py (light,
colours) and rules.py (speeds, times) it writes, in generated/:

  kfig0.asm   Sir Roderick's figures in one block, with zeros
              between them where the kernel may read them (only
              as many as the top lines he is drawn at need),
              and his colours (those of the thrust padded as # {2}
              well: they switch the blade) # {2}
  kfig2.asm   the same bytes, for bank 2 # {6}
  bank0.asm   the figures of player 1 in one block, as his, # {4}
              and their colours; # {4}
              the colour tables of the rooms: one for each
              level (COLUBK and COLUPF interleaved) and the
              floors with the flames of the torches
  bank1.asm   the title: emblem and letters in six columns, # {8}
              colours of each line # {8}
  bank2.asm   the throne room: the figures of the King and of # {6}
              the crown, their colours, the colours of the room # {6}
  bank3.asm   the playfield of the 16 rooms (PF0, PF1, PF2 of
              the 20 courses), copied into the Superchip RAM
              when Sir Roderick comes in: the grate closed and
              the plates down; the bytes of the open grate # {3}
  bank4.asm   the things: the versions of the rows (the plates # {4}
              down and up, the grate open), where he touches a # {4}
              chest, a door, a plate; the times of the spikes; # {4}
              the points; # {4}
              the guards; # {5}
              the Serpent King # {6}
  bank5.asm   the music and the effects (music.py: score.py, # {7}
              sfx.py) # {7}
  bank6.asm   the end screens: the decor of the title in their # {8}
              colours, the crown whole and broken, GAME OVER and # {8}
              VICTORY in six columns, the colours of the score # {8}
              (its digits are in the Superchip RAM), the scenes # {8}
  bank7.asm   the numbers of each television (rules.py); for
              each room the colour tables; # {1-1}
              each room the colour tables, the collision maps; # {2-3}
              each room the colour tables, the collision maps # {4}
              (with the door open and closed), player 1 (the # {4}
              chest or the gate); # {4}
              the guards, the seam; # {5}
              the plug (the ball), the torch flicker; the name # {3}
              of each level for the HUD; # {3}
              the pointer bases of the figures;
              the HUD (digits, colours, energy bar) # {3}
  game.json   what the tests and the notes may want
Every table that differs between NTSC and PAL is written
twice, chosen with IF PAL.

The playfield bit order, the order of the tables in the
Superchip RAM, the interleaving of the colour tables, the
order of the figures and the order of the bits of the
collision maps are decided here and only here (look.py has
the design they encode).
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import art                                            # noqa: E402
import dungeon                                        # noqa: E402
import look                                           # noqa: E402
import rooms                                          # noqa: E402
import rules                                          # noqa: E402
import music                                          # noqa: E402 {7}

GEN = os.path.join(HERE, "generated")
LINES = 160
NROOMS = len(dungeon.ROOMS)
KNIGHT_FRAMES = ["knight_stand", "knight_walk1", "knight_walk2",  # {2}
                 "knight_thrust", "knight_parry"]  # {6}
#|                 "knight_thrust"] {2-5}
#|KNIGHT_FRAMES = ["knight_stand"] {1-1}
# P1 figures of the room kernel (bank 0): (art, colour level or  # {4}
# None); two frames each  # {4}
# (the Serpent King and the crown are in the bank of the  # {6}
# throne room: bank 2, THRONE_FRAMES)  # {6}
# (the empty figure first: p1_bands takes a figure of a  # {5}
# guard, never 0, as "always")  # {5}
OBJ_FRAMES = [("none", None), ("none", None)] # {4}
for lv in (1, 2, 3, 4): # {5}
    OBJ_FRAMES += [("serpent_a", lv), ("serpent_b", lv)] # {5}
for n in ("chest", "chest_open", "gate"): # {4}
    OBJ_FRAMES += [(n, None), (n, None)] # {4}
# the figures of the throne room (bank 2): the King's two  # {6}
# frames, the crown and its pieces  # {6}
THRONE_FRAMES = ["king_a", "king_b", "crown", "crown_broken"]  # {6}
# the colours of player 1 there: the King plain, spitting,  # {6}
# flashing, both; the crown, its pieces  # {6}
THRONE_COLOURS = ["king", "king_spit", "king_flash",  # {6}
                  "king_flash_spit", "crown", "crown_broken"]  # {6}
# the colour schemes of the rooms: (level, torches); the rooms
# of a level share one, the rooms with torches the flames too
# (the throne room has its own, in bank 2)  # {6}
SCHEMES = [(1, False), (2, False), (2, True), (3, False),
           (4, False), (4, True), "throne"]  # {6}
#|           (4, False), (4, True)] {1-5}
TORCH_LEVELS = (2, 4)           # the two floors of the flames


def hexs(vals):
    if any(not 0 <= v <= 255 for v in vals):
        raise SystemExit(f"a byte out of 0-255: {vals}")
    return ",".join(f"${v:02X}" for v in vals)


def data_lines(label, vals, comment=None, per=11, page=False):
    """A table; with page=True it is kept inside one page
    (a load from it never takes the extra cycle)."""
    out = []
    if comment:
        out.append(f"; {comment}")
    if page:
        out += [f"        IF >* != >(*+{len(vals) - 1})",
                "        ALIGN 256", "        ENDIF"]
    out.append(f"{label}")
    for i in range(0, len(vals), per):
        out.append(f"        .byte {hexs(vals[i:i + per])}")
    return out


def expr_table(label, exprs, op):
    """A table of low (op "<") or high (">") bytes of
    addresses written as expressions."""
    out = [label]
    for i in range(0, len(exprs), 3):
        out.append("        .byte " + ", ".join(
            f"{op}({x})" for x in exprs[i:i + 3]))
    return out


def tv_block(fn):
    """fn(tv) -> lines, written for NTSC and for PAL."""
    out = []
    for tv in ("ntsc", "pal"):
        out.append("        IF " + ("!PAL" if tv == "ntsc"
                                     else "PAL"))
        out += fn(tv)
        out.append("        ENDIF")
    return out


def half_to_pf(cells):
    """20 cells of 4 pixels (the left half) -> PF0, PF1, PF2.

    On the screen the bits come in this order:
      PF0 bits 4, 5, 6, 7; PF1 bits 7 down to 0;
      PF2 bits 0 up to 7."""
    pf0 = sum(1 << (4 + i) for i in range(4) if cells[i])
    pf1 = sum(1 << (7 - i) for i in range(8) if cells[4 + i])
    pf2 = sum(1 << i for i in range(8) if cells[12 + i])
    return pf0, pf1, pf2


def map_bytes(walls): # {2}
    """A collision map: three bytes a row of blocks, the whole # {2}
    width (the plug makes a room lopsided): blocks 0-7 in # {2}
    bits 7-0 of the first byte, 8-15 of the second, 16-19 in # {2}
    bits 7-4 of the third.""" # {2}
    vals = [] # {2}
    for row in walls: # {2}
        for k in range(3): # {2}
            vals.append(sum(0x80 >> i for i in range(8) # {2}
                            if 8 * k + i < 20 and row[8 * k + i])) # {2}
    return vals # {2}


def scheme(r):
    if dungeon.throne(r): # {6}
        return SCHEMES.index("throne") # {6}
    rm = dungeon.ROOMS[r]
    return SCHEMES.index((rm["level"], rooms.torches(rm)))


# --- figures: padded graphics, colours -----------------------

def figure_block(items, label):
    """Several tables of a figure each, in one block with
    zeros between them: the kernel reads a figure for every
    line of its window without testing where it is, so the
    bytes it reads must be the figure and zeros. items:
    (name, values bottom first, uses), a use being (top line,
    first line read, last line read): Sir Roderick is read on
    all 160 lines of the room, player 1 on its band (the seam
    cuts the room in two). A figure h lines high drawn
    from top line t and read from line l0 to l1 needs
    l1 - t - h + 1 zeros below its table (the lines below it)
    and t - l0 above (the lines above it), shared with its
    neighbours. The order of the tables that needs the fewest
    zeros is found by trying them all (a search over the
    subsets; ties broken by the order of items). Returns
    lines, the offset of each table (in the order of items)
    and the size of the block.

    An empty figure (h = 0) is only zeros: it is where the
    kernel reads for a band of player 1 that shows nothing."""
    n = len(items)
    pre = [max([0] + [l1 - t - len(v) + 1 for t, _, l1 in u])
           for _, v, u in items]
    post = [max([0] + [t - l0 for t, l0, _ in u])
            for _, _, u in items]
    full = (1 << n) - 1
    best = {}                   # (set, last) -> (zeros, order)
    for i in range(n):
        best[(1 << i, i)] = (pre[i], (i,))
    for mask in range(1, full + 1):
        for last in range(n):
            if (mask, last) not in best:
                continue
            z, order = best[(mask, last)]
            for j in range(n):
                if mask & (1 << j):
                    continue
                key = (mask | (1 << j), j)
                c = (z + max(post[last], pre[j]), order + (j,))
                if key not in best or c < best[key]:
                    best[key] = c
    z, order = min((best[(full, last)][0] + post[last],
                    best[(full, last)][1]) for last in range(n))
    data, offsets = [], [0] * n
    prev = None
    for i in order:
        data += [0] * (pre[i] if prev is None
                       else max(post[prev], pre[i]))
        offsets[i] = len(data)
        data += items[i][1]
        prev = i
    data += [0] * post[prev]
    out = [f"; {label}: bottom first; between them only the zeros",
           "; that the lines each one is read at need (zeros",
           "; below it, above it):"]
    out += [f";   {items[i][0]} ({pre[i]}, {post[i]})" for i in order]
    out += data_lines(label, data, per=11)
    return out, offsets, len(data)


KIND_OF = {"serpent_a": "serpent", "serpent_b": "serpent", # {4}
           "king_a": "king", "king_b": "king"} # {4}
FRAMES_OF = {"serpent": ("serpent_a", "serpent_b"), # {4}
             "king": ("king_a", "king_b")} # {4}


def ob_col(name, level): # {4}
    return f"OB_COL_{name}_{level or 0}".upper() # {4}


def p1_uses(): # {4}
    """For each figure of player 1, its uses: (top line, first # {4}
    line read, last line read), from what player 1 can show in # {4}
    each band of each room (dungeon.p1_shows, windows).""" # {4}
    uses = {} # {4}
    for r in range(NROOMS): # {4}
        wa, wb = dungeon.windows(r) # {4}
        for band, kind, top in dungeon.p1_shows(r): # {4}
            lo, hi = wa if band == "A" else wb # {4}
            for n in FRAMES_OF.get(kind, (kind,)): # {4}
                uses.setdefault(n, set()).add((top, lo, hi)) # {4}
    return uses # {4}


def shared(tables):
    """{label: values} -> {label: the label of the first table
    with the same values on both televisions}, to write each
    table once."""
    first, out = {}, {}
    for lab, vals in tables.items():
        key = tuple(tuple(vals[tv]) for tv in ("ntsc", "pal"))
        out[lab] = first.setdefault(key, lab)
    return out


def gfx(name):
    return [bits for bits, _ in reversed(look.figure_lines(name))]


def colour_rows(name, level=None):
    """Colour values of a figure, bottom first, NTSC and PAL."""
    return {tv: list(reversed(look.pose_colours(name, tv, level)))
            for tv in ("ntsc", "pal")}


# --- the versions of the rows -----------------------------  # {3}

def door_bits(r): # {4}
    """The bit of the door of room r in `opened` (0: none).""" # {4}
    if not dungeon.door(r): # {4}
        return 0 # {4}
    return dungeon.door_bit(dungeon.ROOMS[r]["level"]) # {4}


def sc_bytes(st): # {3}
    """The 60 bytes of the Superchip for a room drawn as st.""" # {3}
    pf = [half_to_pf(st[c][:20]) for c in range(20)] # {3}
    return [pf[19 - i][k] for k in range(3) for i in range(20)] # {3}


def version_lists(): # {3}
    """For each room, the bytes of the Superchip that change # {3}
    with the state of its things, as (index, value): the open # {3}
    grate ("door"), the plates down and up. The playfield of # {3}
    bank 3 is the room with the grate closed and the plates # {3}
    down; the logic writes the other versions.""" # {3}
    vl = dict(door={}, down={}, up={}) # {3}
    for r, rm in enumerate(dungeon.ROOMS): # {3}
        base = sc_bytes(look.stone(rm, 0, closed=True)) # {3}
        if rooms.grate(rm): # {3}
            op = sc_bytes(look.stone(rm, 0, closed=False)) # {3}
            vl["door"][r] = [(i, v) for i, v in enumerate(op) # {3}
                             if v != base[i]] # {3}
        if rm.get("plate") is not None: # {4}
            up = sc_bytes(look.stone(rm, 0, closed=True, # {4}
                                     raised=True)) # {4}
            idx = [i for i, v in enumerate(up) if v != base[i]] # {4}
            vl["up"][r] = [(i, up[i]) for i in idx] # {4}
            vl["down"][r] = [(i, base[i]) for i in idx] # {4}
    for kind, lists in vl.items(): # {3}
        for r, ent in lists.items(): # {3}
            if len(ent) != 2: # {3}
                raise SystemExit(f"room {r}: {kind} changes " # {3}
                                 f"{len(ent)} bytes, not 2") # {3}
    return vl # {3}


def list_tables(suffix, named): # {3}
    """Lists of (index, value) in two tables, VI and VV, each # {3}
    list ended by the index $FF; entry 0 is the empty list. # {3}
    For each name, the start of the list of every room.""" # {3}
    vi, vv, out = [0xFF], [0], [] # {3}
    starts = {} # {3}
    for name, lists in named.items(): # {3}
        st = [] # {3}
        for r in range(NROOMS): # {3}
            ent = lists.get(r, []) # {3}
            st.append(len(vi) if ent else 0) # {3}
            for i, v in ent: # {3}
                vi.append(i) # {3}
                vv.append(v) # {3}
            if ent: # {3}
                vi.append(0xFF) # {3}
                vv.append(0) # {3}
        starts[name] = st # {3}
    if len(vi) > 256: # {3}
        raise SystemExit("version lists over 256 entries") # {3}
    out += data_lines(f"VI{suffix}", vi, "Superchip index, " # {3}
                      "$FF: end of a list", per=10) # {3}
    out += data_lines(f"VV{suffix}", vv, "its value", per=10) # {3}
    for name, st in starts.items(): # {3}
        out += data_lines(f"{name}{suffix}", st, per=8) # {3}
    return out # {3}


def bank4(vl): # {4}
    """The tables of things.asm.""" # {4}
    out = ["; the plates of the spikes, down (SPD) and up (SPU),", # {4}
           "; and the open door (DOP): lists of the bytes of the", # {4}
           "; Superchip of each version"] # {4}
    out += list_tables("4", {"SPD": vl["down"], "SPU": vl["up"], # {4}
                             "DOP": vl["door"]}) # {4}
    zones = [dungeon.zone(r) for r in range(NROOMS)] # {4}
    out += ["", "; the thing of each room: its bit in `opened` (0:", # {4}
            "; none; a chest below $10, a door from $10), where", # {4}
            "; he touches it: columns TX0 to TX1-1, top lines TY0", # {4}
            "; to TY1-1"] # {4}
    out += data_lines("TBIT", [dungeon.thing_bit(r) # {4}
                               for r in range(NROOMS)], per=8) # {4}
    for lab, i, j in (("TX0", 0, 0), ("TX1", 0, 1), ("TY0", 1, 0), # {4}
                      ("TY1", 1, 1)): # {4}
        out += data_lines(lab, [ # {4}
            (z[i][j] + j if z else 255) for z in zones], per=8) # {4}
    pz = [dungeon.plate_zones(r) for r in range(NROOMS)] # {4}
    ys = {p[1] for p in pz if p} # {4}
    if len(ys) != 1: # {4}
        raise SystemExit("the plates in the same lines") # {4}
    y0, y1 = ys.pop() # {4}
    out += ["", "; the plates: the columns where the middle of his", # {4}
            "; feet is over the first (PXA0 to PXA1-1) or the", # {4}
            "; second (PXB0 to PXB1-1); his top line from", # {4}
            "; PLATE_Y0 to PLATE_Y1-1; 255: no plates", # {4}
            f"PLATE_Y0 = {y0}", f"PLATE_Y1 = {y1 + 1}"] # {4}
    for lab, i, j in (("PXA0", 0, 0), ("PXA1", 0, 1), # {4}
                      ("PXB0", 1, 0), ("PXB1", 1, 1)): # {4}
        out += data_lines(lab, [(p[0][i][j] + j if p else 255) # {4}
                                for p in pz], per=8) # {4}
    out += ["", "; times (rules.py): frames down by level, frames", # {4}
            "; up, frames before a plate hurts again"] # {4}
    out += tv_block(lambda tv: data_lines( # {4}
        "TH_DOWN", rules.spike_frames(tv)[0]) + [ # {4}
        f"SPK_UP = {rules.spike_frames(tv)[1]}", # {4}
        f"HURT_FRAMES = {rules.spike_frames(tv)[2]}"]) # {4}
    out += ["; points, added to the middle byte of the score", # {4}
            f"CHEST_BCD = ${rules.bcd_hundreds(rules.CHEST_POINTS):02X}", # {4}
            f"DOOR_BCD = ${rules.bcd_hundreds(rules.DOOR_POINTS):02X}", # {4}
            f"SERPENT_BCD = " # {5}
            f"${rules.bcd_hundreds(rules.SERPENT_POINTS):02X}", # {5}
            f"SPIKE_DAMAGE = {rules.SPIKE_DAMAGE}", # {5}
            f"BITE_DAMAGE = {rules.BITE_DAMAGE}"] # {5}
#|            ] {4-4}
    # the guards. Entry r the first guard of room r, 16 + r {5}
    # the second: top line (0: none), the columns of its path; {5}
    # and the speed of each room (rules.crawl: a fraction a {5}
    # frame; in the King's room his own) {5}
    guards = [dungeon.ROOMS[r]["guards"] for r in range(NROOMS)] # {5}
    slot = [g[k] if len(g) > k else None # {5}
            for k in (0, 1) for g in guards] # {5}
    out += ["", "; the guards: entry r the first of room r,", # {5}
            "; 16 + r the second; top line (0: none), path from", # {5}
            "; S_MIN to S_MAX (all serpents)"] # {5}
    out += data_lines("S_TOP4", [g["top"] if g else 0 for g in slot], # {5}
                      per=8) # {5}
    out += data_lines("S_MIN4", [g["path"][0] if g else 0 # {5}
                                 for g in slot], per=8) # {5}
    out += data_lines("S_MAX4", [g["path"][1] if g else 0 # {5}
                                 for g in slot], per=8) # {5}
    out += ["; the speed of the guards of each room: a fraction of", # {5}
            "; a pixel a frame"] # {5}
    out += tv_block(lambda tv: data_lines("CRAWL", [ # {5}
        rules.crawl(None if g and g[0]["kind"] == "king" # {5}
                    else dungeon.ROOMS[r]["level"], tv) # {5}
        for r, g in enumerate(guards)], per=8)) # {5}
    # the sprint of a chasing serpent (rules.sprint: a {9}
    # whole pixel or none, and a fraction a frame), the push of {9}
    # the first blow {9}
    out += ["; the sprint of the chase in each room: the", # {9}
            "; whole pixels (SPRI) and the fraction (SPRF) a frame;", # {9}
            "; the push of the first blow", # {9}
            f"KNOCK_PX = {rules.KNOCK_PX}"] # {9}
    out += tv_block(lambda tv: data_lines("SPRI", [ # {9}
        rules.sprint(dungeon.ROOMS[r]["level"], tv)[0] # {9}
        for r in range(NROOMS)], per=8) + data_lines("SPRF", [ # {9}
        rules.sprint(dungeon.ROOMS[r]["level"], tv)[1] # {9}
        for r in range(NROOMS)], per=8)) # {9}
    out += throne4() # {6}
    return out # {4}


def ranges(test): # {6}
    """The columns 0-X_MAX of Sir Roderick where test(kx) holds: # {6}
    one run (first, count), for a compare in the cartridge.""" # {6}
    xs = [x for x in range(rules.X_MAX + 1) if test(x)] # {6}
    if not xs or xs != list(range(xs[0], xs[-1] + 1)): # {6}
        raise SystemExit("not one run of columns") # {6}
    return xs[0], len(xs) # {6}


def blade_pixels(kx, kdir): # {6}
    """The blade's (first pixel, width), as knight.asm puts it # {6}
    (the model has the same rule).""" # {6}
    if kdir == 0: # {6}
        x0 = kx + rules.FIRST_PIXEL + rules.KNIGHT_W # {6}
        for w in (8, 4, 2, 1): # {6}
            if x0 + w <= 160: # {6}
                return x0, w # {6}
        return None # {6}
    end = kx + rules.FIRST_PIXEL - 1 # {6}
    for w in (8, 4, 2, 1): # {6}
        if end - w + 1 >= 0: # {6}
            return end - w + 1, w # {6}
    return None # {6}


def meets(a0, a1, b0, b1): # {6}
    return a0 <= b1 and b0 <= a1 # {6}


def throne4(): # {6}
    """The tables and numbers of the Serpent King.""" # {6}
    th = dungeon.THRONE # {6}
    t0, t1 = th["top"] # {6}
    ka, kb = dungeon.king_pixels() # {6}
    ca, cb, c0, c1 = dungeon.crown_box() # {6}
    kw = rules.FIRST_PIXEL # {6}
    out = ["", "; the throne room (its room, the King's column and",  # {6}
           "; top lines, the crown: bank7.asm): the King's height,",  # {6}
           "; his head (where the blade strikes him),",  # {9}
           "; his mouth, where the venom starts, the free pixels of",  # {6}
           "; the venom for each top line of the King",  # {6}
           "; ((top - KING_T0) / 2: from VSPAN_LO to VSPAN_HI)",  # {6}
           f"KING_H = {dungeon.height('king')}", # {6}
           f"KING_HEAD = {th['head']}", # {9}
           f"MOUTH = {th['mouth']}", # {6}
           f"VEN_LEFT = {dungeon.venom_start(False)}", # {6}
           f"VEN_RIGHT = {dungeon.venom_start(True)}"] # {6}
    spans = [dungeon.venom_span(t) for t in range(t0, t1 + 1, 2)] # {6}
    out += data_lines("VSPAN_LO", [a for a, _ in spans], per=8) # {6}
    out += data_lines("VSPAN_HI", [b for _, b in spans], per=8) # {6}
    # where his blade meets the King (pixels ka-kb) or the crown, {6}
    # facing right and left: a run of columns; his box meets {6}
    # the King's at a run of columns too {6}
    for lab, (a, b) in (("KB", (ka, kb)), ("CB", (ca, cb))): # {6}
        for d, kd in (("R", 0), ("L", 8)): # {6}
            x0, n = ranges(lambda x: blade_pixels(x, kd) and meets( # {6}
                blade_pixels(x, kd)[0], # {6}
                blade_pixels(x, kd)[0] + blade_pixels(x, kd)[1] - 1, # {6}
                a, b)) # {6}
            out += [f"{lab}_{d}0 = {x0}", f"{lab}_{d}N = {n}"] # {6}
    x0, n = ranges(lambda x: meets(x + kw, x + kw + rules.KNIGHT_W - 1, # {6}
                                   ka, kb)) # {6}
    out += [f"KBITE_X0 = {x0}", f"KBITE_N = {n}", # {6}
            f"CROWN_H = {c1 - c0 + 1}", # {6}
            f"VENOM_DAMAGE = {rules.VENOM_DAMAGE}", # {6}
            f"KHIT_BCD = ${rules.bcd_hundreds(rules.KING_HIT_POINTS):02X}", # {6}
            f"KING_BCD = ${rules.bcd_hundreds(rules.KING_POINTS):02X}", # {6}
            f"ENERGY_BCD = ${rules.bcd_hundreds(rules.ENERGY_POINTS):02X}", # {6}
            f"KING_HITS = {rules.KING_HITS}", # {6}
            "; the time between two spits by the blows he has had", # {6}
            "; (the other times of each television: bank7.asm)"] # {6}
    out += tv_block(lambda tv: data_lines( # {6}
        "SPIT", rules.spit_frames(tv), per=8)) # {6}
    return out # {6}


def build():
    os.makedirs(GEN, exist_ok=True)
    info = dict(rooms=NROOMS, lines=LINES)

    # --- Sir Roderick: his figures, the colours of the thrust  # {2}
    # (padded: they switch the blade) and his other colours,  # {2}
#|    # --- Sir Roderick: his figures and his colours {1-1}
    # the same bytes at the start of bank 0 and of bank 2  # {6}
    # (kfig0.asm, kfig2.asm): the pointers that prep_room  # {6}
    # makes work in both kernels  # {6}
    thrust = KNIGHT_FRAMES.index(art.BLADE_POSE) # {2}
    kt = [(t, 0, LINES - 1) for t in (rules.TOP_MIN, rules.TOP_MAX)]
    kcols = {f"KN_COL{i}": colour_rows(n) for i, n in
             enumerate(KNIGHT_FRAMES) if i != thrust} # {2}
#|             enumerate(KNIGHT_FRAMES)} {1-1}
    kcols["KN_FLASH"] = {tv: [look.tv_colour(rules.FLASH_COLOUR, tv)] # {5}
                         * rules.KNIGHT_H for tv in ("ntsc", "pal")} # {5}
    ksame = shared(kcols)

    def kfig(suffix):
        out = [f"; generated by build_assets.py - Sir Roderick for "
               f"bank {suffix or 0}", "",
               "; his figures and the colours of the thrust (they",  # {2}
               "; also switch the blade)"]  # {2}
#|               "; his figures"] {1-1}

        def block(tv):
            items = [(n, gfx(n), kt) for n in KNIGHT_FRAMES]
            items.append(("the colours of the thrust", # {2}
                          colour_rows(art.BLADE_POSE)[tv], kt)) # {2}
            lines, off, size = figure_block(items, "KFG" + suffix)
            kfig.off, kfig.size = off, size
            return lines
        out += tv_block(block)
        out += ["", "; the colours of the other poses and of the",
                "; flash, bottom first (outside the figure the kernel",
                "; reads whatever follows: the graphics there are",
                "; zero)"]
        out += tv_block(lambda tv: sum(
            (data_lines(lab + suffix, v[tv]) for lab, v in kcols.items()
             if ksame[lab] == lab), []))
        out.append(f"KFG_END{suffix}")
        return out
    for suffix, name in (("", "kfig0.asm"), ("_2", "kfig2.asm")): # {6}
#|    for suffix, name in (("", "kfig0.asm"),): {1-5}
        open(os.path.join(GEN, name), "w").write(
            "\n".join(kfig(suffix)) + "\n")
    koff = kfig.off[:len(KNIGHT_FRAMES)]
    toff = kfig.off[len(KNIGHT_FRAMES)] # {2}

    # --- bank 0: player 1 and the colours of the room kernel  # {4}
#|    # --- bank 0: the colours of the room kernel {1-3}
    b0 = ["; generated by build_assets.py - bank 0", ""]
    uniq = list(dict.fromkeys(n for n, _ in OBJ_FRAMES)) # {4}
    uses = p1_uses() # {4}

    def figures(tv): # {4}
        items = [(n, gfx(n), sorted(uses[n])) for n in uniq] # {4}
        lines, off, size = figure_block(items, "FG") # {4}
        figures.off, figures.size = off, size # {4}
        return lines # {4}
    b0 += ["; the figures of player 1"] # {4}
    b0 += tv_block(figures) # {4}
    ooff = figures.off # {4}
    # the colours of the figures of player 1: a table that is {4}
    # the same as one before it is not written again {4}
    ocols = {ob_col(n, lv): colour_rows(n, lv) # {4}
             for n, lv in dict.fromkeys(OBJ_FRAMES)} # {4}
    same = shared(ocols) # {4}
    b0 += ["", "; colours of the figures of player 1, bottom first"] # {4}
    b0 += tv_block(lambda tv: sum( # {4}
        (data_lines(lab, v[tv]) for lab, v in ocols.items() # {4}
         if same[lab] == lab), [])) # {4}
    b0.append("") # {4}

    # colour tables: T[159-2p] = COLUBK of pair p, T[158-2p] =
    # COLUPF of pair p (the kernel reads COLUBK through cbk and
    # COLUPF through cpf, with the same index). One for each
    # level (two for the water); the floors with the flames
    # of levels 2 and 4 are COLUBK only, interleaved in one
    # block: the first at its odd bytes, the second at the even
    # ones (its table starts a byte later)
    def colours(tv):
        out = []
        for lv in (1, 2, 3, 4):
            shim = (0, 1) if rooms.LEVELS[lv]["shimmer"] else (0,)
            for fr in shim:
                t = [0] * LINES
                for p, (wall, floor) in enumerate(
                        look.pair_colours(lv, False, fr)):
                    t[159 - 2 * p] = look.tv_colour(floor, tv)
                    t[158 - 2 * p] = look.tv_colour(wall, tv)
                out += data_lines(f"RC_{lv}_{fr}", t, per=11)
        tb = [0] * (LINES + 1)
        for k, lv in enumerate(TORCH_LEVELS):
            for p, (_, floor) in enumerate(
                    look.pair_colours(lv, True)):
                tb[k + 159 - 2 * p] = look.tv_colour(floor, tv)
        out += data_lines("RC_FLAME", tb, per=11)
        return out
    b0 += ["; colours of the rooms: 160 bytes for a level, COLUBK",
           "; of pair p at 159-2p and COLUPF at 158-2p; then the",
           "; floors of the rooms with torches, COLUBK only:",
           "; level 2 at RC_FLAME, level 4 at RC_FLAME+1"]
    b0 += tv_block(colours)
    b0.append("")
    open(os.path.join(GEN, "bank0.asm"), "w").write(
        "\n".join(b0) + "\n")

#{6}
    # --- bank 2: the throne room. The King is read on
    # every line of the room at each top line he can have, the
    # crown at its place; the King's colours while he spits
    # are padded as well (bit 1 switches the venom)
    b2 = ["; generated by build_assets.py - bank 2", ""]
    t0, t1 = dungeon.THRONE["top"]
    ku = [(t, 0, LINES - 1) for t in range(t0, t1 + 1, 2)]
    cu = [(dungeon.THRONE["crown"]["top"], 0, LINES - 1)]

    def tcol(name, tv):
        """Colours of a figure of the throne room, bottom
        first."""
        if name.startswith("king"):
            return list(reversed(look.king_colours(
                tv, spit="spit" in name, flash="flash" in name)))
        return colour_rows(name)[tv]

    def throne_block(tv):
        items = [(n, gfx(n), ku if n.startswith("king") else cu)
                 for n in THRONE_FRAMES]
        items += [(f"colours {n}", tcol(n, tv), ku)
                  for n in ("king_spit", "king_flash_spit")]
        lines, off, size = figure_block(items, "TFG")
        throne_block.off, throne_block.size = off, size
        return lines
    b2 += ["; the figures of the throne room: the King's two frames,",
           "; the crown, its pieces; the King's colours while he",
           "; spits (plain and flashing)"]
    b2 += tv_block(throne_block)
    toffs = throne_block.off
    tplain = {f"TC_{n.upper()}": {tv: tcol(n, tv)
                                  for tv in ("ntsc", "pal")}
              for n in ("king", "king_flash", "crown",
                        "crown_broken")}
    tsame = shared(tplain)
    b2 += ["", "; the other colours of player 1, bottom first: the",
           "; King, flashing; the crown, its pieces"]
    b2 += tv_block(lambda tv: sum(
        (data_lines(lab, v[tv]) for lab, v in tplain.items()
         if tsame[lab] == lab), []))

    def throne_colours(tv):
        t = [0] * LINES
        for p, (wall, floor) in enumerate(look.pair_colours(4, True)):
            t[159 - 2 * p] = look.tv_colour(floor, tv)
            t[158 - 2 * p] = look.tv_colour(wall, tv)
        return ["        ALIGN 256", "        .byte 0"] + \
            data_lines("TRC", t, per=11)
    b2 += ["", "; the colours of the throne room (level 4, the flames",
           "; of its torches): COLUBK of pair p at 159-2p, COLUPF",
           "; at 158-2p; from the second byte of a page, so that",
           "; neither pointer (TRC, TRC-1) crosses a page"]
    b2 += tv_block(throne_colours)
    b2.append("")
    open(os.path.join(GEN, "bank2.asm"), "w").write(
        "\n".join(b2) + "\n")
#{}

    # --- bank 3: the playfield of the rooms
    b3 = ["; generated by build_assets.py - bank 3", "",
          "; the rooms for the Superchip RAM: PF0 of the 20",
          "; courses, then PF1, then PF2; course c at index 19-c"]
    flick = {} # {3}
    for r, rm in enumerate(dungeon.ROOMS):
        st = look.stone(rm, 0, closed=True)
        pf = [half_to_pf(st[c][:20]) for c in range(20)]
        sc = []
        for k in range(3):
            sc += [pf[19 - i][k] for i in range(20)]
        b3 += data_lines(f"RS_{r}", sc, f"{r} {rm['name']}", per=10)
        if rooms.torches(rm): # {3}
            st1 = look.stone(rm, 1) # {3}
            flick[r] = [half_to_pf(st1[0][:20]), pf[0]] # {3}
    b3 += [""] + expr_table("RS_LO", [f"RS_{r}" for r in
                                      range(NROOMS)], "<")
    b3 += expr_table("RS_HI", [f"RS_{r}" for r in range(NROOMS)],
                     ">")
    vl = version_lists() # {3}
    b3 += ["", "; the door open: the bytes of the open version,",  # {3}
           "; written after the copy if the door of the room",  # {3}
           "; is open"]  # {3}
    b3 += list_tables("3", {"DOP": vl["door"]})  # {3}
    b3 += data_lines("RDOOR3", [door_bits(r) for r in # {4}
                                range(NROOMS)], per=8) # {4}
    open(os.path.join(GEN, "bank3.asm"), "w").write(
        "\n".join(b3) + "\n")

    # --- bank 4: the things of the rooms {4}
    b4 = ["; generated by build_assets.py - bank 4", ""] # {4}
    b4 += bank4(vl) # {4}
    open(os.path.join(GEN, "bank4.asm"), "w").write( # {4}
        "\n".join(b4) + "\n") # {4}

    # --- bank 7: logic, HUD, the tables of each room
    b7 = ["; generated by build_assets.py - bank 7", ""]
    b7 += ["; speeds and times of each television (rules.py):",
           "; whole part and fraction (1/256) per frame"]
    b7 += tv_block(lambda tv: [f"{k} = {v}" for k, v in
                               rules.table(tv).items()])
    st = dungeon.START
    b7 += [f"START_X = {st['x']}", f"START_TOP = {st['top']}",
           f"START_ROOM = {st['room']}", f"GRID = {dungeon.GRID}",
           f"X_MAX = {rules.X_MAX}", f"TOP_MIN = {rules.TOP_MIN}",
           f"TOP_MAX = {rules.TOP_MAX}", f"STRIDE = {rules.STRIDE}",
           f"ENERGY_FULL = {rules.ENERGY}",
           f"THRUST_POSE = {rules.THRUST_POSE}", ""]
    b7 += data_lines("WALK", list(rules.WALK), # {2}
                     "poses of the walk, a pose every STRIDE") # {2}
    # player 1 in each room: the thing (chest, gate) of  # {4}
    # band A, its figure (OG) closed and open (the bit OB_BIT  # {4}
    # of `opened` chooses), top line and column (the empty  # {4}
    # figure where there is no thing); NUSIZ1;  # {4}
    # the guards: their figures (the serpents of the level),  # {5}
    # and in tables of 32 entries (entry r: the first guard,  # {5}
    # 16 + r: the second) top line (0: none), start column,  # {5}
    # path; the seam (0: none, else its course + 1: the count  # {5}
    # the kernel takes down to 0 in line B1)  # {5}
    first = {} # {4}
    for i, (n, lv) in enumerate(OBJ_FRAMES): # {4}
        first.setdefault((KIND_OF.get(n, n), lv), i) # {4}
    lvs = [rm["level"] for rm in dungeon.ROOMS] # {4}

    def kind(k, lv): # {4}
        if k == "king":         # drawn in bank 2 {6}
            k = "none" # {6}
        return first[(k, lv if k == "serpent" else None)] # {4}
    bits = [dungeon.thing_bit(r) for r in range(NROOMS)] # {4}
    things = [dungeon.thing_item(r) for r in range(NROOMS)] # {4}
    guards = [dungeon.ROOMS[r]["guards"] for r in range(NROOMS)] # {6}
#|    guards = [[] if dungeon.throne(r) else {4-5}
#|              dungeon.ROOMS[r]["guards"] for r in range(NROOMS)] {4-5}
    b7 += ["; player 1: the thing of band A closed and open, the", # {4}
           "; bit that opens it, its top line and column; NUSIZ1"] # {4}
    b7 += data_lines("OB_KIND0", [ # {4}
        kind(t["kind"] if t else "none", lv) # {4}
        for t, lv in zip(things, lvs)], per=8) # {4}
    b7 += data_lines("OB_KIND1", [ # {4}
        kind(dungeon.open_kind(t["kind"]) if t else "none", lv) # {4}
        for t, lv in zip(things, lvs)], per=8) # {4}
    b7 += data_lines("OB_BIT", bits, per=8) # {4}
    b7 += data_lines("OB_TOP", [t["top"] if t else dungeon.NONE_TOP # {4}
                                for t in things], per=8) # {4}
    b7 += data_lines("OB_X", [t["x"] if t else 1 for t in things], # {4}
                     per=8) # {4}
    b7 += data_lines("OB_NUS", [ # {4}
        5 if g and g[0]["kind"] == "king" else 0 for g in guards], # {4}
        per=8) # {4}
    b7 += ["; the guards: their figure; top line (0: none), start", # {5}
           "; column (entry r the first, 16 + r the second)"] # {5}
    b7 += data_lines("S_KIND", [ # {5}
        kind(g[0]["kind"], lv) if g else kind("none", lv) # {5}
        for g, lv in zip(guards, lvs)], per=8) # {5}
    slot = [[g[k] if len(g) > k else None for g in guards] # {5}
            for k in (0, 1)] # {5}
    b7 += data_lines("S_TOP", [g["top"] if g else 0 # {5}
                               for g in slot[0] + slot[1]], per=8) # {5}
    b7 += data_lines("S_X", [g["x"] if g else dungeon.ABSENT_X # {5}
                             for g in slot[0] + slot[1]], per=8) # {5}

    def place(x):               # the count and HMP1 of place {5}
        q, m = divmod(x, 15) # {5}
        return q + 1, (((m - 15) & 0xFF) ^ 7) << 4 & 0xFF # {5}
    b7 += ["; the first guard at its start: the count of the delay", # {5}
           "; of the seam and its fine move (as place does it for", # {5}
           "; the column - 3: RESP1 there writes a cycle later)"] # {5}
    x0 = [g["x"] if g else dungeon.ABSENT_X for g in slot[0]] # {5}
    b7 += data_lines("S_CO", [place(x - 3)[0] for x in x0], per=8) # {5}
    b7 += data_lines("S_HM", [place(x - 3)[1] for x in x0], per=8) # {5}
    seams = [dungeon.seam(r) for r in range(NROOMS)] # {5}
    b7 += ["; the seam: 0 none, else its course + 1"] # {5}
    b7 += data_lines("SEAM", [0 if c is None else c + 1 # {5}
                              for c in seams], per=8) # {5}
    if any(seams[r] is not None and # {5}
           kind(guards[r][0]["kind"], lvs[r]) == 0 # {5}
           for r in range(NROOMS)): # {5}
        raise SystemExit("a guard below a seam has figure 0") # {5}
    blade = [c for _, c in art.ALL[art.BLADE_POSE]].index( # {5}
        art.BLADE_COLOUR) # {5}
    b7 += [f"NONE_KIND = {kind('none', None)}", # {5}
           f"FLASH_FRAMES = {rules.FLASH_FRAMES}", # {5}
           f"BLADE_LINE = {blade}", # {5}
           f"SERPENT_H = {dungeon.SERPENT_H}", ""] # {5}
    # the throne room (dungeon.THRONE): its room;  # {5}
    # the King's column and top lines, the crown; NUSIZ1 for  # {6}
    # them (the King twice as wide, the crown four times;  # {6}
    # missile 1, the venom, 8 pixels); the venom flies left  # {6}
    # when Sir Roderick's column is below SPIT_LEFT (his  # {6}
    # middle left of the King's); the entry of the parry;  # {6}
    # the entry of the colours of the flash  # {5}
    th = dungeon.THRONE  # {5}
    if th["mouth"] != art.KING_MOUTH:  # {6}
        raise SystemExit("the King's mouth: dungeon and art")  # {6}
    b7 += [f"THRONE_ROOM = {th['room']}"]  # {5}
    b7 += ["; the throne room",  # {6}
           f"KING_X = {th['x']}",  # {6}
           f"KING_T0 = {th['top'][0]}", f"KING_T1 = {th['top'][1]}",  # {6}
           f"KING_START = {th['start']}",  # {6}
           f"CROWN_X = {th['crown']['x']}",  # {6}
           f"CROWN_TOP = {th['crown']['top']}",  # {6}
           "NUS_KING = $35", "NUS_CROWN = $37",  # {6}
           f"SPIT_LEFT = {dungeon.spit_left()}",  # {6}
           f"PARRY_POSE = {rules.PARRY_POSE}"]  # {6}
    b7 += [f"FLASH_KC = {len(KNIGHT_FRAMES)}", ""]  # {5}
    # the plug: ENABL for the room (2: the ball is on) and the {3}
    # column that puts the ball's first pixel on 0 or 152 (a {3}
    # ball, like a missile, starts at column + 2) {3}
    plugs = [dungeon.plug(r) for r in range(NROOMS)] # {3}
    b7 += ["; the plug of each room: ENABL, the column of the ball"] # {3}
    b7 += data_lines("PLUG", [2 if p else 0 for p in plugs], per=8) # {3}
    b7 += data_lines("BALL_X", [{None: 0, "west": 158, # {3}
                                 "east": 150}[p] for p in plugs], # {3}
                     per=8) # {3}
    # colours: the scheme of each room, and for each scheme
    # cbk for the two frames of the water and cpf
    b7 += ["; colours: the scheme of each room; for a scheme the",
           "; COLUBK table of the two frames of the water and",
           "; the COLUPF table (a byte before its level's table)"]
    b7 += data_lines("SCHEME", [scheme(r) for r in range(NROOMS)],
                     per=8)
    cb0, cb1, cp = [], [], []
    for sch in SCHEMES:
        if sch == "throne": # {6}
            cb0.append("TRC") # {6}
            cb1.append("TRC") # {6}
            cp.append("TRC-1") # {6}
            continue # {6}
        lv, torch = sch
        shim = rooms.LEVELS[lv]["shimmer"] # {3}
        if torch:
            k = TORCH_LEVELS.index(lv)
            cb0.append(f"RC_FLAME+{k}")
            cb1.append(f"RC_FLAME+{k}") # {3}
        else:
            cb0.append(f"RC_{lv}_0")
            cb1.append(f"RC_{lv}_{1 if shim else 0}") # {3}
        cp.append(f"RC_{lv}_0-1")
    for lab, lst in (("CB0", cb0), ("CB1", cb1), ("CP", cp)): # {3}
#|    for lab, lst in (("CB0", cb0), ("CP", cp)): {1-2}
        b7 += expr_table(f"{lab}_LO", lst, "<")
        b7 += expr_table(f"{lab}_HI", lst, ">")
    # HUD colours {3}
    b7 += tv_block(lambda tv: [ # {3}
        f"SCORE_COL = ${look.tv_colour(look.HUD_SCORE_COLOUR, tv):02X}", # {3}
        f"TEXT_COL = ${look.tv_colour(look.HUD_TEXT_COLOUR, tv):02X}"] # {3}
        + data_lines("BAR_COL", [look.tv_colour(c, tv) for c in # {3}
                                 reversed(look.HUD_BAR_COLOURS)], # {3}
                     "energy bar colours, bottom first")) # {3}
    # digits, bottom first {3}
    dig = [] # {3}
    for g in art.DIGITS: # {3}
        dig += [int((r + "..").replace("#", "1").replace(".", "0"), # {3}
                    2) for r in reversed(g)] # {3}
    b7 += data_lines("DIGITS", dig, "digits 0-9, 8 lines each, " # {3}
                     "bottom first", per=8, page=True) # {3}
    # collision maps: three bytes a row of blocks, the whole {2}
    # width (the plug makes a room lopsided): blocks 0-7 in {2}
    # bits 7-0 of the first byte, 8-15 of the second, 16-19 {2}
    # in bits 7-4 of the third {2}
    b7 += ["; collision maps: 10 rows of 3 bytes, block 0 in bit", # {2}
           "; 7 of the first byte, block 8 in bit 7 of the second,", # {2}
           "; block 16 in bit 7 of the third"] # {2}
    cmaps = {} # {2}
    for r in range(NROOMS): # {2}
        vals = map_bytes(dungeon.walls(r)) # {2}
        cmaps[r] = vals # {2}
        b7 += data_lines(f"CM_{r}", vals, per=9) # {2}
    b7 += expr_table("CM_LO", [f"CM_{r}" for r in range(NROOMS)], # {2}
                     "<") # {2}
    b7 += expr_table("CM_HI", [f"CM_{r}" for r in range(NROOMS)], # {2}
                     ">") # {2}
    # the maps with the door closed: stone in the gap of the  # {4}
    # grate, or over the opening of the gate; a room without  # {4}
    # a door has its only map  # {4}
    b7 += ["; collision maps with the door closed; the door's",  # {4}
           "; bit in `opened` (0: no door)"]  # {4}
    closed = {} # {4}
    for r in range(NROOMS): # {4}
        if dungeon.door(r): # {4}
            vals = map_bytes(dungeon.walls(r, closed=True)) # {4}
            closed[r] = vals # {4}
            b7 += data_lines(f"CMC_{r}", vals, per=9) # {4}
    cmc = [f"CMC_{r}" if r in closed else f"CM_{r}" # {4}
           for r in range(NROOMS)] # {4}
    b7 += expr_table("CMC_LO", cmc, "<") # {4}
    b7 += expr_table("CMC_HI", cmc, ">") # {4}
    b7 += data_lines("RDOOR", [door_bits(r) for r in # {4}
                               range(NROOMS)], per=8) # {4}
    b7 += ["; the spikes start down, for the time of the level"] # {4}
    b7 += tv_block(lambda tv: data_lines( # {4}
        "SU_DOWN", rules.spike_frames(tv)[0])) # {4}
    b7.append("") # {4}
    b7 += ["; the torches: course 0 in the two frames of the", # {3}
           "; flicker (PF0-2 odd, even); 0 for a room without"] # {3}
    for r, f in flick.items(): # {3}
        b7 += data_lines(f"RF_{r}", list(f[0]) + list(f[1])) # {3}
    b7 += expr_table("RF_LO", [f"RF_{r}" if r in flick else "0" # {3}
                               for r in range(NROOMS)], "<") # {3}
    b7 += expr_table("RF_HI", [f"RF_{r}" if r in flick else "0" # {3}
                               for r in range(NROOMS)], ">") # {3}
    b7 += ["; the name of each level for the HUD: six columns of",  # {3}
           "; 8 bytes, bottom first,",  # {3}
           "; then the sixth column again with the key after",  # {4}
           "; the name,",  # {4}
           "; in one page (the HUD reads them through pointers,",  # {3}
           "; at fixed cycles)"]  # {3}

    def columns(rows): # {3}
        return [[int(r[8 * col:8 * col + 8].replace( # {3}
            "#", "1").replace(".", "0"), 2) # {3}
            for r in reversed(rows)] for col in range(6)] # {3}
    for lv in (1, 2, 3, 4): # {3}
        plain = columns(look.hud_text_rows(lv)) # {3}
        keyed = columns(look.hud_text_rows(lv, key=True)) # {4}
        if plain[:5] != keyed[:5]: # {4}
            raise SystemExit("the key must be in the sixth column") # {4}
        vals = sum(plain, []) + keyed[5] # {4}
#|        vals = sum(plain, []) {3-3}
        b7 += data_lines(f"TX_{lv}", vals, per=8, page=True) # {3}
    b7 += ["; GAME OVER in the place of the name: six",  # {5}
           "; columns"]  # {5}
    b7 += data_lines("TX_GO", sum(columns(look.game_over_rows()), []),  # {5}
                     per=8, page=True)  # {5}
    b7 += ["; VICTORY in the place of the name"]  # {6}
    b7 += data_lines("TX_VIC", sum(columns(look.victory_rows()), []),  # {6}
                     per=8, page=True)  # {6}
    names = [f"TX_{lv}" for lv in (1, 2, 3, 4)] + ["TX_GO", "TX_VIC"]  # {6}
#|    names = [f"TX_{lv}" for lv in (1, 2, 3, 4)] + ["TX_GO"] {5-5}
#|    names = [f"TX_{lv}" for lv in (1, 2, 3, 4)] {3-4}
    b7 += expr_table("TX_LO", names, "<") # {3}
    b7 += expr_table("TX_HI", names, ">") # {3}
    b7.append("") # {3}
    # pointer bases: address + h - 160 (pointer = base + top)
    b7 += ["; pointer bases of the figures: data + h - 160, so that",
           "; pointer = base + top line"]
    kb = [f"KFG+{koff[i]}+{len(art.ALL[n])}-160"
          for i, n in enumerate(KNIGHT_FRAMES)]
    kc = [f"{ksame[f'KN_COL{i}']}+{len(art.ALL[n])}-160"
          if i != thrust else # {2}
          f"KFG+{toff}+{len(art.ALL[n])}-160" # {2}
          for i, n in enumerate(KNIGHT_FRAMES)] # {2}
#|          for i, n in enumerate(KNIGHT_FRAMES)] {1-1}
    kc.append(f"{ksame['KN_FLASH']}+{rules.KNIGHT_H}-160")  # flash {5}
    ob = [f"FG+{ooff[uniq.index(n)]}+{len(art.ALL[n])}-160" # {4}
          for n, _ in OBJ_FRAMES] # {4}
    oc = [f"{same[ob_col(n, lv)]}+{len(art.ALL[n])}-160" # {4}
          for n, lv in OBJ_FRAMES] # {4}
    # the throne room (bank 2): figures and colours {6}
    tg = [f"TFG+{toffs[i]}+{len(art.ALL[n])}-160" # {6}
          for i, n in enumerate(THRONE_FRAMES)] # {6}
    nf = len(THRONE_FRAMES) # {6}
    tc = [] # {6}
    for n in THRONE_COLOURS: # {6}
        h = len(art.ALL["king_a" if n.startswith("king") else n]) # {6}
        if n in ("king_spit", "king_flash_spit"): # {6}
            k = nf + ("king_spit", "king_flash_spit").index(n) # {6}
            tc.append(f"TFG+{toffs[k]}+{h}-160") # {6}
        else: # {6}
            tc.append(f"{tsame['TC_' + n.upper()]}+{h}-160") # {6}
    for lab, lst in (("KG", kb), ("KC", kc), ("OG", ob), ("OC", oc), # {4}
                     ("TG", tg), ("TC", tc)): # {6}
#|                     ): {4-5}
#|    for lab, lst in (("KG", kb), ("KC", kc)): {1-3}
        for half, op in (("LO", "<"), ("HI", ">")):
            b7.append(f"{lab}_{half}")
            for x in lst:
                b7.append(f"        .byte {op}({x})")
    b7.append("")
    # energy bar: units 1-8 in PF2 from bit 7 down (near the {3}
    # middle), 9-16 in PF1 from bit 0 up {3}
    p2 = [(0xFF << (8 - min(n, 8))) & 0xFF for n in range(17)] # {3}
    p1 = [(1 << max(0, n - 8)) - 1 for n in range(17)] # {3}
    b7 += data_lines("BAR_PF2", p2, "energy bar, 0-16 units", # {3}
                     per=9) # {3}
    b7 += data_lines("BAR_PF1", p1, per=9) # {3}
    open(os.path.join(GEN, "bank7.asm"), "w").write(
        "\n".join(b7) + "\n")

    # --- bank 1: the title {8}
    b1 = ["; generated by build_assets.py - bank 1", ""] # {8}
    blocks = {} # {8}
    modes = [(m, look.MODE_TOP, lab) for m, lab in # {8}
             zip(look.MODES, ("MMU", "MSF", "MSI"))] # {8}
    for name, top, lab in [(n, t, n[:3].upper()) for n, t in # {8}
                           look.TITLE_BLOCKS] + modes: # {8}
        rows = look.title_block_lines(name) # {8}
        blocks[name] = rows # {8}
        for col in range(6): # {8}
            vals = [int(row[8 * col:8 * col + 8].replace( # {8}
                "#", "1").replace(".", "0"), 2) # {8}
                for row in reversed(rows)] # {8}
            b1 += data_lines(f"{lab}{col}", vals, page=True) # {8}
        b1.append(f"{lab}_H = {len(rows)}") # {8}
        b1.append(f"{lab}_TOP = {top}") # {8}
        cols = look.title_block_colours(name) # {8}
        b1 += tv_block(lambda tv: data_lines( # {8}
            f"{lab}_COL", [look.tv_colour(c, tv) # {8}
                           for c in reversed(cols)], page=True)) # {8}
    dec = look.title_decor() # {8}
    b1 += tv_block(lambda tv: data_lines( # {8}
        "T_BG", [look.tv_colour(d[0], tv) for d in dec], # {8}
        "title, from the top: background, playfield colour", # {8}
        page=True) + data_lines( # {8}
        "T_PFC", [look.tv_colour(d[1], tv) for d in dec], # {8}
        page=True)) # {8}
    b1.append(f"SCN_H = {look.SCENE_H}") # {8}
    b1.append(f"SCN_SETUP = {look.TITLE_SETUP}") # {8}
    b1.append(f"SCN_KX = {look.SCENE_KNIGHT['x']}") # {8}
    b1.append(f"SCN_OX = {look.SCENE_KING['x']}") # {8}
    b1 += tv_block(lambda tv: sum( # {8}
        (data_lines(lab, vals, page=True) for lab, vals in zip( # {8}
            ("SCN_K", "SCN_KC", "SCN_O", "SCN_OC"), # {8}
            look.scene_tables(tv))), [])) # {8}
    pfs = [half_to_pf(d[2]) for d in dec] # {8}
    for r in range(3): # {8}
        b1 += data_lines(f"T_PF{r}", [p[r] for p in pfs], # {8}
                         page=True) # {8}
    open(os.path.join(GEN, "bank1.asm"), "w").write( # {8}
        "\n".join(b1) + "\n") # {8}

    # --- bank 6: the end screens {8}
    b6 = ["; generated by build_assets.py - bank 6: the end", # {8}
          "; screens", ""] # {8}
    end_blocks = {} # {8}
    labels = {"emblem": "E", "emblem_broken": "E", "GAME": "G", # {8}
              "OVER": "O", "VICTORY": "W"} # {8}
    for kind, pre in zip(look.END_KINDS, ("GO", "VI")): # {8}
        for name, top in look.END_BLOCKS[kind]: # {8}
            if name == "score": # {8}
                continue # {8}
            lab = pre + labels[name] # {8}
            rows = look.end_block_lines(name) # {8}
            end_blocks[f"{kind} {name}"] = rows # {8}
            for col in range(6): # {8}
                vals = [int(row[8 * col:8 * col + 8].replace( # {8}
                    "#", "1").replace(".", "0"), 2) # {8}
                    for row in reversed(rows)] # {8}
                b6 += data_lines(f"{lab}{col}", vals, page=True) # {8}
            b6.append(f"{lab}_H = {len(rows)}") # {8}
            b6.append(f"{lab}_TOP = {top}") # {8}
            cols = look.end_block_colours(name) # {8}
            b6 += tv_block(lambda tv, lab=lab, cols=cols: data_lines( # {8}
                f"{lab}_COL", [look.tv_colour(c, tv) # {8}
                               for c in reversed(cols)], page=True)) # {8}
        # (the decor's tables may cross a page: in DECOR a {8}
        # load that takes a cycle more still writes in time) {8}
        dec = look.end_decor(kind) # {8}
        b6 += tv_block(lambda tv, dec=dec, pre=pre: data_lines( # {8}
            f"{pre}_BG", [look.tv_colour(d[0], tv) for d in dec], # {8}
            f"{kind}, from the top: background, playfield colour") # {8}
            + data_lines( # {8}
            f"{pre}_PFC", [look.tv_colour(d[1], tv) for d in dec])) # {8}
        sc = look.END_SCENES[kind] # {8}
        p0, p1 = sc["p0"], sc["p1"] # {8}
        b6 += [f"{pre}_P0X = {p0['x'] if p0 else 0}", # {8}
               f"{pre}_P1X = {p1['x']}", # {8}
               f"{pre}_NUS1 = {p1['nus']}", # {8}
               f"{pre}_REF1 = {8 if p1['mirror'] else 0}"] # {8}
        b6 += tv_block(lambda tv, kind=kind, pre=pre: sum( # {8}
            (data_lines(lab, vals, page=True) for lab, vals in zip( # {8}
                (f"{pre}_SK", f"{pre}_SKC", f"{pre}_SO", # {8}
                 f"{pre}_SOC"), # {8}
                look.end_scene_tables(kind, tv))), [])) # {8}
    # the score: six columns of 9 bytes in the Superchip RAM {8}
    # (main.asm: end_score), read as the columns of a block {8}
    n = len(look.score_rows(0)) # {8}
    for col in range(6): # {8}
        b6.append(f"ESC{col} = SCR+{n * col}") # {8}
    b6.append(f"ESC_H = {n}") # {8}
    b6.append(f"ESC_TOP = {dict(look.END_BLOCKS['gameover'])['score']}") # {8}
    b6 += tv_block(lambda tv: data_lines( # {8}
        "ESC_COL", [look.tv_colour(c, tv) for c in reversed( # {8}
            look.end_block_colours("score"))], page=True)) # {8}
    # the shapes of the decor: the title's (the colours differ) {8}
    pfs = [half_to_pf(d[2]) for d in look.end_decor("gameover")] # {8}
    if pfs != [half_to_pf(d[2]) for d in look.end_decor("victory")]: # {8}
        raise SystemExit("the end screens: the same decor shapes") # {8}
    for r in range(3): # {8}
        b6 += data_lines(f"E_PF{r}", [p[r] for p in pfs]) # {8}
    open(os.path.join(GEN, "bank6.asm"), "w").write( # {8}
        "\n".join(b6) + "\n") # {8}

    # --- bank 5: the music and the effects (music.py) {7}
    b5, sound = music.build() # {7}
    open(os.path.join(GEN, "bank5.asm"), "w").write( # {7}
        "\n".join(b5) + "\n") # {7}

    info.update(knight_frames=KNIGHT_FRAMES, schemes=SCHEMES,
                room_schemes=[scheme(r) for r in range(NROOMS)],
                knight_bytes=kfig.size,
                tv={tv: rules.table(tv) for tv in ("ntsc", "pal")})
    info.update(collision=cmaps)  # {2}
    info.update(flicker={r: [list(f[0]), list(f[1])]  # {3}
                         for r, f in flick.items()},  # {3}
                versions={k: {r: v for r, v in d.items()}  # {3}
                          for k, d in vl.items()})  # {3}
    info.update(obj_frames=OBJ_FRAMES, figures_bytes=figures.size,  # {4}
                collision_closed=closed,  # {4}
                p1_uses={n: sorted(t) for n, t in uses.items()})  # {4}
    info.update(seams=seams)  # {5}
    info.update(throne_bytes=throne_block.size,  # {6}
                throne_frames=THRONE_FRAMES,  # {6}
                throne_colours=THRONE_COLOURS)  # {6}
    info.update(sound=sound)  # {7}
    info.update(title_blocks={n: blocks[n] for n in blocks},  # {8}
                end_blocks=end_blocks)  # {8}
    json.dump(info, open(os.path.join(GEN, "game.json"), "w"),
              indent=0)
    files = ["kfig0.asm", "bank0.asm", "bank3.asm", "bank7.asm"]
    files += ["bank4.asm"]  # {4}
    files += ["kfig2.asm", "bank2.asm"]  # {6}
    files += ["bank5.asm"]  # {7}
    files += ["bank1.asm", "bank6.asm"]  # {8}
    long = [f"{f}:{i}" for f in files
            for i, ln in enumerate(open(os.path.join(GEN, f)), 1)
            if len(ln.rstrip("\n")) > 60]
    print("assets:", " ".join(files),
          f"(lines over 60: {len(long)})")
    return long


if __name__ == "__main__":
    bad = art.check() + dungeon.check() + rules.check()
    bad += music.check()  # {7}
    if bad:
        sys.exit("\n".join(bad))
    build()
