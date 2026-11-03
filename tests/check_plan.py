"""check_plan.py - the dungeon plan of Scalecrown, as data.

    python3 tests/check_plan.py [--out FOLDER]

The plan of the crypt, written once here, and checked:

1. 16 rooms, 4 levels of 4 (the rows of the 4 x 4 grid);
2. east-west exits inside a level, stairs only straight down
   (south gap of room r, north gap of room r + 4);
3. one door per level; a key per level, in a chest, on the
   key's own level, reachable before its door;
4. every room reachable; the game can be won: a search over
   (room, key held, doors open, chests opened) finds the
   shortest route to the throne room with the King's key;
5. spikes and serpents grow level by level as in the
   technical sheet (section 4.2);
6. the rooms at the two ends of a level need the ball as a
   plug on their outer side; the ball is never needed twice
   in one room.

It is a check of a proposal: the real dungeon.py comes with
milestone 0.4 and reads the rooms the game draws.
"""
import argparse
import json
import os
from collections import deque

# room: name, level, key (level number) in a chest, door on
# the south gap (level number), spikes, serpents, notes
ROOMS = {
    0: ("RUBBLE HALL", 1, 1, None, False, 2),
    1: ("THE BROKEN GATE", 1, None, None, False, 0),
    2: ("PILLAR WALK", 1, None, None, True, 2),
    3: ("THE IRON STAIR", 1, None, 1, False, 2),
    4: ("BONE NICHE", 2, 2, None, False, 2),
    5: ("THE NARROW STEPS", 2, None, 2, True, 2),
    6: ("SHED SKINS", 2, None, None, True, 2),
    7: ("THE LANDING", 2, None, None, False, 0),
    8: ("THE DROWNED STAIR", 3, None, 3, True, 2),
    9: ("COLD LANDING", 3, None, None, False, 2),
    10: ("REED GALLERY", 3, None, None, True, 2),
    11: ("FANG CISTERN", 3, 3, None, True, 2),
    12: ("LAST LANDING", 4, None, None, False, 2),
    13: ("HALL OF COILS", 4, 4, None, True, 2),
    14: ("THE GILDED GATE", 4, None, None, True, 2),
    15: ("THRONE OF SCALES", 4, None, None, False, 0),
}
START = 1
THRONE = 15
EAST_DOOR = {14: 4}     # the gate of level 4: east of room 14
# 0.9.2: a second serpent in every room that had one (more
# serpents, asked for by the author); 0.6-0.9.1: 3, 5, 7, 5
SHEET = {1: (1, 6), 2: (2, 6), 3: (3, 8), 4: (2, 6)}


def exits(r):
    """(neighbour, door level or None) of room r."""
    out = []
    col = r % 4
    if col > 0:
        door = EAST_DOOR.get(r - 1)
        out.append((r - 1, door))
    if col < 3:
        out.append((r + 1, EAST_DOOR.get(r)))
    if ROOMS[r][3]:
        out.append((r + 4, ROOMS[r][3]))        # stairs down
    if r >= 4 and ROOMS[r - 4][3]:
        out.append((r - 4, ROOMS[r - 4][3]))    # stairs up
    return out


def solve():
    """Breadth-first over (room, key held, doors, chests)."""
    start = (START, 0, frozenset(), frozenset())
    prev = {start: None}
    q = deque([start])
    while q:
        s = q.popleft()
        room, key, doors, chests = s
        if room == THRONE:
            path = []
            while s:
                path.append(s)
                s = prev[s]
            return path[::-1]
        nexts = []
        k = ROOMS[room][2]
        if k and k not in chests and key == 0:
            nexts.append((room, k, doors, chests | {k}))
        for n, door in exits(room):
            if door is None or door in doors:
                nexts.append((n, key, doors, chests))
            elif key == door:
                nexts.append((n, 0, doors | {door}, chests))
        for t in nexts:
            if t not in prev:
                prev[t] = s
                q.append(t)
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out")
    a = ap.parse_args()
    checks = []

    def check(name, good, detail=""):
        checks.append(dict(check=name, ok=bool(good),
                           detail=detail))
        print(f"{'PASS' if good else 'FAIL'}  {name}"
              + (f": {detail}" if detail else ""))

    check("16 rooms, 4 per level",
          len(ROOMS) == 16 and all(
              ROOMS[r][1] == r // 4 + 1 for r in ROOMS))
    keys = {v[2]: r for r, v in ROOMS.items() if v[2]}
    doors = {v[3]: r for r, v in ROOMS.items() if v[3]}
    doors.update({lv: r for r, lv in EAST_DOOR.items()})
    check("one key and one door per level",
          sorted(keys) == [1, 2, 3, 4] and
          sorted(doors) == [1, 2, 3, 4])
    check("each key on its own level",
          all(ROOMS[r][1] == lv for lv, r in keys.items()))
    check("throne room is the last room of level 4",
          THRONE == 15 and ROOMS[THRONE][1] == 4)
    # reachability with every door open
    seen, q = {START}, deque([START])
    while q:
        r = q.popleft()
        for n, _ in exits(r):
            if n not in seen:
                seen.add(n)
                q.append(n)
    check("every room reachable", len(seen) == 16)
    path = solve()
    check("the game can be won", path is not None)
    route = []
    for s in path or []:
        if not route or route[-1] != s[0]:
            route.append(s[0])
    check("the route visits every room",
          set(route) == set(ROOMS), " -> ".join(map(str, route)))
    for lv, (spk, snk) in SHEET.items():
        rs = [r for r in ROOMS if ROOMS[r][1] == lv]
        s = sum(ROOMS[r][4] for r in rs)
        n = sum(ROOMS[r][5] for r in rs)
        check(f"level {lv}: spikes and serpents as in the sheet",
              (s, n) == (spk, snk), f"{s} rooms with spikes, "
              f"{n} serpents")
    check("no serpent in the starting room", ROOMS[START][5] == 0)
    plugs = [r for r in ROOMS if r % 4 in (0, 3)]
    clash = [r for r in plugs if r in EAST_DOOR]
    check("the ball: a plug or a gate, never both",
          not clash, f"plugs in rooms {plugs}")
    rep = dict(rooms={r: dict(name=v[0], level=v[1], key=v[2],
                              door_south=v[3], spikes=v[4],
                              serpents=v[5], exits=exits(r))
                      for r, v in ROOMS.items()},
               route=route, moves=len(route) - 1, checks=checks,
               passed=all(c["ok"] for c in checks))
    if a.out:
        os.makedirs(a.out, exist_ok=True)
        with open(os.path.join(a.out, "plan_check.json"), "w") as f:
            json.dump(rep, f, indent=1)
    print("PLAN OK" if rep["passed"] else "PLAN FAILS")
    return 0 if rep["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
