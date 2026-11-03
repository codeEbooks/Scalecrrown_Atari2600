"""build_assets.py - the data of Scalecrown.

    python3 game/assets/build_assets.py

From art.py (figures, digits, letters, emblem), dungeon.py and
rooms.py (the 16 rooms and their things), look.py (light,
colours) and rules.py (speeds, times) it writes, in generated/:

  kfig0.asm   Sir Roderick's figures in one block, with zeros
              between them where the kernel may read them (only
              as many as the top lines he is drawn at need),
              and his colours (those of the thrust padded as
              well: they switch the blade)
  kfig2.asm   the same bytes, for bank 2
  bank0.asm   the figures of player 1 in one block, as his,
              and their colours;
              the colour tables of the rooms: one for each
              level (COLUBK and COLUPF interleaved) and the
              floors with the flames of the torches
  bank2.asm   the throne room: the figures of the King and of
              the crown, their colours, the colours of the room
  bank3.asm   the playfield of the 16 rooms (PF0, PF1, PF2 of
              the 20 courses), copied into the Superchip RAM
              when Sir Roderick comes in: the grate closed and
              the plates down; the bytes of the open grate
  bank4.asm   the things: the versions of the rows (the plates
              down and up, the grate open), where he touches a
              chest, a door, a plate; the times of the spikes;
              the points;
              the guards;
              the Serpent King
  bank5.asm   the music and the effects (music.py: score.py,
              sfx.py)
  bank7.asm   the numbers of each television (rules.py); for
              each room the colour tables, the collision maps
              (with the door open and closed), player 1 (the
              chest or the gate);
              the guards, the seam;
              the plug (the ball), the torch flicker; the name
              of each level for the HUD;
              the pointer bases of the figures;
              the HUD (digits, colours, energy bar)
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
import music                                          # noqa: E402

GEN = os.path.join(HERE, "generated")
LINES = 160
NROOMS = len(dungeon.ROOMS)
KNIGHT_FRAMES = ["knight_stand", "knight_walk1", "knight_walk2",
                 "knight_thrust", "knight_parry"]
# P1 figures of the room kernel (bank 0): (art, colour level or
# None); two frames each
# (the Serpent King and the crown are in the bank of the
# throne room: bank 2, THRONE_FRAMES)
# (the empty figure first: p1_bands takes a figure of a
# guard, never 0, as "always")
OBJ_FRAMES = [("none", None), ("none", None)]
for lv in (1, 2, 3, 4):
    OBJ_FRAMES += [("serpent_a", lv), ("serpent_b", lv)]
for n in ("chest", "chest_open", "gate"):
    OBJ_FRAMES += [(n, None), (n, None)]
# the figures of the throne room (bank 2): the King's two
# frames, the crown and its pieces
THRONE_FRAMES = ["king_a", "king_b", "crown", "crown_broken"]
# the colours of player 1 there: the King plain, spitting,
# flashing, both; the crown, its pieces
THRONE_COLOURS = ["king", "king_spit", "king_flash",
                  "king_flash_spit", "crown", "crown_broken"]
# the colour schemes of the rooms: (level, torches); the rooms
# of a level share one, the rooms with torches the flames too
# (the throne room has its own, in bank 2)
SCHEMES = [(1, False), (2, False), (2, True), (3, False),
           (4, False), (4, True), "throne"]
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


def map_bytes(walls):
    """A collision map: three bytes a row of blocks, the whole
    width (the plug makes a room lopsided): blocks 0-7 in
    bits 7-0 of the first byte, 8-15 of the second, 16-19 in
    bits 7-4 of the third."""
    vals = []
    for row in walls:
        for k in range(3):
            vals.append(sum(0x80 >> i for i in range(8)
                            if 8 * k + i < 20 and row[8 * k + i]))
    return vals


def scheme(r):
    if dungeon.throne(r):
        return SCHEMES.index("throne")
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


KIND_OF = {"serpent_a": "serpent", "serpent_b": "serpent",
           "king_a": "king", "king_b": "king"}
FRAMES_OF = {"serpent": ("serpent_a", "serpent_b"),
             "king": ("king_a", "king_b")}


def ob_col(name, level):
    return f"OB_COL_{name}_{level or 0}".upper()


def p1_uses():
    """For each figure of player 1, its uses: (top line, first
    line read, last line read), from what player 1 can show in
    each band of each room (dungeon.p1_shows, windows)."""
    uses = {}
    for r in range(NROOMS):
        wa, wb = dungeon.windows(r)
        for band, kind, top in dungeon.p1_shows(r):
            lo, hi = wa if band == "A" else wb
            for n in FRAMES_OF.get(kind, (kind,)):
                uses.setdefault(n, set()).add((top, lo, hi))
    return uses


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


# --- the versions of the rows -----------------------------

def door_bits(r):
    """The bit of the door of room r in `opened` (0: none)."""
    if not dungeon.door(r):
        return 0
    return dungeon.door_bit(dungeon.ROOMS[r]["level"])


def sc_bytes(st):
    """The 60 bytes of the Superchip for a room drawn as st."""
    pf = [half_to_pf(st[c][:20]) for c in range(20)]
    return [pf[19 - i][k] for k in range(3) for i in range(20)]


def version_lists():
    """For each room, the bytes of the Superchip that change
    with the state of its things, as (index, value): the open
    grate ("door"), the plates down and up. The playfield of
    bank 3 is the room with the grate closed and the plates
    down; the logic writes the other versions."""
    vl = dict(door={}, down={}, up={})
    for r, rm in enumerate(dungeon.ROOMS):
        base = sc_bytes(look.stone(rm, 0, closed=True))
        if rooms.grate(rm):
            op = sc_bytes(look.stone(rm, 0, closed=False))
            vl["door"][r] = [(i, v) for i, v in enumerate(op)
                             if v != base[i]]
        if rm.get("plate") is not None:
            up = sc_bytes(look.stone(rm, 0, closed=True,
                                     raised=True))
            idx = [i for i, v in enumerate(up) if v != base[i]]
            vl["up"][r] = [(i, up[i]) for i in idx]
            vl["down"][r] = [(i, base[i]) for i in idx]
    for kind, lists in vl.items():
        for r, ent in lists.items():
            if len(ent) != 2:
                raise SystemExit(f"room {r}: {kind} changes "
                                 f"{len(ent)} bytes, not 2")
    return vl


def list_tables(suffix, named):
    """Lists of (index, value) in two tables, VI and VV, each
    list ended by the index $FF; entry 0 is the empty list.
    For each name, the start of the list of every room."""
    vi, vv, out = [0xFF], [0], []
    starts = {}
    for name, lists in named.items():
        st = []
        for r in range(NROOMS):
            ent = lists.get(r, [])
            st.append(len(vi) if ent else 0)
            for i, v in ent:
                vi.append(i)
                vv.append(v)
            if ent:
                vi.append(0xFF)
                vv.append(0)
        starts[name] = st
    if len(vi) > 256:
        raise SystemExit("version lists over 256 entries")
    out += data_lines(f"VI{suffix}", vi, "Superchip index, "
                      "$FF: end of a list", per=10)
    out += data_lines(f"VV{suffix}", vv, "its value", per=10)
    for name, st in starts.items():
        out += data_lines(f"{name}{suffix}", st, per=8)
    return out


def bank4(vl):
    """The tables of things.asm."""
    out = ["; the plates of the spikes, down (SPD) and up (SPU),",
           "; and the open door (DOP): lists of the bytes of the",
           "; Superchip of each version"]
    out += list_tables("4", {"SPD": vl["down"], "SPU": vl["up"],
                             "DOP": vl["door"]})
    zones = [dungeon.zone(r) for r in range(NROOMS)]
    out += ["", "; the thing of each room: its bit in `opened` (0:",
            "; none; a chest below $10, a door from $10), where",
            "; he touches it: columns TX0 to TX1-1, top lines TY0",
            "; to TY1-1"]
    out += data_lines("TBIT", [dungeon.thing_bit(r)
                               for r in range(NROOMS)], per=8)
    for lab, i, j in (("TX0", 0, 0), ("TX1", 0, 1), ("TY0", 1, 0),
                      ("TY1", 1, 1)):
        out += data_lines(lab, [
            (z[i][j] + j if z else 255) for z in zones], per=8)
    pz = [dungeon.plate_zones(r) for r in range(NROOMS)]
    ys = {p[1] for p in pz if p}
    if len(ys) != 1:
        raise SystemExit("the plates in the same lines")
    y0, y1 = ys.pop()
    out += ["", "; the plates: the columns where the middle of his",
            "; feet is over the first (PXA0 to PXA1-1) or the",
            "; second (PXB0 to PXB1-1); his top line from",
            "; PLATE_Y0 to PLATE_Y1-1; 255: no plates",
            f"PLATE_Y0 = {y0}", f"PLATE_Y1 = {y1 + 1}"]
    for lab, i, j in (("PXA0", 0, 0), ("PXA1", 0, 1),
                      ("PXB0", 1, 0), ("PXB1", 1, 1)):
        out += data_lines(lab, [(p[0][i][j] + j if p else 255)
                                for p in pz], per=8)
    out += ["", "; times (rules.py): frames down by level, frames",
            "; up, frames before a plate hurts again"]
    out += tv_block(lambda tv: data_lines(
        "TH_DOWN", rules.spike_frames(tv)[0]) + [
        f"SPK_UP = {rules.spike_frames(tv)[1]}",
        f"HURT_FRAMES = {rules.spike_frames(tv)[2]}"])
    out += ["; points, added to the middle byte of the score",
            f"CHEST_BCD = ${rules.bcd_hundreds(rules.CHEST_POINTS):02X}",
            f"DOOR_BCD = ${rules.bcd_hundreds(rules.DOOR_POINTS):02X}",
            f"SERPENT_BCD = "
            f"${rules.bcd_hundreds(rules.SERPENT_POINTS):02X}",
            f"SPIKE_DAMAGE = {rules.SPIKE_DAMAGE}",
            f"BITE_DAMAGE = {rules.BITE_DAMAGE}"]
    # the guards. Entry r the first guard of room r, 16 + r
    # the second: top line (0: none), the columns of its path;
    # and the speed of each room (rules.crawl: a fraction a
    # frame; in the King's room his own)
    guards = [dungeon.ROOMS[r]["guards"] for r in range(NROOMS)]
    slot = [g[k] if len(g) > k else None
            for k in (0, 1) for g in guards]
    out += ["", "; the guards: entry r the first of room r,",
            "; 16 + r the second; top line (0: none), path from",
            "; S_MIN to S_MAX (all serpents)"]
    out += data_lines("S_TOP4", [g["top"] if g else 0 for g in slot],
                      per=8)
    out += data_lines("S_MIN4", [g["path"][0] if g else 0
                                 for g in slot], per=8)
    out += data_lines("S_MAX4", [g["path"][1] if g else 0
                                 for g in slot], per=8)
    out += ["; the speed of the guards of each room: a fraction of",
            "; a pixel a frame"]
    out += tv_block(lambda tv: data_lines("CRAWL", [
        rules.crawl(None if g and g[0]["kind"] == "king"
                    else dungeon.ROOMS[r]["level"], tv)
        for r, g in enumerate(guards)], per=8))
    out += throne4()
    return out


def ranges(test):
    """The columns 0-X_MAX of Sir Roderick where test(kx) holds:
    one run (first, count), for a compare in the cartridge."""
    xs = [x for x in range(rules.X_MAX + 1) if test(x)]
    if not xs or xs != list(range(xs[0], xs[-1] + 1)):
        raise SystemExit("not one run of columns")
    return xs[0], len(xs)


def blade_pixels(kx, kdir):
    """The blade's (first pixel, width), as knight.asm puts it
    (the model has the same rule)."""
    if kdir == 0:
        x0 = kx + rules.FIRST_PIXEL + rules.KNIGHT_W
        for w in (8, 4, 2, 1):
            if x0 + w <= 160:
                return x0, w
        return None
    end = kx + rules.FIRST_PIXEL - 1
    for w in (8, 4, 2, 1):
        if end - w + 1 >= 0:
            return end - w + 1, w
    return None


def meets(a0, a1, b0, b1):
    return a0 <= b1 and b0 <= a1


def throne4():
    """The tables and numbers of the Serpent King."""
    th = dungeon.THRONE
    t0, t1 = th["top"]
    ka, kb = dungeon.king_pixels()
    ca, cb, c0, c1 = dungeon.crown_box()
    kw = rules.FIRST_PIXEL
    out = ["", "; the throne room (its room, the King's column and",
           "; top lines, the crown: bank7.asm): the King's height,",
           "; his mouth, where the venom starts, the free pixels of",
           "; the venom for each top line of the King",
           "; ((top - KING_T0) / 2: from VSPAN_LO to VSPAN_HI)",
           f"KING_H = {dungeon.height('king')}",
           f"MOUTH = {th['mouth']}",
           f"VEN_LEFT = {dungeon.venom_start(False)}",
           f"VEN_RIGHT = {dungeon.venom_start(True)}"]
    spans = [dungeon.venom_span(t) for t in range(t0, t1 + 1, 2)]
    out += data_lines("VSPAN_LO", [a for a, _ in spans], per=8)
    out += data_lines("VSPAN_HI", [b for _, b in spans], per=8)
    # where his blade meets the King (pixels ka-kb) or the crown,
    # facing right and left: a run of columns; his box meets
    # the King's at a run of columns too
    for lab, (a, b) in (("KB", (ka, kb)), ("CB", (ca, cb))):
        for d, kd in (("R", 0), ("L", 8)):
            x0, n = ranges(lambda x: blade_pixels(x, kd) and meets(
                blade_pixels(x, kd)[0],
                blade_pixels(x, kd)[0] + blade_pixels(x, kd)[1] - 1,
                a, b))
            out += [f"{lab}_{d}0 = {x0}", f"{lab}_{d}N = {n}"]
    x0, n = ranges(lambda x: meets(x + kw, x + kw + rules.KNIGHT_W - 1,
                                   ka, kb))
    out += [f"KBITE_X0 = {x0}", f"KBITE_N = {n}",
            f"CROWN_H = {c1 - c0 + 1}",
            f"VENOM_DAMAGE = {rules.VENOM_DAMAGE}",
            f"KHIT_BCD = ${rules.bcd_hundreds(rules.KING_HIT_POINTS):02X}",
            f"KING_BCD = ${rules.bcd_hundreds(rules.KING_POINTS):02X}",
            f"ENERGY_BCD = ${rules.bcd_hundreds(rules.ENERGY_POINTS):02X}",
            f"KING_HITS = {rules.KING_HITS}",
            "; the time between two spits by the blows he has had",
            "; (the other times of each television: bank7.asm)"]
    out += tv_block(lambda tv: data_lines(
        "SPIT", rules.spit_frames(tv), per=8))
    return out


def build():
    os.makedirs(GEN, exist_ok=True)
    info = dict(rooms=NROOMS, lines=LINES)

    # --- Sir Roderick: his figures, the colours of the thrust
    # (padded: they switch the blade) and his other colours,
    # the same bytes at the start of bank 0 and of bank 2
    # (kfig0.asm, kfig2.asm): the pointers that prep_room
    # makes work in both kernels
    thrust = KNIGHT_FRAMES.index(art.BLADE_POSE)
    kt = [(t, 0, LINES - 1) for t in (rules.TOP_MIN, rules.TOP_MAX)]
    kcols = {f"KN_COL{i}": colour_rows(n) for i, n in
             enumerate(KNIGHT_FRAMES) if i != thrust}
    kcols["KN_FLASH"] = {tv: [look.tv_colour(rules.FLASH_COLOUR, tv)]
                         * rules.KNIGHT_H for tv in ("ntsc", "pal")}
    ksame = shared(kcols)

    def kfig(suffix):
        out = [f"; generated by build_assets.py - Sir Roderick for "
               f"bank {suffix or 0}", "",
               "; his figures and the colours of the thrust (they",
               "; also switch the blade)"]

        def block(tv):
            items = [(n, gfx(n), kt) for n in KNIGHT_FRAMES]
            items.append(("the colours of the thrust",
                          colour_rows(art.BLADE_POSE)[tv], kt))
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
    for suffix, name in (("", "kfig0.asm"), ("_2", "kfig2.asm")):
        open(os.path.join(GEN, name), "w").write(
            "\n".join(kfig(suffix)) + "\n")
    koff = kfig.off[:len(KNIGHT_FRAMES)]
    toff = kfig.off[len(KNIGHT_FRAMES)]

    # --- bank 0: player 1 and the colours of the room kernel
    b0 = ["; generated by build_assets.py - bank 0", ""]
    uniq = list(dict.fromkeys(n for n, _ in OBJ_FRAMES))
    uses = p1_uses()

    def figures(tv):
        items = [(n, gfx(n), sorted(uses[n])) for n in uniq]
        lines, off, size = figure_block(items, "FG")
        figures.off, figures.size = off, size
        return lines
    b0 += ["; the figures of player 1"]
    b0 += tv_block(figures)
    ooff = figures.off
    # the colours of the figures of player 1: a table that is
    # the same as one before it is not written again
    ocols = {ob_col(n, lv): colour_rows(n, lv)
             for n, lv in dict.fromkeys(OBJ_FRAMES)}
    same = shared(ocols)
    b0 += ["", "; colours of the figures of player 1, bottom first"]
    b0 += tv_block(lambda tv: sum(
        (data_lines(lab, v[tv]) for lab, v in ocols.items()
         if same[lab] == lab), []))
    b0.append("")

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

    # --- bank 3: the playfield of the rooms
    b3 = ["; generated by build_assets.py - bank 3", "",
          "; the rooms for the Superchip RAM: PF0 of the 20",
          "; courses, then PF1, then PF2; course c at index 19-c"]
    flick = {}
    for r, rm in enumerate(dungeon.ROOMS):
        st = look.stone(rm, 0, closed=True)
        pf = [half_to_pf(st[c][:20]) for c in range(20)]
        sc = []
        for k in range(3):
            sc += [pf[19 - i][k] for i in range(20)]
        b3 += data_lines(f"RS_{r}", sc, f"{r} {rm['name']}", per=10)
        if rooms.torches(rm):
            st1 = look.stone(rm, 1)
            flick[r] = [half_to_pf(st1[0][:20]), pf[0]]
    b3 += [""] + expr_table("RS_LO", [f"RS_{r}" for r in
                                      range(NROOMS)], "<")
    b3 += expr_table("RS_HI", [f"RS_{r}" for r in range(NROOMS)],
                     ">")
    vl = version_lists()
    b3 += ["", "; the door open: the bytes of the open version,",
           "; written after the copy if the door of the room",
           "; is open"]
    b3 += list_tables("3", {"DOP": vl["door"]})
    b3 += data_lines("RDOOR3", [door_bits(r) for r in
                                range(NROOMS)], per=8)
    open(os.path.join(GEN, "bank3.asm"), "w").write(
        "\n".join(b3) + "\n")

    # --- bank 4: the things of the rooms
    b4 = ["; generated by build_assets.py - bank 4", ""]
    b4 += bank4(vl)
    open(os.path.join(GEN, "bank4.asm"), "w").write(
        "\n".join(b4) + "\n")

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
    b7 += data_lines("WALK", list(rules.WALK),
                     "poses of the walk, a pose every STRIDE")
    # player 1 in each room: the thing (chest, gate) of
    # band A, its figure (OG) closed and open (the bit OB_BIT
    # of `opened` chooses), top line and column (the empty
    # figure where there is no thing); NUSIZ1;
    # the guards: their figures (the serpents of the level),
    # and in tables of 32 entries (entry r: the first guard,
    # 16 + r: the second) top line (0: none), start column,
    # path; the seam (0: none, else its course + 1: the count
    # the kernel takes down to 0 in line B1)
    first = {}
    for i, (n, lv) in enumerate(OBJ_FRAMES):
        first.setdefault((KIND_OF.get(n, n), lv), i)
    lvs = [rm["level"] for rm in dungeon.ROOMS]

    def kind(k, lv):
        if k == "king":         # drawn in bank 2
            k = "none"
        return first[(k, lv if k == "serpent" else None)]
    bits = [dungeon.thing_bit(r) for r in range(NROOMS)]
    things = [dungeon.thing_item(r) for r in range(NROOMS)]
    guards = [dungeon.ROOMS[r]["guards"] for r in range(NROOMS)]
    b7 += ["; player 1: the thing of band A closed and open, the",
           "; bit that opens it, its top line and column; NUSIZ1"]
    b7 += data_lines("OB_KIND0", [
        kind(t["kind"] if t else "none", lv)
        for t, lv in zip(things, lvs)], per=8)
    b7 += data_lines("OB_KIND1", [
        kind(dungeon.open_kind(t["kind"]) if t else "none", lv)
        for t, lv in zip(things, lvs)], per=8)
    b7 += data_lines("OB_BIT", bits, per=8)
    b7 += data_lines("OB_TOP", [t["top"] if t else dungeon.NONE_TOP
                                for t in things], per=8)
    b7 += data_lines("OB_X", [t["x"] if t else 1 for t in things],
                     per=8)
    b7 += data_lines("OB_NUS", [
        5 if g and g[0]["kind"] == "king" else 0 for g in guards],
        per=8)
    b7 += ["; the guards: their figure; top line (0: none), start",
           "; column (entry r the first, 16 + r the second)"]
    b7 += data_lines("S_KIND", [
        kind(g[0]["kind"], lv) if g else kind("none", lv)
        for g, lv in zip(guards, lvs)], per=8)
    slot = [[g[k] if len(g) > k else None for g in guards]
            for k in (0, 1)]
    b7 += data_lines("S_TOP", [g["top"] if g else 0
                               for g in slot[0] + slot[1]], per=8)
    b7 += data_lines("S_X", [g["x"] if g else dungeon.ABSENT_X
                             for g in slot[0] + slot[1]], per=8)

    def place(x):               # the count and HMP1 of place
        q, m = divmod(x, 15)
        return q + 1, (((m - 15) & 0xFF) ^ 7) << 4 & 0xFF
    b7 += ["; the first guard at its start: the count of the delay",
           "; of the seam and its fine move (as place does it for",
           "; the column - 3: RESP1 there writes a cycle later)"]
    x0 = [g["x"] if g else dungeon.ABSENT_X for g in slot[0]]
    b7 += data_lines("S_CO", [place(x - 3)[0] for x in x0], per=8)
    b7 += data_lines("S_HM", [place(x - 3)[1] for x in x0], per=8)
    seams = [dungeon.seam(r) for r in range(NROOMS)]
    b7 += ["; the seam: 0 none, else its course + 1"]
    b7 += data_lines("SEAM", [0 if c is None else c + 1
                              for c in seams], per=8)
    if any(seams[r] is not None and
           kind(guards[r][0]["kind"], lvs[r]) == 0
           for r in range(NROOMS)):
        raise SystemExit("a guard below a seam has figure 0")
    blade = [c for _, c in art.ALL[art.BLADE_POSE]].index(
        art.BLADE_COLOUR)
    b7 += [f"NONE_KIND = {kind('none', None)}",
           f"FLASH_FRAMES = {rules.FLASH_FRAMES}",
           f"BLADE_LINE = {blade}",
           f"SERPENT_H = {dungeon.SERPENT_H}", ""]
    # the throne room (dungeon.THRONE): its room;
    # the King's column and top lines, the crown; NUSIZ1 for
    # them (the King twice as wide, the crown four times;
    # missile 1, the venom, 8 pixels); the venom flies left
    # when Sir Roderick's column is below SPIT_LEFT (his
    # middle left of the King's); the entry of the parry;
    # the entry of the colours of the flash
    th = dungeon.THRONE
    if th["mouth"] != art.KING_MOUTH:
        raise SystemExit("the King's mouth: dungeon and art")
    b7 += [f"THRONE_ROOM = {th['room']}"]
    b7 += ["; the throne room",
           f"KING_X = {th['x']}",
           f"KING_T0 = {th['top'][0]}", f"KING_T1 = {th['top'][1]}",
           f"KING_START = {th['start']}",
           f"CROWN_X = {th['crown']['x']}",
           f"CROWN_TOP = {th['crown']['top']}",
           "NUS_KING = $35", "NUS_CROWN = $37",
           f"SPIT_LEFT = {dungeon.spit_left()}",
           f"PARRY_POSE = {rules.PARRY_POSE}"]
    b7 += [f"FLASH_KC = {len(KNIGHT_FRAMES)}", ""]
    # the plug: ENABL for the room (2: the ball is on) and the
    # column that puts the ball's first pixel on 0 or 152 (a
    # ball, like a missile, starts at column + 2)
    plugs = [dungeon.plug(r) for r in range(NROOMS)]
    b7 += ["; the plug of each room: ENABL, the column of the ball"]
    b7 += data_lines("PLUG", [2 if p else 0 for p in plugs], per=8)
    b7 += data_lines("BALL_X", [{None: 0, "west": 158,
                                 "east": 150}[p] for p in plugs],
                     per=8)
    # colours: the scheme of each room, and for each scheme
    # cbk for the two frames of the water and cpf
    b7 += ["; colours: the scheme of each room; for a scheme the",
           "; COLUBK table of the two frames of the water and",
           "; the COLUPF table (a byte before its level's table)"]
    b7 += data_lines("SCHEME", [scheme(r) for r in range(NROOMS)],
                     per=8)
    cb0, cb1, cp = [], [], []
    for sch in SCHEMES:
        if sch == "throne":
            cb0.append("TRC")
            cb1.append("TRC")
            cp.append("TRC-1")
            continue
        lv, torch = sch
        shim = rooms.LEVELS[lv]["shimmer"]
        if torch:
            k = TORCH_LEVELS.index(lv)
            cb0.append(f"RC_FLAME+{k}")
            cb1.append(f"RC_FLAME+{k}")
        else:
            cb0.append(f"RC_{lv}_0")
            cb1.append(f"RC_{lv}_{1 if shim else 0}")
        cp.append(f"RC_{lv}_0-1")
    for lab, lst in (("CB0", cb0), ("CB1", cb1), ("CP", cp)):
        b7 += expr_table(f"{lab}_LO", lst, "<")
        b7 += expr_table(f"{lab}_HI", lst, ">")
    # HUD colours
    b7 += tv_block(lambda tv: [
        f"SCORE_COL = ${look.tv_colour(look.HUD_SCORE_COLOUR, tv):02X}",
        f"TEXT_COL = ${look.tv_colour(look.HUD_TEXT_COLOUR, tv):02X}"]
        + data_lines("BAR_COL", [look.tv_colour(c, tv) for c in
                                 reversed(look.HUD_BAR_COLOURS)],
                     "energy bar colours, bottom first"))
    # digits, bottom first
    dig = []
    for g in art.DIGITS:
        dig += [int((r + "..").replace("#", "1").replace(".", "0"),
                    2) for r in reversed(g)]
    b7 += data_lines("DIGITS", dig, "digits 0-9, 8 lines each, "
                     "bottom first", per=8, page=True)
    # collision maps: three bytes a row of blocks, the whole
    # width (the plug makes a room lopsided): blocks 0-7 in
    # bits 7-0 of the first byte, 8-15 of the second, 16-19
    # in bits 7-4 of the third
    b7 += ["; collision maps: 10 rows of 3 bytes, block 0 in bit",
           "; 7 of the first byte, block 8 in bit 7 of the second,",
           "; block 16 in bit 7 of the third"]
    cmaps = {}
    for r in range(NROOMS):
        vals = map_bytes(dungeon.walls(r))
        cmaps[r] = vals
        b7 += data_lines(f"CM_{r}", vals, per=9)
    b7 += expr_table("CM_LO", [f"CM_{r}" for r in range(NROOMS)],
                     "<")
    b7 += expr_table("CM_HI", [f"CM_{r}" for r in range(NROOMS)],
                     ">")
    # the maps with the door closed: stone in the gap of the
    # grate, or over the opening of the gate; a room without
    # a door has its only map
    b7 += ["; collision maps with the door closed; the door's",
           "; bit in `opened` (0: no door)"]
    closed = {}
    for r in range(NROOMS):
        if dungeon.door(r):
            vals = map_bytes(dungeon.walls(r, closed=True))
            closed[r] = vals
            b7 += data_lines(f"CMC_{r}", vals, per=9)
    cmc = [f"CMC_{r}" if r in closed else f"CM_{r}"
           for r in range(NROOMS)]
    b7 += expr_table("CMC_LO", cmc, "<")
    b7 += expr_table("CMC_HI", cmc, ">")
    b7 += data_lines("RDOOR", [door_bits(r) for r in
                               range(NROOMS)], per=8)
    b7 += ["; the spikes start down, for the time of the level"]
    b7 += tv_block(lambda tv: data_lines(
        "SU_DOWN", rules.spike_frames(tv)[0]))
    b7.append("")
    b7 += ["; the torches: course 0 in the two frames of the",
           "; flicker (PF0-2 odd, even); 0 for a room without"]
    for r, f in flick.items():
        b7 += data_lines(f"RF_{r}", list(f[0]) + list(f[1]))
    b7 += expr_table("RF_LO", [f"RF_{r}" if r in flick else "0"
                               for r in range(NROOMS)], "<")
    b7 += expr_table("RF_HI", [f"RF_{r}" if r in flick else "0"
                               for r in range(NROOMS)], ">")
    b7 += ["; the name of each level for the HUD: six columns of",
           "; 8 bytes, bottom first,",
           "; then the sixth column again with the key after",
           "; the name,",
           "; in one page (the HUD reads them through pointers,",
           "; at fixed cycles)"]

    def columns(rows):
        return [[int(r[8 * col:8 * col + 8].replace(
            "#", "1").replace(".", "0"), 2)
            for r in reversed(rows)] for col in range(6)]
    for lv in (1, 2, 3, 4):
        plain = columns(look.hud_text_rows(lv))
        keyed = columns(look.hud_text_rows(lv, key=True))
        if plain[:5] != keyed[:5]:
            raise SystemExit("the key must be in the sixth column")
        vals = sum(plain, []) + keyed[5]
        b7 += data_lines(f"TX_{lv}", vals, per=8, page=True)
    b7 += ["; GAME OVER in the place of the name: six",
           "; columns"]
    b7 += data_lines("TX_GO", sum(columns(look.game_over_rows()), []),
                     per=8, page=True)
    b7 += ["; VICTORY in the place of the name"]
    b7 += data_lines("TX_VIC", sum(columns(look.victory_rows()), []),
                     per=8, page=True)
    names = [f"TX_{lv}" for lv in (1, 2, 3, 4)] + ["TX_GO", "TX_VIC"]
    b7 += expr_table("TX_LO", names, "<")
    b7 += expr_table("TX_HI", names, ">")
    b7.append("")
    # pointer bases: address + h - 160 (pointer = base + top)
    b7 += ["; pointer bases of the figures: data + h - 160, so that",
           "; pointer = base + top line"]
    kb = [f"KFG+{koff[i]}+{len(art.ALL[n])}-160"
          for i, n in enumerate(KNIGHT_FRAMES)]
    kc = [f"{ksame[f'KN_COL{i}']}+{len(art.ALL[n])}-160"
          if i != thrust else
          f"KFG+{toff}+{len(art.ALL[n])}-160"
          for i, n in enumerate(KNIGHT_FRAMES)]
    kc.append(f"{ksame['KN_FLASH']}+{rules.KNIGHT_H}-160")  # flash
    ob = [f"FG+{ooff[uniq.index(n)]}+{len(art.ALL[n])}-160"
          for n, _ in OBJ_FRAMES]
    oc = [f"{same[ob_col(n, lv)]}+{len(art.ALL[n])}-160"
          for n, lv in OBJ_FRAMES]
    # the throne room (bank 2): figures and colours
    tg = [f"TFG+{toffs[i]}+{len(art.ALL[n])}-160"
          for i, n in enumerate(THRONE_FRAMES)]
    nf = len(THRONE_FRAMES)
    tc = []
    for n in THRONE_COLOURS:
        h = len(art.ALL["king_a" if n.startswith("king") else n])
        if n in ("king_spit", "king_flash_spit"):
            k = nf + ("king_spit", "king_flash_spit").index(n)
            tc.append(f"TFG+{toffs[k]}+{h}-160")
        else:
            tc.append(f"{tsame['TC_' + n.upper()]}+{h}-160")
    for lab, lst in (("KG", kb), ("KC", kc), ("OG", ob), ("OC", oc),
                     ("TG", tg), ("TC", tc)):
        for half, op in (("LO", "<"), ("HI", ">")):
            b7.append(f"{lab}_{half}")
            for x in lst:
                b7.append(f"        .byte {op}({x})")
    b7.append("")
    # energy bar: units 1-8 in PF2 from bit 7 down (near the
    # middle), 9-16 in PF1 from bit 0 up
    p2 = [(0xFF << (8 - min(n, 8))) & 0xFF for n in range(17)]
    p1 = [(1 << max(0, n - 8)) - 1 for n in range(17)]
    b7 += data_lines("BAR_PF2", p2, "energy bar, 0-16 units",
                     per=9)
    b7 += data_lines("BAR_PF1", p1, per=9)
    open(os.path.join(GEN, "bank7.asm"), "w").write(
        "\n".join(b7) + "\n")

    # --- bank 5: the music and the effects (music.py)
    b5, sound = music.build()
    open(os.path.join(GEN, "bank5.asm"), "w").write(
        "\n".join(b5) + "\n")

    info.update(knight_frames=KNIGHT_FRAMES, schemes=SCHEMES,
                room_schemes=[scheme(r) for r in range(NROOMS)],
                knight_bytes=kfig.size,
                tv={tv: rules.table(tv) for tv in ("ntsc", "pal")})
    info.update(collision=cmaps)
    info.update(flicker={r: [list(f[0]), list(f[1])]
                         for r, f in flick.items()},
                versions={k: {r: v for r, v in d.items()}
                          for k, d in vl.items()})
    info.update(obj_frames=OBJ_FRAMES, figures_bytes=figures.size,
                collision_closed=closed,
                p1_uses={n: sorted(t) for n, t in uses.items()})
    info.update(seams=seams)
    info.update(throne_bytes=throne_block.size,
                throne_frames=THRONE_FRAMES,
                throne_colours=THRONE_COLOURS)
    info.update(sound=sound)
    json.dump(info, open(os.path.join(GEN, "game.json"), "w"),
              indent=0)
    files = ["kfig0.asm", "bank0.asm", "bank3.asm", "bank7.asm"]
    files += ["bank4.asm"]
    files += ["kfig2.asm", "bank2.asm"]
    files += ["bank5.asm"]
    long = [f"{f}:{i}" for f in files
            for i, ln in enumerate(open(os.path.join(GEN, f)), 1)
            if len(ln.rstrip("\n")) > 60]
    print("assets:", " ".join(files),
          f"(lines over 60: {len(long)})")
    return long


if __name__ == "__main__":
    bad = art.check() + dungeon.check() + rules.check()
    bad += music.check()
    if bad:
        sys.exit("\n".join(bad))
    build()
