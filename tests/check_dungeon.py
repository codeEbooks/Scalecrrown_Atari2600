"""check_dungeon.py - the 16 rooms the game draws, checked.

    python3 tests/check_dungeon.py [--out FOLDER] [--sheet PNG]

The dungeon of milestones 0.4-0.7 (game/assets/dungeon.py),
against the plan and against Sir Roderick's box:

1. the rules of the maps (dungeon.check());
2. the plan: the names, levels, keys, doors, spikes and
   serpents of tests/check_plan.py (the plan of the crypt),
   the doors on the right ways out (a grate on a stair down,
   the golden gate east of room 14), and the plan's route to
   the throne over the exits the maps really have;
3. each room, walked: every position of Sir Roderick's 8 x 24
   box (column 0-149, top line 1-135, odd) that touches no
   stone of the collision map, joined to its neighbours (a
   pixel left or right, two lines up or down). Every way in
   and every way out of the room must be in one piece with
   the others, and every way in must be free in the room it
   leads to: so from wherever he comes in he can reach every
   way out (and the start, in room 1);
4. the guards: a serpent's box on the floor along its whole
   path (its head, the top line, may be on the last line of the
   wall above: 0.6, along the top and bottom walls); the
   Serpent King sways in front of its throne; the two things
   of player 1 (0.6): the seam of each room, band A above it
   and band B below, the rooms where two things take turns
   (they share lines); the throne room (0.7): the King follows
   Sir Roderick's height (his top line his + 2), and from
   every height where the King's column is clear of the throne
   Sir Roderick can stand west and east of him with the blade
   on him and his box off the King's; the blade reaches the
   crown from both sides;
5. the levels get narrower (the story: "ever narrower"): the
   positions free for Sir Roderick, on average a room, fewer
   from level 1 to level 3, level 4 (the wide throne room left
   out) no more than level 2;
6. the things (0.5): with its door closed a room is walked
   again: the way the door closes has no position free, every
   other way in reaches every other way out and the place in
   front of the door (dungeon.zone); in a room with a chest
   every way in reaches the chest; the plates of the spikes
   can be stood on; and the game, walked room by room with
   the real maps (a door passes only when open, a chest gives
   its key, a door opens with the key of its level), reaches
   the throne room by the plan's route.

With --sheet: the 16 rooms in a 4 x 4 picture, as the
cartridge draws them (look.py, NTSC), with the plugs, the
grates closed, the chests, the gate, the guards where they
start, the comb of the seam; under each serpent a dotted line
(not in the game) shows its path.
"""
import argparse
import json
import os
import sys
from collections import deque

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "game",
                                "assets"))
import check_plan                               # noqa: E402
import dungeon                                  # noqa: E402
import rules                                    # noqa: E402

X_MAX, TOP_MIN, TOP_MAX = rules.X_MAX, rules.TOP_MIN, rules.TOP_MAX
GUARD_H = {"serpent": 16, "king": 40}
GUARD_W = {"serpent": 8, "king": 16}
GUARD_OFF = {"serpent": 3, "king": 4}


