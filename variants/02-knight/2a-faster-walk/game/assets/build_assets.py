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
              the colour tables of the rooms: one for each
              level (COLUBK and COLUPF interleaved) and the
              floors with the flames of the torches
  bank3.asm   the playfield of the 16 rooms (PF0, PF1, PF2 of
              the 20 courses), copied into the Superchip RAM
              when Sir Roderick comes in: the grate closed and
  bank7.asm   the numbers of each television (rules.py); for
              each room the colour tables, the collision maps;
              the pointer bases of the figures;
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

GEN = os.path.join(HERE, "generated")
LINES = 160
NROOMS = len(dungeon.ROOMS)
KNIGHT_FRAMES = ["knight_stand", "knight_walk1", "knight_walk2",
                 "knight_thrust"]
# the colour schemes of the rooms: (level, torches); the rooms
# of a level share one, the rooms with torches the flames too
SCHEMES = [(1, False), (2, False), (2, True), (3, False),
           (4, False), (4, True)]
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











def build():
    os.makedirs(GEN, exist_ok=True)
    info = dict(rooms=NROOMS, lines=LINES)

    # --- Sir Roderick: his figures, the colours of the thrust
    # (padded: they switch the blade) and his other colours,
    thrust = KNIGHT_FRAMES.index(art.BLADE_POSE)
    kt = [(t, 0, LINES - 1) for t in (rules.TOP_MIN, rules.TOP_MAX)]
    kcols = {f"KN_COL{i}": colour_rows(n) for i, n in
             enumerate(KNIGHT_FRAMES) if i != thrust}
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
    for suffix, name in (("", "kfig0.asm"),):
        open(os.path.join(GEN, name), "w").write(
            "\n".join(kfig(suffix)) + "\n")
    koff = kfig.off[:len(KNIGHT_FRAMES)]
    toff = kfig.off[len(KNIGHT_FRAMES)]

    # --- bank 0: the colours of the room kernel
    b0 = ["; generated by build_assets.py - bank 0", ""]

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

    # --- bank 3: the playfield of the rooms
    b3 = ["; generated by build_assets.py - bank 3", "",
          "; the rooms for the Superchip RAM: PF0 of the 20",
          "; courses, then PF1, then PF2; course c at index 19-c"]
    for r, rm in enumerate(dungeon.ROOMS):
        st = look.stone(rm, 0, closed=True)
        pf = [half_to_pf(st[c][:20]) for c in range(20)]
        sc = []
        for k in range(3):
            sc += [pf[19 - i][k] for i in range(20)]
        b3 += data_lines(f"RS_{r}", sc, f"{r} {rm['name']}", per=10)
    b3 += [""] + expr_table("RS_LO", [f"RS_{r}" for r in
                                      range(NROOMS)], "<")
    b3 += expr_table("RS_HI", [f"RS_{r}" for r in range(NROOMS)],
                     ">")
    open(os.path.join(GEN, "bank3.asm"), "w").write(
        "\n".join(b3) + "\n")

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

    # colours: the scheme of each room, and for each scheme
    # cbk for the two frames of the water and cpf
    b7 += ["; colours: the scheme of each room; for a scheme the",
           "; COLUBK table of the two frames of the water and",
           "; the COLUPF table (a byte before its level's table)"]
    b7 += data_lines("SCHEME", [scheme(r) for r in range(NROOMS)],
                     per=8)
    cb0, cb1, cp = [], [], []
    for sch in SCHEMES:
        lv, torch = sch
        if torch:
            k = TORCH_LEVELS.index(lv)
            cb0.append(f"RC_FLAME+{k}")
        else:
            cb0.append(f"RC_{lv}_0")
        cp.append(f"RC_{lv}_0-1")
    for lab, lst in (("CB0", cb0), ("CP", cp)):
        b7 += expr_table(f"{lab}_LO", lst, "<")
        b7 += expr_table(f"{lab}_HI", lst, ">")
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

    # pointer bases: address + h - 160 (pointer = base + top)
    b7 += ["; pointer bases of the figures: data + h - 160, so that",
           "; pointer = base + top line"]
    kb = [f"KFG+{koff[i]}+{len(art.ALL[n])}-160"
          for i, n in enumerate(KNIGHT_FRAMES)]
    kc = [f"{ksame[f'KN_COL{i}']}+{len(art.ALL[n])}-160"
          if i != thrust else
          f"KFG+{toff}+{len(art.ALL[n])}-160"
          for i, n in enumerate(KNIGHT_FRAMES)]
    for lab, lst in (("KG", kb), ("KC", kc)):
        for half, op in (("LO", "<"), ("HI", ">")):
            b7.append(f"{lab}_{half}")
            for x in lst:
                b7.append(f"        .byte {op}({x})")
    b7.append("")
    open(os.path.join(GEN, "bank7.asm"), "w").write(
        "\n".join(b7) + "\n")

    info.update(knight_frames=KNIGHT_FRAMES, schemes=SCHEMES,
                room_schemes=[scheme(r) for r in range(NROOMS)],
                knight_bytes=kfig.size,
                tv={tv: rules.table(tv) for tv in ("ntsc", "pal")})
    info.update(collision=cmaps)
    json.dump(info, open(os.path.join(GEN, "game.json"), "w"),
              indent=0)
    files = ["kfig0.asm", "bank0.asm", "bank3.asm", "bank7.asm"]
    long = [f"{f}:{i}" for f in files
            for i, ln in enumerate(open(os.path.join(GEN, f)), 1)
            if len(ln.rstrip("\n")) > 60]
    print("assets:", " ".join(files),
          f"(lines over 60: {len(long)})")
    return long


if __name__ == "__main__":
    bad = art.check() + dungeon.check() + rules.check()
    if bad:
        sys.exit("\n".join(bad))
    build()