def box_free(w, x, top, width=rules.KNIGHT_W, height=rules.KNIGHT_H,
             off=rules.FIRST_PIXEL):
    x0 = x + off
    for line in range(top, top + height):
        for px in range(x0, x0 + width):
            if line >= 160 or px >= 160 or w[line // 16][px // 8]:
                return False
    return True


def free_positions(r, closed=False):
    w = dungeon.walls(r, closed)
    return {(x, t) for x in range(X_MAX + 1)
            for t in range(TOP_MIN, TOP_MAX + 1, 2)
            if box_free(w, x, t)}


def pieces(free):
    """The positions in pieces joined by single moves."""
    piece, n = {}, 0
    for p in sorted(free):
        if p in piece:
            continue
        n += 1
        piece[p] = n
        q = deque([p])
        while q:
            x, t = q.popleft()
            for nb in ((x - 1, t), (x + 1, t), (x, t - 2),
                       (x, t + 2)):
                if nb in free and nb not in piece:
                    piece[nb] = n
                    q.append(nb)
    return piece


def ways(r, free, closed=False):
    """The positions from which each way out is taken (with
    the door closed, not the one it closes)."""
    ex = dict(dungeon.exits(r))
    if closed:
        ex[DOOR_WAY[dungeon.door(r)]] = None
    out = {}
    if ex["east"] is not None:
        out["east"] = {p for p in free if p[0] == X_MAX}
    if ex["west"] is not None:
        out["west"] = {p for p in free if p[0] == 0}
    if ex["south"] is not None:
        out["south"] = {p for p in free if p[1] == TOP_MAX}
    if ex["north"] is not None:
        out["north"] = {p for p in free if p[1] == TOP_MIN}
    return out


DOOR_WAY = {"grate": "south", "gate": "east"}
BACK = {"east": "west", "west": "east", "south": "north",
        "north": "south"}


def zone_positions(r, free):
    z = dungeon.zone(r)
    return {p for p in free if z[0][0] <= p[0] <= z[0][1] and
            z[1][0] <= p[1] <= z[1][1]}


def arrival(way, p):
    """Where a way out of one room puts him in the next."""
    x, t = p
    return {"east": (0, t), "west": (X_MAX, t),
            "south": (x, TOP_MIN), "north": (x, TOP_MAX)}[way]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out")
    ap.add_argument("--sheet")
    a = ap.parse_args()
    checks = []

    def check(name, good, detail=""):
        checks.append(dict(check=name, ok=bool(good),
                           detail=detail))
        print(f"{'PASS' if good else 'FAIL'}  {name}"
              + (f": {detail}" if detail else ""))

    bad = dungeon.check()
    check("the rules of the maps", not bad, "; ".join(bad))
    # 2. the plan
    diff = []
    for r, rm in enumerate(dungeon.ROOMS):
        p = check_plan.ROOMS[r]
        mine = (rm["name"], rm["level"], rm.get("key"),
                rm.get("door") if r != 14 else None,
                rm["spikes"], rm["serpents"])
        if mine != p:
            diff.append(f"{r}: {mine} != {p}")
    check("names, levels, keys, doors, spikes, serpents as in "
          "the plan", not diff, "; ".join(diff))
    grates = [r for r, rm in enumerate(dungeon.ROOMS)
              if rm.get("door") and r != 14]
    check("a grate on each stair down, the gate east of room 14",
          all(dungeon.exits(r)["south"] is not None for r in grates)
          and dungeon.ROOMS[14].get("door") == 4 and
          dungeon.exits(14)["east"] == 15 and
          check_plan.EAST_DOOR == {14: 4},
          f"grates in rooms {grates}")
    mine = {r: sorted(n for n in dungeon.exits(r).values()
                      if n is not None) for r in range(16)}
    plan = {r: sorted(n for n, _ in check_plan.exits(r))
            for r in range(16)}
    check("the exits of the maps are the plan's", mine == plan)
    path = check_plan.solve()
    route = []
    for s in path or []:
        if not route or route[-1] != s[0]:
            route.append(s[0])
    check("the plan's route, every room", set(route) == set(
        range(16)), " -> ".join(map(str, route)))
    # 3. each room, walked
    free = {r: free_positions(r) for r in range(16)}
    report = {}
    for r in range(16):
        piece = pieces(free[r])
        wy = ways(r, free[r])
        ins = set()
        for r2 in range(16):            # ways in from the others
            for way, ps in ways(r2, free[r2]).items():
                if dungeon.exits(r2)[way] == r:
                    ins |= {arrival(way, p) for p in ps}
        if r == dungeon.START["room"]:
            st = dungeon.START
            ins.add((st["x"], st["top"]))
        blocked = sorted(p for p in ins if p not in free[r])
        used = {piece[p] for p in ins if p in piece}
        for ps in wy.values():
            used |= {piece[p] for p in ps}
        empty = [w for w, ps in wy.items() if not ps]
        report[r] = dict(name=dungeon.ROOMS[r]["name"],
                         ways={w: len(ps) for w, ps in wy.items()},
                         ways_in=len(ins), pieces_used=len(used),
                         blocked=blocked[:4],
                         free=len(free[r]))
        check(f"room {r:2d} {dungeon.ROOMS[r]['name']}: every way "
              "in reaches every way out",
              not blocked and not empty and len(used) == 1,
              f"ways {sorted(wy)}, {len(ins)} ways in"
              + (f", blocked {blocked[:2]}" if blocked else "")
              + (f", no way {empty}" if empty else "")
              + (f", {len(used)} pieces" if len(used) > 1 else ""))
    # 4. the guards
    bad = [f"room {r}" for r, rm in enumerate(dungeon.ROOMS)
           for g in rm["guards"] if g["kind"] == "serpent" and
           not dungeon.serpent_on_floor(r, g)]
    check("the guards on the floor along their paths", not bad,
          "; ".join(bad))
    seams = {r: dungeon.seam(r) for r in range(16)
             if dungeon.seam(r) is not None}
    turns = [r for r in range(16) if len(dungeon.band_a(r)) == 2]
    shares = all(
        max(o["top"] for o in dungeon.band_a(r)) <=
        min(o["top"] + dungeon.height(o["kind"]) - 1
            for o in dungeon.band_a(r)) for r in turns)
    check("two things on player 1: a seam where a thing or a "
          "second guard is above the first; two in turn only "
          "where they share lines", shares and all(
              len(dungeon.band_a(r)) <= 2 for r in range(16)),
          "seams (room: course) " + ", ".join(
              f"{r}: {c}" for r, c in seams.items())
          + f"; in turn in rooms {turns}")
    # 4b. the throne room (0.7)
    tr, strikes, crown = throne_reach(free)
    check("the throne room: the King struck from both sides "
          "from every height below the throne, the crown too",
          tr and crown, f"King's top lines struck from both sides "
          f"{strikes[0]}-{strikes[-1]}" if strikes else "none")
    # 5. the levels get narrower
    lv = {}
    for r in range(15):                 # not the throne room
        lv.setdefault(r // 4 + 1, []).append(len(free[r]))
    avg = {k: round(sum(v) / len(v)) for k, v in lv.items()}
    check("the levels get narrower",
          avg[1] > avg[2] > avg[3] and avg[4] <= avg[2],
          "free positions a room: " + ", ".join(
              f"level {k} {v}" for k, v in avg.items()))
    # 6. the things
    things = {}
    for r in range(16):
        rm = dungeon.ROOMS[r]
        d = dungeon.door(r)
        if not (d or rm.get("chest")):
            continue
        fr = free_positions(r, closed=bool(d))
        piece = pieces(fr)
        wy = ways(r, fr, closed=bool(d))
        ins = set()
        for r2 in range(16):
            for way, ps in ways(r2, free[r2]).items():
                if dungeon.exits(r2)[way] == r and not (
                        d and BACK[way] == DOOR_WAY[d]):
                    ins |= {arrival(way, p) for p in ps}
        zp = zone_positions(r, fr)
        used = {piece[p] for p in ins if p in piece}
        used |= {piece[p] for ps in wy.values() for p in ps}
        used |= {piece[p] for p in zp}
        shut = []
        if d:
            way = DOOR_WAY[d]
            shut = [p for p in fr if (way == "south" and
                                      p[1] == TOP_MAX) or
                    (way == "east" and p[0] == X_MAX)]
        blocked = [p for p in ins if p not in fr]
        things[r] = dict(zone=len(zp), pieces=len(used),
                         shut=len(shut))
        what = f"its {d} closed" if d else "its chest"
        check(f"room {r:2d} {rm['name']}: {what}: every way in "
              "reaches every way out and the "
              + ("door" if d else "chest"),
              zp and len(used) == 1 and not shut and not blocked,
              f"{len(zp)} positions in front of it"
              + (f", the {DOOR_WAY[d]} way shut" if d else ""))
    bad = []
    for r, rm in enumerate(dungeon.ROOMS):
        if rm.get("plate") is None:
            continue
        xs, (y0, y1) = dungeon.plate_zones(r)
        on = [p for p in free[r] if y0 <= p[1] <= y1 and
              any(a <= p[0] <= b for a, b in xs)]
        if not on:
            bad.append(f"room {r}")
    check("the plates of the spikes can be stood on", not bad,
          "; ".join(bad))
    real = walk_game()
    plan_rooms = []
    for s in check_plan.solve() or []:
        if not plan_rooms or plan_rooms[-1] != s[0]:
            plan_rooms.append(s[0])
    check("the game with the real maps reaches the throne by "
          "the plan's route", real == plan_rooms,
          " -> ".join(map(str, real or [])))
    rep = dict(rooms=report, levels=avg, things=things,
               route=real, checks=checks,
               passed=all(c["ok"] for c in checks))
    if a.out:
        os.makedirs(a.out, exist_ok=True)
        with open(os.path.join(a.out, "dungeon_check.json"),
                  "w") as f:
            json.dump(rep, f, indent=1)
    if a.sheet:
        sheet(a.sheet)
    print("DUNGEON OK" if rep["passed"] else "DUNGEON FAILS")
    return 0 if rep["passed"] else 1


def throne_reach(free):
    """(good, the King's top lines where Sir Roderick strikes
    him from both sides, the crown struck from both sides)."""
    import art
    th = dungeon.THRONE
    fr = free[th["room"]]
    bl = [c for _, c in art.ALL[art.BLADE_POSE]].index(
        art.BLADE_COLOUR)
    a, b = dungeon.king_pixels()
    kh = dungeon.height("king")
    fp, kw, h = rules.FIRST_PIXEL, rules.KNIGHT_W, rules.KNIGHT_H

    def meets(x, ky, face, box):
        x0, x1, t0, t1 = box
        p = x + fp + kw if face == 0 else x + fp - 8
        y = ky + bl
        return p <= x1 and p + 7 >= x0 and y <= t1 and y + 1 >= t0

    def touches(x, ky, box):
        x0, x1, t0, t1 = box
        return x + fp <= x1 and x + fp + kw - 1 >= x0 and \
            ky <= t1 and ky + h - 1 >= t0

    t0, t1 = th["top"]
    both = []
    for top in range(t0, t1 + 1, 2):
        ky = top - 2                    # where he draws the King
        box = (a, b, top, top + kh - 1)
        if all(any(meets(x, y, face, box) and not touches(x, y, box)
                   for x, y in fr if y == ky) for face in (0, 8)):
            both.append(top)
    # below the throne's row (lines 32 on) every height
    first = 32 + 2 + (1 - (32 + 2) % 2)     # odd, Sir Roderick at 33
    want = list(range(max(t0, first), t1 + 1, 2))
    crown = all(any(meets(x, y, face, dungeon.crown_box())
                    for x, y in fr) for face in (0, 8))
    return set(want) <= set(both), both, crown


def walk_game():
    """The rooms of walk_steps(), in the order visited."""
    steps = walk_steps()
    if steps is None:
        return None
    out = []
    for s, _ in steps:
        if not out or out[-1] != s[0]:
            out.append(s[0])
    return out


def walk_steps():
    """The shortest game over (room, key, open things), with
    the real rooms: from a room he can take a way out that is
    free in its map with the doors as they are; in a room he
    can open its chest (taking its key) or, with the key of
    its level, its door. [(state, what took him there)], what
    is "touch" or the way out taken."""
    start = (dungeon.START["room"], 0, 0)
    prev = {start: None}
    how = {}
    q = deque([start])
    while q:
        s = q.popleft()
        r, key, op = s
        if r == 15:
            out = []
            while s:
                out.append((s, how.get(s)))
                s = prev[s]
            return out[::-1]
        nexts = []
        bit = dungeon.thing_bit(r)
        lv = dungeon.ROOMS[r]["level"]
        if bit and not op & bit:
            if dungeon.ROOMS[r].get("chest"):
                nexts.append(((r, lv, op | bit), "touch"))
            elif key == lv:
                nexts.append(((r, 0, op | bit), "touch"))
        closed = bool(dungeon.door(r)) and not op & \
            dungeon.door_bit(lv)
        fr = free_positions_cached(r, closed)
        for way, ps in sorted(ways(r, fr, closed).items()):
            n = dungeon.exits(r)[way]
            if ps and n is not None:
                nexts.append(((n, key, op), way))
        for t, w in nexts:
            if t not in prev:
                prev[t] = s
                how[t] = w
                q.append(t)
    return None


_FP = {}


def free_positions_cached(r, closed):
    if (r, closed) not in _FP:
        _FP[(r, closed)] = free_positions(r, closed)
    return _FP[(r, closed)]


def sheet(path, scale=2, closed=True):
    """The 16 rooms in a 4 x 4 picture, NTSC, with names, the
    grates closed, the chests and the gate (0.5), the guards
    at their start, the comb of the seam and, under each
    serpent, its path dotted (0.6)."""
    import look
    from PIL import Image, ImageDraw
    pal = look.PALETTE["ntsc"]
    w, h, gap, label = 160 * scale, 160, 8, 14
    im = Image.new("RGB", (4 * w + 3 * gap,
                           4 * (h + label) + 3 * gap), (24, 24, 24))
    dr = ImageDraw.Draw(im)
    for r in range(16):
        rm = dungeon.ROOMS[r]
        pic = look.room_picture(rm, "ntsc", plug=dungeon.plug(r),
                                closed=closed)
        figs = []
        th = dungeon.thing_item(r)
        if th:
            figs.append((th["kind"], th["x"], th["top"], False,
                         None))
        for g in rm["guards"]:
            figs.append((g["kind"] + "_a", g["x"], g["top"], True,
                         rm["level"] if g["kind"] == "serpent"
                         else None))
        for name, x, top, mirror, lv in figs:
            wide = name.startswith("king")
            cols = look.pose_colours(name, "ntsc", lv)
            for j, (bits, _) in enumerate(look.figure_lines(name)):
                for i in range(8):
                    b = 7 - i if mirror else i
                    if bits & (0x80 >> b):
                        for k in range(2 if wide else 1):
                            xx = x + (4 + 2 * i + k if wide
                                      else 3 + i)
                            pic[top + j][xx] = cols[j]
        for g in rm["guards"]:
            if g["kind"] == "serpent":
                y = g["top"] + dungeon.SERPENT_H
                for xx in range(g["path"][0] + 3, g["path"][1] + 11,
                                2):
                    pic[y][xx] = 0x0E
        c = dungeon.comb_line(r)
        if c is not None:
            pic[c][0:8] = [0] * 8
        x0 = (r % 4) * (w + gap)
        y0 = (r // 4) * (h + label + gap)
        dr.text((x0 + 2, y0 + 1), f"{r}  {rm['name']}",
                fill=(230, 230, 230))
        for y in range(160):
            for x in range(160):
                col = tuple(pal[f"{pic[y][x]:02X}"])
                for s in range(scale):
                    im.putpixel((x0 + scale * x + s, y0 + label + y),
                                col)
    im.save(path)


if __name__ == "__main__":
    raise SystemExit(main())
