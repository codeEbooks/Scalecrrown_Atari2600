"""verify_0_9.py - milestones 0.9, 0.9.1, 0.9.2, 0.9.3, 0.9.4 and
1.0 (the 0.9.4, which became the 1.0: the same tests) of
Scalecrown:
the final cartridge, NTSC and PAL; every test from all eight
banks (0.9.1: the King and the serpents harder, rules.py; the
same tests, the King's bite told from the venom by the venom
gone, the last GAME OVER with an energy that is not a multiple
of the bite. 0.9.2: 12 units, a second serpent in six rooms,
serpents that chase him, the King struck on his head only: the
bite and the spikes shown in the second game, a thrust on the
King's coils that must not count, the strike spots off the
plates. 0.9.3: a serpent chases him only with his column on its
path; off it, it keeps its round. 0.9.4: the chase a sprint,
two blows for a serpent - the first pushes and stuns it, and
it blinks -, a serpent killed back in a while at the far end
of its path: the route pushes two to the ends of their paths
and waits for one to come back; the serpents' facts; the
coverage with a reason for NTSC only, the sprint never two
pixels there).

    python3 tests/verify_0_9.py --stella PATH [--mutations]
                                [--audio] [--out FOLDER]
                                [--workers N]

For the two cartridges (NTSC and PAL, 32K F4SC), everything of
milestones 0.2-0.8, and (0.9) all of it from each of the eight
banks the console can start in:

A. the route: a whole game played by a script of joystick,
   button, SELECT and RESET, planned with tests/model.py: the
   title and the three sound modes; the game of the plan in the
   SOUND FX mode (0.9: every stair with the sound of its steps)
   with the walls, the sword, RESET, the edges, the serpents,
   the seams, the flicker, the chests and the doors; the throne
   room and VICTORY; the VICTORY screen; the MUSIC mode, RESET
   on the title and held, SELECT in a game; GAME OVER and its
   screen, RESET on it; GAME OVER again (0.9: after one wound
   of the spikes, so the last bite takes 2 from 1 and the
   energy stops at 0), the button back to the title;
A2. the songs (0.8): the two ends put in the RAM of the
   cartridge and in the model at once, in the three modes: the
   fanfare and the lament to their end and then silence;
B. the simulator, starting from each of the eight banks with
   its own RAM and Superchip RAM at random (0.9: the whole route,
   the songs, the two random games and the extremes from every
   bank, in processes side by side):
   - 262 lines a frame (NTSC) or 312 (PAL), VSYNC 228 cycles;
   - no read of the write side of the Superchip RAM;
   - every write to the TIA inside its window (rooms, title, end
     screens); the idle cycles of each kind of line; the VBLANK
     left on the title, in the game and on the end screens;
   - the seam in every frame of a room that has one;
   - after every frame, the state of the game and the six sound
     registers equal to the model's (model.py, sound_model.py);
     the songs started and the silence after the ends;
   - the cycles of the things and of the sound player, the
     overscan left; the change of room;
   - the flicker, measured on the route;
C. two random games (the music, the SOUND FX mode);
D. the extremes: Sir Roderick at every column and height in
   every pose, the guards below the seams, every room closed
   and open, the throne room (the King, the venom, the crown),
   the end screens with four scores; and the figures in the
   cartridge, read as the kernels read them;
E. Stella, the route from each of the eight banks (0.9; before,
   banks 0 and 7): the RAM of every frame equal to the
   simulator's, the pictures equal to the ones drawn from what
   the model's frame showed (look.py, art.py); and (0.9) the ROM
   bytes Stella's counters say were read, the same that the
   simulator read (outside the window of the Superchip RAM);
F. with --audio: the title recorded from Stella at its normal
   speed (tests/audio_check.py: 0.9, the start found on 15
   seconds, not 5: the march matched itself two beats later);
G. with --mutations: one-line defects that the checks must
   catch (the route, the songs, the extremes, the figures,
   Stella and the random games, from bank 7, stopping at the
   first difference);
H. the coverage (0.9): every instruction of the listing that
   the simulator ran in any of the tests from any bank; those
   it never ran must each have a reason in
   tests/coverage_notes.py (and every reason must still hold).

The simulator looks at the writes to the TIA of each frame
when the frame ends and forgets them (a route of 15 000
frames keeps the memory under 100 MB).
"""
import argparse
import concurrent.futures
import copy
import hashlib
import json
import os
import random
import re
import shutil
import subprocess
import sys
from collections import deque

from py65.devices.mpu6502 import MPU

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "game", "assets"))
from vcs_sim import VCS, read_symbols, LINE      # noqa: E402
import stella_run                                 # noqa: E402
import model                                      # noqa: E402
import sound_model                                # noqa: E402
import sfx                                        # noqa: E402
import coverage_notes                             # noqa: E402
import check_dungeon                              # noqa: E402
import art                                        # noqa: E402
import dungeon                                    # noqa: E402
import look                                       # noqa: E402
import rooms                                      # noqa: E402
import rules                                      # noqa: E402
import tia_audio                                  # noqa: E402
import audio_check                                # noqa: E402

MPU_NAMES = MPU.disassemble     # (mnemonic, mode) by opcode

BUILD = os.path.join(ROOT, "game", "build")
SRC = os.path.join(ROOT, "game", "src")
ASSETS = os.path.join(ROOT, "game", "assets")
MS = "1.0"
EVID = os.path.join(ROOT, "evidence", MS, "workspace")
# the step of the chain of the book (tests/verify_chain.py
# sets it with BUILD): 9, the whole game, for these tests
STEP = 9
TV = {"ntsc": dict(lines=262, vis0=40, visn=192, top=0, row0=14),
      "pal": dict(lines=312, vis0=48, visn=228, top=18, row0=13)}
H_OFFSET = 3            # first pixel of a player = column + 3
DOUBLE_OFFSET = 4       # ... of a player twice as wide
BLOCK_OFFSET = 3        # 48-pixel blocks: column of player 0 + 3
POSES = ["knight_stand", "knight_walk1", "knight_walk2",
         "knight_thrust", "knight_parry"]
QUAD_OFFSET = 4         # ... four times as wide (0.7: the crown)
NONE, RIGHT, LEFT, DOWN, UP = 0xFF, 0x7F, 0xBF, 0xDF, 0xEF
RANDOM_FRAMES = 6000
STELLA_FIRST = 2500             # mutations: Stella on these first
SHORT_FRAMES = 300      # the route from banks 1-6: the start

# TIA registers
VBLANK, WSYNC = 0x01, 0x02
COLUP0, COLUP1, COLUPF, COLUBK = 0x06, 0x07, 0x08, 0x09
PF0, PF1, PF2, GRP0, GRP1, ENAM0 = 0x0D, 0x0E, 0x0F, 0x1B, 0x1C, \
    0x1D
ENAM1 = 0x1E
NAMES = {COLUP0: "COLUP0", COLUP1: "COLUP1", COLUPF: "COLUPF",
         COLUBK: "COLUBK", PF0: "PF0", PF1: "PF1", PF2: "PF2",
         GRP0: "GRP0", GRP1: "GRP1", ENAM0: "ENAM0",
         ENAM1: "ENAM1"}
# windows (cycle of the store's write): when a change of the
# register cannot be caught by the beam
WIN = {GRP0: [(0, 21)], GRP1: [(0, 21)], COLUP0: [(0, 21)],
       COLUP1: [(0, 21)], COLUPF: [(0, 21)], COLUBK: [(0, 21)],
       PF0: [(0, 21)], PF1: [(0, 26), (71, 75)],
       PF2: [(0, 37), (60, 75)], ENAM0: [(0, 21)],
       ENAM1: [(0, 21)]}
AUDIO = {0x15: "C0", 0x16: "C1", 0x17: "F0", 0x18: "F1",
         0x19: "V0", 0x1A: "V1"}
OFF = (NONE, False, False, False)
# into the game for the extremes: a few frames, the button
INTO_GAME = [OFF] * 3 + [(NONE, True, False, False)] + [OFF] * 16


# ---------------------------------------------------------
# A. the route

_FREE = {}


def free(r, closed=False):
    """The positions of Sir Roderick's box free in room r,
    with its door closed or open."""
    if (r, closed) not in _FREE:
        _FREE[(r, closed)] = check_dungeon.free_positions(r, closed)
    return _FREE[(r, closed)]


def bfs(fr, start, goal, allowed=None):
    """The shortest way (positions, one move apart) from start
    to a position where goal(position) holds, over the
    positions fr (and, with allowed, only those it allows
    after the start), or None."""
    prev = {start: None}
    q = deque([start])
    while q:
        p = q.popleft()
        if goal(p):
            path = []
            while p:
                path.append(p)
                p = prev[p]
            return path[::-1]
        x, t = p
        for nb in ((x + 1, t), (x - 1, t), (x, t + 2), (x, t - 2)):
            if nb in fr and nb not in prev and (
                    allowed is None or allowed(nb)):
                prev[nb] = p
                q.append(nb)
    return None


def plan(r, start, goal, closed=False, allowed=None):
    path = bfs(free(r, closed), start, goal, allowed)
    if path is None:
        raise RuntimeError(f"route: no way in room {r} from {start}")
    return path


WAY_GOAL = {"east": lambda p: p[0] == rules.X_MAX,
            "west": lambda p: p[0] == 0,
            "south": lambda p: p[1] == rules.TOP_MAX,
            "north": lambda p: p[1] == rules.TOP_MIN}
WAY_PUSH = {"east": RIGHT, "west": LEFT, "south": DOWN, "north": UP}


def lines_meet(ky, top, h):
    return ky <= top + h - 1 and ky + rules.KNIGHT_H - 1 >= top


def out_of_reach(r, k, p):
    """Guard k of room r can never bite Sir Roderick at p: its
    lines do not meet his box's, or its path keeps 8 columns
    away from him."""
    s = dungeon.ROOMS[r]["guards"][k]
    x, ky = p
    if not lines_meet(ky, s["top"], dungeon.height(s["kind"])):
        return True
    return x > s["path"][1] + 7 or x < s["path"][0] - 7


def kill_now(g, k):
    """Would the button, pressed in the next frame, strike guard
    k of the model g (the thrust starts, the blade is out, the
    guards are where the last overscan left them)? (0.9.4: a
    blow wounds or kills; a stunned guard takes none.)"""
    if not g.screen or g.over or g.held & model.FIRE or \
            g.thrust > 1 or not g.live >> k & 1 or g.gt[k]:
        return False
    pose = g.kpose
    g.kpose = rules.THRUST_POSE
    try:
        return g.blade_hits(k)
    finally:
        g.kpose = pose


def sim_poke(poke):
    """The values of the model put in after the logic (0.8), as
    the cartridge keeps them: over, won, song by their names;
    restart: $FF in smode (a song to start); score: three BCD
    bytes; request: sfxreq."""
    out = {}
    for name, val in poke.items():
        if name in ("over", "won", "song"):
            out[name] = val
        elif name == "restart":
            if val:
                out["smode"] = 0xFF
        elif name == "score":
            bcd = int(f"{val:06d}", 16)
            out.update({"score": bcd >> 16,
                        "score+1": (bcd >> 8) & 0xFF,
                        "score+2": bcd & 0xFF})
        elif name == "request":
            out["sfxreq"] = val
        else:
            raise ValueError(f"no poke for {name}")
    return out


class Snap:
    """What the tests keep of the model after a frame."""

    def __init__(self, g):
        self._state = g.state()
        self.audio = dict(g.audio)
        self.pic = g.pic
        for a in ("room", "screen", "opened", "energy", "thrust",
                  "t", "over", "live", "kpose", "frames", "won",
                  "song", "started", "mode", "score", "kx"):
            setattr(self, a, getattr(g, a))
        self.sx, self.gt = list(g.sx), list(g.gt)   # 0.9.4
        self.blinking = [g.blinks(k) for k in (0, 1)]

    def state(self):
        return self._state


class Director:
    """Plays the model and writes down the inputs: the route
    for the cartridge, and the frames to photograph."""

    def __init__(self, tv, careful=False, keep=True, step=None):
        self.tv = tv
        self.g = model.Game(tv, STEP if step is None else step)
        self.careful = careful          # waits for the spikes,
        #                                 keeps clear of serpents
        self.keep = keep
        self.inputs = []                # (SWCHA, fire, RESET,
        #                                  SELECT)
        self.states = []                # the model after each
        self.shots = {}                 # frame -> what it shows
        self.hunting = None             # the guard being hunted
        self.pokes = []                 # 0.8: values put in the
        #                                 RAM after the logic

    def frame(self, swcha=NONE, fire=False, reset=False,
              select=False, poke=None):
        """One frame; poke (0.8, the songs): values of the model
        put in after the logic, in the model and, by their RAM
        names, in the cartridge (sim_poke)."""
        self.g.step(swcha, fire, reset, select, poke)
        self.inputs.append((swcha, fire, reset, select))
        self.pokes.append(sim_poke(poke or {}))
        if self.keep:
            self.states.append(Snap(self.g))

    def select(self):
        self.frame(select=True)

    def wait(self, n, swcha=NONE):
        for _ in range(n):
            self.frame(swcha)

    def press(self):
        self.frame(fire=True)

    def shot(self, label):
        self.shots[len(self.inputs)] = label

    def head(self, n):
        """The first n frames of the route (the mutations try
        Stella on them first)."""
        h = copy.copy(self)
        h.inputs, h.states = self.inputs[:n], self.states[:n]
        h.pokes = self.pokes[:n]
        h.shots = {k: v for k, v in self.shots.items() if k <= n}
        return h

    def on_plate(self, g):
        pz = dungeon.plate_zones(g.room)
        if not pz or not g.screen:
            return False
        xs, (y0, y1) = pz
        return y0 <= g.ky <= y1 and any(a <= g.kx <= b
                                         for a, b in xs)

    def danger(self, swcha, margin=24):
        """Careful: would this joystick put him on a plate that
        is up, or that goes up within `margin` frames?"""
        if not self.careful or self.on_plate(self.g):
            return False
        c = copy.deepcopy(self.g)
        c.step(swcha)
        return c.room == self.g.room and self.on_plate(c) and (
            c.spup or c.spk < margin)

    def leaves(self, swcha):
        """Would this joystick take him out of the room?"""
        c = copy.deepcopy(self.g)
        c.step(swcha)
        return c.room != self.g.room

    def until(self, swcha, cond, stay=True, limit=600):
        """Push until cond; with stay, never through an
        opening."""
        for _ in range(limit):
            if cond(self.g):
                return
            if stay and self.leaves(swcha):
                return
            self.frame(swcha)
        raise RuntimeError("route: never got there")

    def until_stuck(self, swcha, attr, quiet=12, limit=400):
        last, same = None, 0
        for _ in range(limit):
            self.frame(swcha)
            v = getattr(self.g, attr)
            same = same + 1 if v == last else 0
            last = v
            if same >= quiet:
                return
        raise RuntimeError("route: never stopped")

    # -- the serpents (0.6) ---------------------------------
    def biters(self):
        """The guards of the room alive that bite."""
        g = self.g
        gs = dungeon.ROOMS[g.room]["guards"]
        return [k for k, s in enumerate(gs) if s["kind"] == "serpent"
                and g.live >> k & 1]

    def safe(self, p, but=None):
        return all(out_of_reach(self.g.room, k, p)
                   for k in self.biters() if k != but)

    def go(self, goal, limit=80, bold=False):
        """Walk to a position where goal holds, along the
        shortest way, planned again after every straight run
        (in PAL a step can be 2 pixels); never out of the
        room: at the edge of a way out he stops. Careful (and
        not bold), the way keeps out of the serpents' reach;
        where no way does, the serpents in the way are hunted
        first (0.9.4: a serpent that comes back on the way
        makes him plan again). After GAME OVER nothing moves: it gives up (the
        caller sees the game over)."""
        for _ in range(limit):
            g = self.g
            p = (g.kx, g.ky)
            if goal(p) or g.over:
                return
            closed = not g.map_open
            path = None
            if self.careful and not bold and self.biters():
                path = bfs(free(g.room, closed), p, goal,
                           lambda q: self.safe(q, self.hunting))
                if path is None:
                    plain = plan(g.room, p, goal, closed)
                    ks = [k for k in self.biters()
                          if k != self.hunting and any(
                              not out_of_reach(g.room, k, q)
                              for q in plain)]
                    if not ks:
                        path = plain
                    else:
                        self.hunt(ks[0])
                        continue
            if path is None:
                path = plan(g.room, p, goal, closed)
            if len(path) < 2:
                return
            dx = path[1][0] - path[0][0]
            dt = path[1][1] - path[0][1]
            k = 1
            while k + 1 < len(path) and \
                    (path[k + 1][0] - path[k][0],
                     path[k + 1][1] - path[k][1]) == (dx, dt):
                k += 1
            tx, tt = path[k]
            sw = RIGHT if dx > 0 else LEFT if dx < 0 else \
                DOWN if dt > 0 else UP
            bs = self.biters()          # 0.9.4: they come back
            for _ in range(400):
                g = self.g
                if g.over:
                    return
                if self.careful and not bold and \
                        self.biters() != bs:
                    break               # plan again
                if (dx > 0 and g.kx >= tx) or (dx < 0 and g.kx <= tx) \
                        or (dt > 0 and g.ky >= tt) or \
                        (dt < 0 and g.ky <= tt):
                    break
                if self.leaves(sw):
                    return
                while self.danger(sw):
                    self.frame()        # the spikes: wait
                self.frame(sw)
        raise RuntimeError("route: never got there")

    def spots(self, k):
        """Where Sir Roderick can strike guard k of this room:
        (column, top line, facing), his blade on its lines and
        its path passing 8-15 columns in front of him."""
        g = self.g
        s = dungeon.ROOMS[g.room]["guards"][k]
        a, b = s["path"]
        out = []
        for x, ky in free(g.room, not g.map_open):
            if not 0 <= ky + model.BLADE_LINE + 1 - s["top"] <= \
                    dungeon.SERPENT_H:
                continue
            for face in (0, 8):
                lo, hi = (x + 8, x + 15) if face == 0 else \
                    (x - 15, x - 8)
                if lo <= b and hi >= a:
                    out.append((x, ky, face))
        # 0.9.2 (12 units): not on a plate, where the spikes
        # can rise under him after the blow, if he can help it
        pz = dungeon.plate_zones(g.room)
        if pz:
            xs, (y0, y1) = pz
            off = [o for o in out if not (
                y0 <= o[1] <= y1 and any(c <= o[0] <= e
                                         for c, e in xs))]
            out = off or out
        return out

    def strike(self, k, spot, wait_max=900):
        """From here: walk to the spot, face, wait for the
        guard and strike when the blade will kill it (0.9.4:
        strike again, after its stun, until it dies). True if
        it died and nothing hurt him (a trial on a copy)."""
        x, ky, face = spot
        e0 = self.g.energy
        try:
            self.go(lambda p: p == (x, ky))
        except RuntimeError:
            return False
        if self.g.kdir != face:
            self.frame(RIGHT if face == 0 else LEFT)
        for _ in range(wait_max):
            if not self.g.live >> k & 1 or self.g.energy < e0:
                break
            if kill_now(self.g, k):
                self.press()
            else:
                self.frame()
        return not self.g.live >> k & 1 and self.g.energy == e0

    def first_blow(self, k, spot, wait_max=900):
        """0.9.4: from here, walk to the spot, face, wait for
        guard k and strike once: True if it is wounded and
        nothing hurt him (a trial on a copy)."""
        x, ky, face = spot
        e0 = self.g.energy
        try:
            self.go(lambda p: p == (x, ky))
        except RuntimeError:
            return False
        if self.g.kdir != face:
            self.frame(RIGHT if face == 0 else LEFT)
        for _ in range(wait_max):
            g = self.g
            if g.live >> (k + 2) & 1 or g.energy < e0 or \
                    not g.live >> k & 1:
                break
            if kill_now(g, k):
                self.blow_from = g.sx[k]    # where it was
                self.press()
            else:
                self.frame()
        return bool(self.g.live >> (k + 2) & 1) and \
            self.g.energy == e0

    def wound_at_end(self, k, face, tries=8, at_end=True,
                     hidden=False):
        """0.9.4: the first blow on guard k, pushing it to the
        end of its path (face 0: he faces right, the east end;
        8: the west end), unhurt. For each spot facing that way,
        the nearest the end first: to the place out of every
        guard's reach nearest the spot, keeping out of reach
        (a trial: given up if it cannot); then, for each wait
        there, a trial: to the spot and strike once. Not at_end
        (face None): a first blow anywhere, the spots nearest
        him first; hidden: then on to the first frame its blink
        hides it, still unhurt."""
        g = self.g
        r = g.room
        gs = dungeon.ROOMS[r]["guards"]
        a, b = gs[k]["path"]
        end = b if face == 0 else a
        fr = free(r, not g.map_open)
        spots = [s for s in self.spots(k)
                 if face is None or s[2] == face]
        if at_end:
            spots.sort(key=lambda s: abs(s[0] - end))
        else:
            spots.sort(key=lambda s: abs(s[0] - g.kx) +
                       abs(s[1] - g.ky))
        for spot in spots[:tries]:
            wp = bfs(fr, spot[:2], lambda p: all(
                out_of_reach(r, j, p) for j in range(len(gs))))
            if wp is None:
                continue
            t0 = self.trial()
            t0.careful = True
            e0, l0 = t0.g.energy, t0.g.live & (1 << k | 4 << k)
            try:
                t0.go(lambda p: p == wp[-1])  # (it may hunt the
            except RuntimeError:                # others)
                continue
            if t0.g.energy < e0 or \
                    t0.g.live & (1 << k | 4 << k) != l0:
                continue
            for w in range(0, 600, 6):
                t = t0.trial()
                t.inputs = list(t0.inputs)
                t.wait(w)
                # (pushed less than KNOCK_PX: the end stops it)
                if not t.first_blow(k, spot) or at_end and not (
                        t.g.sx[k] == end and
                        abs(t.blow_from - end) < rules.KNOCK_PX):
                    continue
                if hidden:
                    e1 = t.g.energy
                    for _ in range(4 * rules.FLASH_FRAMES + 4):
                        if t.g.blinks(k):
                            break
                        t.frame()
                    if not t.g.blinks(k) or t.g.energy < e1:
                        continue
                for inp in t.inputs:
                    self.frame(*inp)
                return
        raise RuntimeError(f"route: guard {k} of room {r} "
                           "never pushed to the end")

    def to_safety(self):
        """0.9.4: to the nearest place out of every guard's
        reach (the dead ones too: they come back), if a trial
        says he gets there unhurt."""
        g = self.g
        r = g.room
        n = len(dungeon.ROOMS[r]["guards"])
        esc = bfs(free(r, not g.map_open), (g.kx, g.ky),
                  lambda p: all(out_of_reach(r, j, p)
                                for j in range(n)))
        if esc is None:
            raise RuntimeError("route: no place out of reach")
        t = self.trial()
        e0 = t.g.energy
        t.go(lambda p: p == esc[-1], bold=True)
        if t.g.energy < e0:
            raise RuntimeError("route: hurt on the way out")
        for inp in t.inputs:
            self.frame(*inp)

    def back(self, k):
        """0.9.4: out of every guard's reach, wait for guard k
        to come back."""
        self.to_safety()
        self.wait_until(lambda g: g.live >> k & 1,
                        limit=self.g.t["RESPAWN_FRAMES"] + 10)

    def trial(self):
        """A copy of this director, to try a plan on."""
        t = Director(self.tv, careful=False, keep=False,
                     step=self.g.nstep)
        t.g = copy.deepcopy(self.g)
        return t

    def hunt(self, k, limit=4000):
        """Kill guard k: wait out of every serpent's reach near
        the best spot, and go and strike when a trial says it
        works."""
        g = self.g
        r = g.room
        fr = free(r, not g.map_open)
        spots = self.spots(k)
        if not spots:
            raise RuntimeError(f"route: guard {k} of room {r} "
                               "cannot be struck")
        here = (g.kx, g.ky)
        dist = {}
        q = deque([here])
        dist[here] = 0
        while q:
            p = q.popleft()
            x, t = p
            for nb in ((x + 1, t), (x - 1, t), (x, t + 2), (x, t - 2)):
                if nb in fr and nb not in dist:
                    dist[nb] = dist[p] + 1
                    q.append(nb)
        spots = [s for s in spots if (s[0], s[1]) in dist]
        prev, self.hunting = self.hunting, k
        try:
            # 0.9.4 (the serpents sprint, take two blows, come
            # back): first a strike from here that a trial says
            # works, the nearest spots first
            for spot in sorted(spots, key=lambda s: dist[s[:2]])[:6]:
                t = self.trial()
                if t.strike(k, spot):
                    for inp in t.inputs:
                        self.frame(*inp)
                    return
        finally:
            self.hunting = prev
        if not self.safe(here):
            # first out of their reach (after a bite nothing
            # hurts him for a while), if a trial says he gets
            # there unhurt (0.9.4)
            esc = bfs(fr, here, lambda p: self.safe(p))
            if esc:
                t = self.trial()
                e0 = t.g.energy
                try:
                    t.go(lambda p: p == esc[-1], bold=True)
                    ok = t.g.energy == e0
                except RuntimeError:
                    ok = False
                if ok:
                    for inp in t.inputs:
                        self.frame(*inp)
        # the places out of reach he can walk to from here
        cur = (self.g.kx, self.g.ky)
        region = {cur}
        q = deque([cur])
        while q:
            x, t = q.popleft()
            for nb in ((x + 1, t), (x - 1, t), (x, t + 2), (x, t - 2)):
                if nb in fr and nb not in region and self.safe(nb):
                    region.add(nb)
                    q.append(nb)
        # for every place, the nearest place out of reach (a
        # search from all of them at once)
        near = {p: p for p in fr if self.safe(p)}
        q = deque(near)
        while q:
            x, t = p = q.popleft()
            for nb in ((x + 1, t), (x - 1, t), (x, t + 2), (x, t - 2)):
                if nb in fr and nb not in near:
                    near[nb] = near[p]
                    q.append(nb)
        waits = {sp: near.get(sp[:2]) for sp in spots}
        spots.sort(key=lambda s: (waits[s] not in region,
                                  not self.safe(s[:2]), dist[s[:2]]))
        prev, self.hunting = self.hunting, k
        try:
            for spot in spots[:8]:
                # wait at the place out of reach nearest the
                # spot, if he can walk there out of reach; else
                # where he is, and let a trial cross over
                w = waits[spot]
                if w in region and w != (self.g.kx, self.g.ky):
                    t = self.trial()     # 0.9.4: unhurt?
                    e0 = t.g.energy
                    try:
                        t.go(lambda p: p == w)
                    except RuntimeError:
                        continue
                    if t.g.energy < e0:
                        continue
                    for inp in t.inputs:
                        self.frame(*inp)
                for _ in range(limit // 4):
                    if not self.g.live >> k & 1:
                        return
                    t = self.trial()
                    if t.strike(k, spot):
                        for inp in t.inputs:
                            self.frame(*inp)
                        return
                    if self.safe((self.g.kx, self.g.ky)):
                        self.wait(4)
                    else:
                        break
            raise RuntimeError(f"route: guard {k} of room {r} "
                               "never struck")
        finally:
            self.hunting = prev

    def hunt_all(self):
        """Kill the serpents of the room alive now (0.9.4: once
        each; one that comes back is the business of go)."""
        for k in self.biters():
            if self.g.live >> k & 1:
                self.hunt(k)

    def bitten(self, k, settle=2):
        """Stand in the path of guard k until it bites."""
        g = self.g
        s = dungeon.ROOMS[g.room]["guards"][k]
        e0 = g.energy
        prev, self.hunting = self.hunting, k
        try:
            self.go(lambda p: lines_meet(p[1], s["top"], 16) and
                    s["path"][0] + 8 <= p[0] <= s["path"][1] - 8)
        finally:
            self.hunting = prev
        self.wait_until(lambda g: g.energy < e0, limit=1200)
        self.wait(settle)

    # -------------------------------------------------------
    def wait_until(self, cond, swcha=NONE, limit=1500):
        for _ in range(limit):
            if cond(self.g):
                return
            self.frame(swcha)
        raise RuntimeError("route: it never happened")

    def touch(self, settle=2):
        """Walk to the thing of the room (dungeon.zone)."""
        z = dungeon.zone(self.g.room)
        self.go(lambda p: z[0][0] <= p[0] <= z[0][1] and
                z[1][0] <= p[1] <= z[1][1])
        self.wait(settle)

    def ways(self):
        """The ways out he can take now (a closed door shuts
        its way)."""
        g = self.g
        fr = free(g.room, not g.map_open)
        return sorted(w for w, n in dungeon.exits(g.room).items()
                      if n is not None and any(
                          WAY_GOAL[w](p) for p in fr))

    def leave(self, way, label=None, settle=2):
        """Out of the room by a way (east, west, south, north),
        into the next; a picture of it after `settle` frames."""
        self.go(WAY_GOAL[way])
        r = self.g.room
        for _ in range(200):
            if self.g.room != r:
                break
            self.frame(WAY_PUSH[way])
        else:
            raise RuntimeError(f"route: room {r} has no {way}")
        self.wait(settle)
        if label:
            n = self.g.room
            self.shot(f"room {n} {dungeon.ROOMS[n]['name']}, "
                      + label)

    def two(self, label):
        """Two frames running (the flicker)."""
        self.shot(label + ", one frame")
        self.frame()
        self.shot(label + ", the next frame")
        self.frame()


def route(tv):
    d = Director(tv, careful=True)
    d.wait(6)
    d.shot("title")
    d.wait(60)                  # the music of the title
    d.select()
    d.wait(2)
    d.shot("title, SOUND FX")
    d.wait(10)
    d.select()
    d.wait(2)
    d.shot("title, SILENT")
    d.wait(10)
    d.select()
    d.wait(2)
    d.shot("title, MUSIC again")
    d.wait(30)
    d.select()                  # the game in the SOUND FX mode
    d.wait(4)
    d.press()
    d.shot("start: the broken gate")
    d.wait(3)
    d.until_stuck(UP, "ky")
    d.wait(20, UP)              # nothing above the gate
    d.shot("the gate of Oakhaven: nothing above")
    # the walls and the sword in room 1 (the route of 0.2)
    d.go(lambda p: p == (20, 69))
    d.wait(20, RIGHT)
    d.shot("walking right")
    d.wait(10, RIGHT)
    d.press()
    d.wait(3)
    d.shot("thrust right")
    d.wait(12)
    d.until_stuck(UP, "ky")
    d.shot("up against a pillar")
    d.until(LEFT, lambda g: g.kx <= 44)
    d.until_stuck(UP, "ky")
    d.shot("up to the top wall")
    d.until_stuck(LEFT, "kx")
    d.shot("left to a pillar")
    d.press()
    d.wait(2)
    d.shot("thrust left")
    d.wait(12)
    d.wait(60, RIGHT & DOWN)
    d.shot("down and right, along the walls")
    d.frame(reset=True)
    d.shot("RESET")
    d.wait(2)
    # the edges of the screen, where the blade gets shorter
    d.go(lambda p: p[1] == 69)
    d.until(LEFT, lambda g: g.kx == 0)
    d.press()
    d.wait(2)
    d.shot("thrust left, the closest to the edge")
    d.wait(12)
    d.until(RIGHT, lambda g: g.kx >= 145)
    d.press()
    d.wait(2)
    d.shot("thrust right at the east edge")
    d.wait(12)
    d.until(RIGHT, lambda g: g.kx >= 148)
    d.press()
    d.wait(2)
    d.shot("thrust right, a shorter blade")
    d.wait(12)
    d.until(RIGHT, lambda g: g.kx == rules.X_MAX)
    d.press()
    d.wait(2)
    d.shot("thrust right at the last column")
    d.wait(12)
    # the game of the plan (0.5) and the serpents (0.6)
    d.leave("east", "a serpent in the corridor")
    # (0.9.2: the bite in the second game, sooner over: with
    # 12 units the first one keeps them for the King)
    # 0.9.4: the first blow wounds it, pushed to the end of its
    # path, stunned and blinking; the second kills it; in a
    # while it comes back, at the end farther from him
    d.hunt(0)
    d.wait(2)
    d.shot("room 2: the serpent killed, 100 points")
    d.back(0)
    d.wait(2)
    d.shot("room 2: the serpent back, at the end of its path "
           "farther from him")
    d.leave("east", "the grate closed, its serpent")
    d.touch()
    d.wait(20, DOWN)            # no key: the grate stays shut
    d.shot("room 3: no key, the grate stays shut")
    d.leave("west")
    d.leave("west")
    d.leave("west", "the seam: the chest above, the serpent "
            "below")
    d.wait(30)
    d.shot("room 0: the serpent below the seam crawls")
    d.go(lambda p: p == (5, 27))
    d.wait(2)
    d.shot("room 0: Sir Roderick across the seam, the chest "
           "open, the key, 500 points")
    d.press()
    d.wait(1)
    d.shot("room 0: a thrust over the plug, on the line of the "
           "comb")
    d.wait(12)
    # 0.9.4: the first blow wounds a serpent: pushed along its
    # path (here to its west end), stunned and blinking; the
    # second kills it
    d.wound_at_end(1, 8)
    d.wait(2)
    d.shot("room 0: the first blow: the serpent above pushed to "
           "the west end of its path, stunned, blinking")
    d.wound_at_end(0, None, at_end=False, hidden=True)
    d.shot("room 0: the first blow on the serpent below the seam: "
           "it blinks, hidden in this frame")
    d.hunt_all()
    d.wait(2)
    d.shot("room 0: the serpent below the seam killed")
    d.go(lambda p: p[1] == 69)
    d.until_stuck(LEFT, "kx")
    d.shot("room 0, the west plug stops him")
    d.leave("east")
    d.leave("east")
    # (0.9.2: the spikes too in the second game)
    d.leave("east")
    d.hunt_all()                # 0.7: his energy for the King
    d.go(lambda p: p[1] == 69)
    d.until_stuck(RIGHT, "kx")
    d.shot("room 3, the east plug stops him")
    d.touch()
    d.shot("room 3: the grate opens, 1000 points, the key used")
    d.leave("south", "down the stair")
    d.leave("north", "back up: the grate stays open")
    d.leave("south")
    d.leave("west", "level 2: two serpents, a seam")
    d.wound_at_end(1, 0)        # 0.9.4: to its east end
    d.wait(2)
    d.shot("room 6: the first blow: the serpent above pushed to "
           "the east end of its path")
    d.hunt_all()
    d.leave("west", "the torches, the grate of level 2")
    d.leave("west", "the chest and its guard")
    d.two("room 4: the chest and its guard take turns")
    d.hunt_all()
    d.touch()
    d.shot("room 4: the chest of level 2, its guard killed")
    d.leave("east")
    d.touch()
    d.shot("room 5: the grate of level 2 opens")
    d.leave("south", "down to level 3")
    d.leave("east", "the reeds: a seam low in the room")
    d.hunt_all()
    d.leave("east", "the cistern", settle=1)
    d.wait(8)
    d.two("room 11: the chest and its guard, the water")
    d.hunt_all()
    d.touch()
    d.shot("room 11: the chest of level 3")
    d.leave("west")
    d.leave("west")
    d.leave("west", "the grate of level 3, a serpent at the stair")
    d.hunt_all()
    d.touch()
    d.shot("room 8: the grate of level 3 opens")
    d.leave("south", "down to level 4")
    d.leave("east", "the hall of coils, its chest")
    d.two("room 13: the chest and its guard")
    d.leave("east", "the golden gate")
    d.two("room 14: the gate and a serpent take turns")
    d.touch()
    d.wait(20, RIGHT)           # no key: the gate stays shut
    d.shot("room 14: no key, the gate stays shut")
    d.leave("west")
    d.hunt_all()
    d.touch()
    d.shot("room 13: the chest of level 4")
    d.leave("east")
    d.touch()
    d.shot("room 14: the golden gate opens")
    d.leave("east", "the throne room: the Serpent King")
    throne_fight(d)
    # 0.8: SELECT to the MUSIC mode (SOUND FX, SILENT, MUSIC);
    # RESET on the title starts a game; RESET held starts one;
    # SELECT in a game does nothing
    d.select()
    d.wait(2)
    d.select()
    d.wait(2)
    d.shot("the title: MUSIC again")
    d.wait(20)
    d.frame(reset=True)
    d.wait(4)
    d.shot("RESET on the title: a new game, the theme")
    d.wait(40)
    for _ in range(20):
        d.frame(reset=True)
    d.wait(30)
    d.select()
    d.wait(4)
    d.shot("SELECT in the game: nothing")
    # a serpent killed (a score), then the bites of the next
    # room's until the energy is gone: GAME OVER, the lament
    # (0.9.2: first a bite in room 2, from the first game)
    d.leave("east")
    d.bitten(0)
    d.shot("room 2: bitten, 3 units, he flashes")
    d.frame()
    d.frame()
    d.shot("room 2: the flash, the other colours")
    d.hunt(0)               # (it chases him: away first)
    g = d.g
    xs, (y0, y1) = dungeon.plate_zones(g.room)
    d.go(lambda p: p[1] == y1 and p[0] == xs[0][0] - 12)
    d.wait_until(lambda g: g.pf_up)
    d.wait(2)
    d.shot("room 2: the spikes up")
    d.wait_until(lambda g: not g.pf_up and not g.hurt)
    d.go(lambda p: p[1] == y1 and xs[0][0] + 4 <= p[0] <= xs[0][1] - 4)
    e0 = d.g.energy
    d.wait_until(lambda g: g.energy == e0 - rules.SPIKE_DAMAGE)
    d.wait(2)
    d.shot("room 2: on the plate, hurt")      # 0.9.2: once
    d.until(LEFT, lambda g: not d.on_plate(g), stay=False)
    d.leave("east")
    start = die(d)
    d.wait(2)
    d.shot("GAME OVER, the lament")
    d.wait_until(lambda g: not g.screen)
    d.wait(2)
    d.shot("the GAME OVER screen: the crown, the Serpent King, the "
           "score")
    # the lament once, then silence; RESET: a new game
    d.wait(max(0, start + song_frames(d.tv, "gameover") + SILENCE
               - len(d.inputs)))
    d.shot("the GAME OVER screen: the lament over, silence")
    d.frame(reset=True)
    d.wait(4)
    d.shot("RESET on the GAME OVER screen: a new game, the theme")
    d.wait(30)
    # GAME OVER again (0.9: a serpent killed, an energy that is
    # not a multiple of the bite, with one wound of the spikes
    # if it is, then the bites: the last takes more than is
    # left and the energy stops at 0), the button back to the
    # title. 0.9.1: the way out of room 2 may cross a plate
    # that goes up; if the energy is a multiple of the bite in
    # room 3, back to room 2 and again
    d.leave("east")
    d.hunt(0)
    for _ in range(4):
        spikes_once(d)
        d.leave("east")
        if d.g.energy % rules.BITE_DAMAGE:
            break
        d.leave("west")
    else:
        raise RuntimeError("route: the energy a multiple of the "
                           "bite in room 3")
    die(d)
    d.wait_until(lambda g: g.over >= g.t["GO_FRAMES"] +
                 g.t["END_FRAMES"])
    d.wait(10)
    d.press()
    d.wait(3)
    d.shot("back to the title after GAME OVER, the theme")
    d.wait(30)
    return d


# the frames of silence the route and the songs wait for after
# a piece of the end
SILENCE = 60


def spikes_once(d):
    """An energy that is not a multiple of the bite (0.9: odd,
    with a bite of 2; 0.9.1: the bite takes 3), so that the
    last bite takes more than is left: if it is, on a plate of
    the room when it goes up, and off it after one wound."""
    if d.g.energy % rules.BITE_DAMAGE:
        return
    xs, (y0, y1) = dungeon.plate_zones(d.g.room)
    d.go(lambda p: p[1] == y1 and p[0] == xs[0][0] - 12)
    d.wait_until(lambda g: not g.pf_up and not g.hurt)
    d.go(lambda p: p[1] == y1 and
         xs[0][0] + 4 <= p[0] <= xs[0][1] - 4)
    e0 = d.g.energy
    d.wait_until(lambda g: g.energy < e0)
    if d.g.energy != e0 - rules.SPIKE_DAMAGE:
        raise RuntimeError("route: not one wound of the spikes")
    d.until(LEFT, lambda g: not d.on_plate(g), stay=False)
    if d.g.energy % rules.BITE_DAMAGE == 0:
        raise RuntimeError("route: the energy a multiple of the "
                           "bite")


def die(d):
    """Bitten by the serpents of the room until the energy is
    gone; the frame of GAME OVER."""
    while not d.g.over:
        k = d.biters()
        if not k:
            raise RuntimeError("route: nothing left to bite him")
        d.bitten(k[0], settle=0)
    return next(k for k in range(len(d.states), 0, -1)
                if not d.states[k - 1].over) + 1


def song_frames(tv, song, extra=0):
    """The frames of a song of the end (its steps, and `extra`
    steps more), from the score and the step of the
    television (sound_model.py)."""
    ev, _ = sound_model.voice_events(0, song)
    steps = sum(n for _, _, n in ev[:-1]) + extra   # (not the rest)
    pat = sound_model.steps_of(tv)
    return sum(pat[i % len(pat)] for i in range(steps))


LEFT_X, RIGHT_X = 58, 88        # where he fights the King
LOW_KY = 119                    # 0.9.2: low beside him
DODGE = (30, 33)                # where the venom flies to a
#                                 pillar if he steps down
CROWN_GOAL = (93, 100, 20, 28)  # where his blade (left) meets
#                                 the crown


def blows(d, label):
    """Strike the King from where he stands whenever a trial on
    the model says the blow lands and nothing hurts him; until
    the King is beaten. The first blow photographed (label)."""
    for _ in range(8000):
        g = d.g
        if g.crown:
            return
        t = d.trial()
        t.press()
        t.wait(g.t["THRUST_FRAMES"] + 2)
        if t.g.kh > g.kh and t.g.energy == g.energy:
            kh = g.kh
            d.press()
            if label:
                d.wait_until(lambda g: g.kh > kh)
                d.wait_until(lambda g: g.band_a["flash"])
                d.shot(label)
                label = None
        else:
            d.frame()
    raise RuntimeError("route: the King never beaten")


def thrust_wound(d, limit=2000):
    """Press the button when a trial on the model says the venom
    meets him in the thrust: a wound of VENOM_DAMAGE."""
    n = d.g.t["THRUST_FRAMES"]
    for _ in range(limit):
        e0 = d.g.energy
        t = d.trial()
        t.press()
        for _ in range(n - 1):
            if t.g.energy < e0:
                break
            t.frame()
        if t.g.energy == e0 - rules.VENOM_DAMAGE:
            d.press()
            d.wait_until(lambda g: g.energy < e0, limit=n)
            return
        d.frame()
    raise RuntimeError("route: the venom never met the thrust")


def throne_fight(d):
    """The throne room (0.7): the venom from behind, the shield
    on both sides, the King's bite, the King beaten, the crown,
    VICTORY, the button back to the title."""
    g = d.g
    if not dungeon.throne(g.room):
        raise RuntimeError("route: not in the throne room")
    # a few steps in, then facing west: the venom from behind
    d.until(RIGHT, lambda g: g.kx >= 24)
    d.frame(LEFT)
    d.wait_until(lambda g: g.vd)
    d.wait(1)
    d.shot("room 15: the King spits, the venom on the line of "
           "his mouth")
    d.wait(6)
    d.shot("room 15: the venom flies west")
    e0 = d.g.energy
    d.wait_until(lambda g: not g.vd)
    if d.g.energy != e0 - rules.VENOM_DAMAGE:
        raise RuntimeError("route: the venom from behind missed")
    d.wait(2)
    d.shot("room 15: the venom from behind, 3 units")
    # facing the King, west of him: the shield
    d.go(lambda p: p[0] == LEFT_X)
    if d.g.kdir != 0:
        d.frame(RIGHT)
    d.wait_until(lambda g: g.parry, limit=2000)
    d.wait(2)
    d.shot("room 15: the shield, the venom parried")
    d.wait_until(lambda g: not g.parry)
    # the next venom while he thrusts: no shield (a trial on
    # the model finds when to press)
    thrust_wound(d)
    d.wait(2)
    d.shot("room 15: the venom in the thrust, no shield, 3 units")
    d.wait_until(lambda g: not g.hurt, limit=200)
    # out of the venom's way: it breaks on a pillar
    x, ky = DODGE
    d.go(lambda p: p == (x, ky))
    d.wait_until(lambda g: g.vd, limit=2000)
    line = d.g.kt + dungeon.THRONE["mouth"]
    lo = dungeon.venom_span(d.g.kt)[0]
    e0 = d.g.energy
    d.until(DOWN, lambda g: g.ky > line + 1)
    d.wait_until(lambda g: not g.vd or g.vp <= lo + 2)
    d.shot("room 15: out of the venom's way, it breaks on a "
           "pillar")
    d.wait_until(lambda g: not g.vd)
    if d.g.energy != e0:
        raise RuntimeError("route: the venom was not dodged")
    # across the King's column: his bite
    e0 = d.g.energy
    d.until(RIGHT, lambda g: g.energy < e0, stay=True, limit=200)
    d.wait(2)
    d.shot("room 15: the King's bite, 3 units")
    d.go(lambda p: p[0] == RIGHT_X)
    if d.g.kdir != 8:
        d.frame(LEFT)
    d.wait_until(lambda g: g.parry, limit=2000)
    d.wait(2)
    d.shot("room 15: the shield, east of the King")
    d.wait_until(lambda g: not g.parry)
    # 0.9.2: low beside him, the blade on his coils: no blow
    # (the blade strikes only his head, where the venom flies;
    # down here the venom flies over him); then back
    here = (d.g.kx, d.g.ky)
    d.go(lambda p: p == (RIGHT_X, LOW_KY))
    if d.g.kdir != 8:
        d.frame(LEFT)
    d.wait_until(lambda g: g.kt == dungeon.THRONE["top"][1] and
                 not g.kf and not g.thrust)
    kh0, e0 = d.g.kh, d.g.energy
    d.press()
    d.wait(3)
    d.shot("room 15: the blade on the coils, low: no blow")
    d.wait(12)
    if d.g.kh != kh0 or d.g.energy != e0:
        raise RuntimeError("route: a blow on the coils, or a wound")
    d.go(lambda p: p == here)
    if d.g.kdir != 8:
        d.frame(LEFT)
    # the blows, from the east
    blows(d, "room 15: a blow, 500 points, the King flashes")
    d.wait(2)
    d.shot("room 15: the King beaten, the crown on the throne, "
           "5000 points")
    x0, x1, t0, t1 = CROWN_GOAL
    d.go(lambda p: x0 <= p[0] <= x1 and t0 <= p[1] <= t1)
    if d.g.kdir != 8:
        d.frame(LEFT)
    d.press()
    d.wait_until(lambda g: g.won, limit=20)
    d.wait(2)
    d.shot("VICTORY: the crown broken, 10000 points and 200 for "
           "each unit of energy")
    d.wait_until(lambda g: g.won >= g.t["VIC_FRAMES"] - 2)
    d.shot("VICTORY: everything stopped")
    # 0.8: the VICTORY screen; the button and SELECT too early
    d.wait_until(lambda g: not g.screen)
    d.wait(2)
    d.shot("the VICTORY screen: the crown broken, Sir Roderick, "
           "the score")
    d.press()
    d.wait(2)
    d.select()
    d.wait(2)
    d.shot("the VICTORY screen: the button and SELECT too early, "
           "nothing")
    d.wait_until(lambda g: g.won >= g.t["VIC_FRAMES"] +
                 g.t["END_FRAMES"])
    d.wait(5)
    d.select()                  # SELECT after the wait: nothing
    d.wait(5)
    d.press()
    d.wait(3)
    d.shot("back to the title after VICTORY, the theme")
    d.wait(30)


def noise(d, rnd, dirs):
    """Something at random in the room: the joystick held for a
    while (never through a way out), the button."""
    if rnd.random() < 0.3:
        d.press()
        return
    sw = rnd.choice(dirs)
    for _ in range(rnd.randint(1, 60)):
        if d.leaves(sw):
            break
        d.frame(sw)


DIRS = [NONE, RIGHT, LEFT, UP, DOWN, RIGHT & UP, RIGHT & DOWN,
        LEFT & UP, LEFT & DOWN]


def attack(d, rnd):
    """A try at a serpent of the room, at random: to a place
    where the blade can reach it, facing it, the button when
    it would die; it may bite first (no care, no trial)."""
    ks = d.biters()
    k = rnd.choice(ks) if ks else None
    spots = d.spots(k) if ks else None
    if not spots:
        noise(d, rnd, DIRS)
        return
    d.strike(k, rnd.choice(spots), wait_max=rnd.randint(30, 300))


def random_game(tv, frames=RANDOM_FRAMES, seed=2600, mode=0):
    """A game at random, in the sound mode `mode` (SELECT on
    the title). Mode 0: joystick and button at random, held
    for a while, walks out of the room by a way taken at
    random and to the thing of the room (it opens chests and
    doors where it can), RESET now and then. Mode 1: the game
    of the plan (tests/check_dungeon.walk_steps: every way out
    and every chest and door, down to the throne room) with
    things at random between the steps, and no care for the
    spikes or the serpents; then at random as in mode 0. Both
    go for the serpents now and then (attack: they kill some,
    and get bitten). When the game is over, the button goes
    back to the title and starts a new one (0.6)."""
    rnd = random.Random(seed)
    d = Director(tv)
    d.wait(3)
    for _ in range(mode):
        d.select()
        d.wait(1)
    d.press()

    def restart():
        """After GAME OVER: the end screen (0.8: the button
        pressed at random, often too early), then RESET or the
        button back to the title and a new game."""
        d.wait_until(lambda g: g.over >= g.t["GO_FRAMES"])
        d.wait(rnd.randint(1, 30))
        d.press()
        if d.g.over and rnd.random() < 0.3:
            d.wait(rnd.randint(1, 30))
            d.frame(reset=True)
            d.wait(2)
            return
        d.wait_until(lambda g: not g.over or g.over >=
                     g.t["GO_FRAMES"] + g.t["END_FRAMES"])
        if d.g.over:
            d.wait(rnd.randint(1, 30))
            d.press()
        d.wait(rnd.randint(2, 20))
        d.press()
        d.wait(2)
    if mode == 1:
        for _, what in check_dungeon.walk_steps()[1:]:
            while rnd.random() < 0.6 and not d.g.over:
                if rnd.random() < 0.25:
                    attack(d, rnd)
                else:
                    noise(d, rnd, DIRS)
            if d.g.over:
                break
            try:
                if what == "touch":
                    d.touch()
                else:
                    d.leave(what)
            except RuntimeError:
                if not d.g.over:
                    raise
                break
    while len(d.inputs) < frames:
        if d.g.over:
            restart()
            continue
        r = rnd.random()
        try:
            if r < 0.004:
                d.frame(reset=True)
            elif r < 0.5:
                noise(d, rnd, DIRS)
            elif r < 0.65:
                attack(d, rnd)
            elif r < 0.85 or not dungeon.zone(d.g.room):
                d.leave(rnd.choice(d.ways()))
            else:
                d.touch()           # the chest or the door
        except RuntimeError:
            if not d.g.over:
                raise
    return d


# ---------------------------------------------------------
# A2. the songs (0.8)

def end_now(d, kind, score):
    """The end of a game, as the game makes it, put in after
    the logic of this frame (model and cartridge): the count at
    its end (the end screen from the next frame), the song
    started, its effect asked for, a score."""
    t = d.g.t
    if kind == "victory":
        poke = dict(won=t["VIC_FRAMES"], song=model.SONG_VICTORY,
                    request=model.VICTORY)
    else:
        poke = dict(over=t["GO_FRAMES"], song=model.SONG_GAMEOVER,
                    request=model.GAMEOVER)
    d.frame(poke=dict(poke, restart=True, score=score))


def to_title(d):
    """From an end screen: its count over, the button."""
    d.wait_until(lambda g: (g.won or g.over) >= (
        g.t["VIC_FRAMES"] if g.won else g.t["GO_FRAMES"]) +
        g.t["END_FRAMES"])
    d.wait(3)
    d.press()
    d.wait(20)


def songs(tv):
    """The two ends in the three modes (the laboratory of 0.8):
    MUSIC, the fanfare and the lament to their end, then
    silence (the lament's past the loop of its rest), back by
    the button and by RESET; SOUND FX, their effects; SILENT."""
    d = Director(tv)
    d.wait(3)
    d.press()                   # MUSIC: a game
    d.wait(30)
    end_now(d, "victory", 31200)
    d.wait(song_frames(tv, "victory") + SILENCE)
    to_title(d)
    d.press()
    d.wait(30)
    end_now(d, "gameover", 4500)
    d.wait(song_frames(tv, "gameover", 255 + 16) + SILENCE)
    d.frame(reset=True)         # RESET: a new game, the theme
    d.wait(60)
    end_now(d, "gameover", 900)
    to_title(d)
    d.select()                  # SOUND FX
    d.wait(4)
    d.press()
    d.wait(30)
    end_now(d, "victory", 10000)
    d.wait(len(sound_model.tables(tv)["fx"][model.VICTORY - 1])
           + SILENCE)
    to_title(d)
    d.press()
    d.wait(30)
    end_now(d, "gameover", 0)
    d.wait(len(sound_model.tables(tv)["fx"][model.GAMEOVER - 1])
           + SILENCE)
    d.frame(reset=True)
    d.wait(30)
    end_now(d, "gameover", 300)
    to_title(d)
    d.select()                  # SILENT
    d.wait(4)
    d.press()
    d.wait(30)
    end_now(d, "victory", 999999)
    d.wait(SILENCE)
    to_title(d)
    d.select()                  # MUSIC again
    d.wait(60)
    return d


def sound_facts(d, audio):
    """The songs started and the silence (0.8), from the sound
    registers of the cartridge (audio: after each frame, from
    the simulator) and the model's states: for every song
    started, why (an end, RESET in a game or on an end screen,
    a new game from the title, the button back to the title),
    the mode; for each end, the frames of its sound (the last
    with a volume) against its length (the piece of the score
    in MUSIC, the effect in SOUND FX, none in SILENT) and the
    frames of silence after it until the next start; for each
    theme started in MUSIC, its first notes."""
    t = sound_model.tables(d.tv)
    first = [t["events"][v][0][0][1] for v in (0, 1)]
    starts = [k for k, g in enumerate(d.states, 1) if g.started]
    out, ok = [], True
    for i, k in enumerate(starts):
        g, b = d.states[k - 1], d.states[k - 2]
        name = model_song(g.song)
        if name != "theme":
            why = name
        elif b.screen and g.screen:
            why = "RESET in a game"
        elif not b.screen and (b.over or b.won):
            why = "RESET on an end screen" if g.screen else \
                "the button: the title"
        else:
            why = "a game from the title"
        end = starts[i + 1] if i + 1 < len(starts) else \
            len(d.states) + 1
        f = dict(frame=k, song=name, why=why, mode=g.mode,
                 frames=end - k)
        if name == "theme":
            if g.mode == 0:
                a = audio[k]
                f["first_notes"] = [(a["C0"], a["F0"]),
                                    (a["C1"], a["F1"])]
                f["ok"] = f["first_notes"] == first and \
                    a["V0"] > 0 and a["V1"] > 0
        else:
            last = max([j for j in range(k, end)
                        if audio[j]["V0"] or audio[j]["V1"]],
                       default=k - 1)
            if g.mode == 0:
                want = song_frames(d.tv, name)
            elif g.mode == 1:
                fx = model.VICTORY if name == "victory" else \
                    model.GAMEOVER
                want = len(t["fx"][fx - 1])
            else:
                want = 0
            f.update(sound=last - k + 1, length=want,
                     silence=end - 1 - last, cut=end - k <= want)
            if f["cut"]:            # the next start came first
                f["ok"] = f["sound"] >= 1
            elif g.mode == 0:       # the piece, then silence
                f["ok"] = want - 2 <= f["sound"] <= want
            else:                   # the effect, or nothing
                f["ok"] = f["sound"] <= want and (
                    want == 0 or f["sound"] >= 1)
        ok &= f.get("ok", True)
        out.append(f)
    return dict(starts=out, passed=ok)


def wav(audio, tv, name):
    """The sound of a run, made by the model of the TIA from the
    registers of the simulator: to listen to."""
    fr = [(a["C0"], a["F0"], a["V0"], a["C1"], a["F1"], a["V1"])
          for a in audio[1:]]
    smp, rate = tia_audio.render(fr, tv)
    tia_audio.to_wav(smp, rate, os.path.join(EVID, name))


def ends_pass(ends):
    """The route's end screens: one VICTORY and two GAME OVER,
    the button and SELECT pressed too early on one, left by
    the button and by RESET."""
    kinds = [e["kind"] for e in ends]
    by = {e["left_by"] for e in ends}
    return kinds == ["victory", "gameover", "gameover"] and \
        by == {"RESET", "the button"} and \
        any(e["ignored_button"] and e["ignored_select"]
            for e in ends)


def songs_pass(sf, tv):
    """The songs test: each end in each mode, played to its end
    (not cut), and the lament in MUSIC followed by more
    silence than its rest of 255 steps lasts."""
    seen = {(f["song"], f["mode"]) for f in sf["starts"]
            if not f.get("cut")}
    want = {(k, m) for k in ("victory", "gameover")
            for m in (0, 1, 2)} - {("gameover", 2)}
    rest = song_frames(tv, "gameover", 255) - \
        song_frames(tv, "gameover")
    long = [f for f in sf["starts"] if f["song"] == "gameover" and
            f["mode"] == 0 and f["silence"] > rest]
    return want <= seen and bool(long)


def model_song(song):
    return {model.SONG_THEME: "theme",
            model.SONG_GAMEOVER: "gameover",
            model.SONG_VICTORY: "victory"}[song]


def end_facts(d):
    """The end screens on the route (0.8), from the model's
    states: for each, its kind, its first frame, how many
    frames, the score shown, the button and SELECT pressed
    while it waited (nothing), how it was left (the button:
    the title; RESET: a game)."""
    out, cur = [], None
    for k, g in enumerate(d.states, 1):
        p = g.pic
        kind = p.get("end") if not p["screen"] else None
        if cur and kind != cur["kind"]:
            cur["left_by"] = "RESET" if g.screen else "the button"
            out.append(cur)
            cur = None
        if kind and not cur:
            cur = dict(kind=kind, first_frame=k, frames=0,
                       score=p["score"], ignored_button=0,
                       ignored_select=0)
        if cur:
            cur["frames"] += 1
            _, fire, _, sel = d.inputs[k - 1]
            if fire and not d.inputs[k - 2][1]:
                cur["ignored_button"] += 1
            if sel and not d.inputs[k - 2][3]:
                cur["ignored_select"] += 1
    if cur:
        out.append(cur)
    return out


# ---------------------------------------------------------
# B. the simulator

def symbols(tv):
    return read_symbols(os.path.join(BUILD, f"scalecrown_{tv}.sym"))


class _Stop(Exception):
    """The simulator stops at the first difference from the
    model (the checks of a mutation)."""


def simulate(tv, start_bank, seed, inputs, pokes=None, model=None,
             quick=False):
    rom = open(os.path.join(BUILD, f"scalecrown_{tv}.bin"),
               "rb").read()
    sym = symbols(tv)
    vcs = VCS(rom, start_bank=start_bank, ram_seed=seed)
    ram, vb_left, audio, sc = [], {}, [], []
    snd_start, snd_cost, over_left = {}, {}, {}
    th_start, th_cost = {}, {}
    su_start, su_cost, cp_start, cp_cost = {}, {}, {}, {}
    sp_min = [0xFF]
    count = [0]
    aud = dict(C0=0, F0=0, V0=0, C1=0, F1=0, V1=0)
    seen = [0]

    def at_frame(v):            # the inputs of frame k
        count[0] += 1
        k = count[0]
        sw, fire, reset, sel = inputs[k - 1] if k <= len(inputs) \
            else OFF
        v.swcha = sw
        v.fire0 = fire
        v.swchb = 0x0B & ~(1 if reset else 0) & ~(2 if sel else 0)

    def at_main(v):             # RAM and sound at a frame's end
        ram.append(bytes(v.ram))
        sc.append(bytes(v.sc_ram))
        log = v.tia_log
        for i in range(seen[0], len(log)):
            if log[i][1] in AUDIO:
                aud[AUDIO[log[i][1]]] = log[i][2]
        seen[0] = len(log)
        audio.append(dict(aud))
        k = len(ram) - 1
        if model is not None and 1 <= k <= len(model.states):
            g = model.states[k - 1]
            for name, want in list(g.state().items()) + [
                    ("AUD" + a, w) for a, w in g.audio.items()]:
                base, _, off = name.partition("+")
                got = audio[k][name[3:]] if base.startswith("AUD") \
                    else sc[k][int(off)] if base == "SC" else \
                    ram[k][sym[base] - 0x80 + int(off or 0)]
                if got != want:
                    early.append(dict(frame=k, var=name, model=want,
                                      ram=got))
                    raise _Stop()
        digest()

    def at_leaf(v):             # the deepest calls: the stack
        sp_min[0] = min(sp_min[0], v.mpu.sp)

    def at_kernel_done(v):      # the things (bank 4) start
        th_start[count[0]] = v.cycle

    def at_kd_sound(v):         # the sound player starts
        k = count[0]
        snd_start[k] = v.cycle
        if k in th_start and v.ram[sym["screen"] - 0x80]:
            th_cost[k] = v.cycle - th_start[k]

    def at_over_wait(v):        # and has finished
        k = count[0]
        if k not in snd_cost and k in snd_start:
            snd_cost[k] = v.cycle - snd_start[k]
            over_left[k] = v.intim()

    def at_vb_end(v):           # the first time in a frame
        vb_left.setdefault(count[0], v.intim())

    def at_vb_wait(v):          # 0.8: the same on the title
        title_vb.setdefault(count[0], v.intim())

    def at_fe_wait(v):          # and on the end screens
        end_vb.setdefault(count[0], v.intim())

    def at_setup(v):            # setting the room up: from
        su_start[count[0]] = v.cycle    # setup_room

    def at_room_state(v):       # to room_state (when it set
        k = count[0]            # a room up)
        if k in su_start and v.cycle - su_start[k] > 40:
            su_cost[k] = v.cycle - su_start[k]

    def at_copy(v):             # the copy: from the jsr TO_COPY
        cp_start[count[0]] = v.cycle

    def at_copied(v):           # back in bank 7
        k = count[0]
        if k in cp_start:
            cp_cost[k] = v.cycle - cp_start[k]

    kz = {}

    def at_room_kernel(v):      # the count of the seam drawn
        if v.bank == 0 and "zcoarse" in sym:
            kz[count[0]] = v.ram[sym["zcoarse"] - 0x80]

    def at_fr_room(v):          # D: values after the logic
        p = pokes[count[0] - 1] if count[0] <= len(pokes) else {}
        for name, val in p.items():
            base, _, off = name.partition("+")
            if base == "SC":
                v.sc_ram[int(off)] = val
            else:
                v.ram[sym[base] - 0x80 + int(off or 0)] = val
    def brk(name, fn, off=0):   # (a step of the chain may not
        if name in sym:         # have the label yet)
            vcs.breaks[sym[name] + off] = fn
    brk("frame_ready", at_frame)
    brk("room_kernel", at_room_kernel)
    brk("main", at_main)
    brk("vb_end", at_vb_end)
    brk("vb_wait", at_vb_wait)
    brk("fe_wait", at_fe_wait)
    title_vb, end_vb = {}, {}
    brk("kernel_done", at_kernel_done)
    brk("kd_sound", at_kd_sound)
    for leaf in ("wall", "fetch", "place", "dig_ptr", "room_copy",
                 "put"):
        brk(leaf, at_leaf)
    brk("over_wait", at_over_wait)
    brk("setup_room", at_setup)
    brk("room_state", at_room_state)
    brk("su_copied", at_copy, -3)
    brk("su_copied", at_copied)
    if pokes:
        brk("fr_room", at_fr_room)
    n = len(pokes) if pokes else len(inputs)
    early = []
    t = TV[tv]
    starts = vcs.frame_starts
    bad, idle = [], {}
    regs = {}
    seam = {}                   # frame -> writes of the seam
    log = vcs.tia_log
    pos = [1, 0]                # next frame to look at, its write
    stopped = []                # quick: the frame it stopped at

    def digest():
        """The writes to the TIA of the frames that have ended:
        windows, idle cycles, the seam; then they are forgotten
        (a route of 12 000 frames would keep 30 million of
        them, gigabytes). Called at the end of every frame and
        once after the run."""
        f, i = pos
        # the screen frame f drew: the RAM after the frame
        # (ram[k] is the RAM when frame k+1 begins); a frame
        # that never ends (a program gone astray) stops here
        try:
            while f + 1 < len(starts) and f + 1 < len(ram):
                i = look(f, i)
                f += 1
                if quick:
                    halt(f - 1)
        finally:
            del log[:i]
            seen[0] = max(0, seen[0] - i)
            pos[0], pos[1] = f, 0

    def halt(f):
        """Quick (the mutations): stop at the first frame with
        the wrong number of lines, a write out of its window or
        the seam wrong (the checks after the run say which)."""
        lines = starts[f + 1] // LINE - starts[f] // LINE
        r = ram[f + 1]
        if lines != t["lines"] or bad or not seam_frame(
                f, r, seam.get(f, []), kz, sym, True)[2]:
            stopped.append(f)
            raise _Stop()

    def look(f, i):
        scr = ram[f + 1][sym["screen"] - 0x80]
        ekind = end_kind(ram[f + 1], sym) if not scr else None
        base = (starts[f] // LINE) * LINE
        end = (starts[f + 1] // LINE) * LINE
        while i < len(log) and log[i][0] < base:
            i += 1
        while i < len(log) and log[i][0] < end:
            cyc, reg, val = log[i]
            i += 1
            line, c = divmod(cyc - base, LINE)
            v = line - t["vis0"] - t["top"]
            if reg in SEAM_REGS and scr and 32 <= v < 192:
                seam.setdefault(f, []).append(
                    (SEAM_REGS[reg], v - 32, c))
            if reg == WSYNC:
                kind = line_kind(scr, v, ekind)
                if kind:
                    idle.setdefault(kind, set()).add(75 - c)
                continue
            changed = regs.get(reg) != val
            regs[reg] = val
            if not changed or reg not in WIN:
                continue
            wins = None
            if scr and 32 <= v < 192:
                wins = WIN[reg]
            elif not scr and decor_line(v, ekind) and \
                    reg not in (GRP0, GRP1):
                wins = WIN[reg]         # both players delayed
            elif not scr and scene_line(v) and reg in SCENE_WIN:
                wins = (END_SCENE_WIN[ekind] if ekind else
                        SCENE_WIN)[reg]
            if wins and not any(a <= c <= b for a, b in wins):
                bad.append(dict(frame=f, line=v, reg=NAMES[reg],
                                cycle=c))
        return i
    try:
        vcs.run_frames(n + 2)
    except _Stop:
        pass
    try:
        digest()
    except _Stop:
        pass
    game_vb = list(vb_left.values())
    change_vb = [vb_left[k] for k in su_cost if k in vb_left]
    return dict(frames_wanted=n, frames_ended=len(ram) - 1,
                stopped=stopped[:1],
                lines=sorted(set(vcs.lines_per_frame())),
                vsync=sorted(set(vcs.vsync_cycles)),
                sc_bad=len(vcs.sc_bad_reads),
                window_errors=bad[:10],
                window_error_count=len(bad),
                idle={k: [min(v), max(v)]
                      for k, v in sorted(idle.items())},
                vblank_left_min=min(game_vb) if game_vb else None,
                title_vblank_left_min=min(title_vb.values())
                if title_vb else None,
                end_vblank_left_min=min(end_vb.values())
                if end_vb else None,
                end_frames=len(end_vb),
                sound_cycles=[min(snd_cost.values()),
                              max(snd_cost.values())]
                if snd_cost else None,
                things_cycles=[min(th_cost.values()),
                               max(th_cost.values())]
                if th_cost else None,
                overscan_left_min=min(over_left.values())
                if over_left else None,
                stack_lowest=sp_min[0] + 1,   # lowest byte used
                room_changes=len(su_cost),
                setup_cycles=[min(su_cost.values()),
                              max(su_cost.values())]
                if su_cost else None,
                copy_cycles=[min(cp_cost.values()),
                             max(cp_cost.values())]
                if cp_cost else None,
                change_vblank_left=min(change_vb)
                if change_vb else None,
                seam=seam_check(seam, ram, kz, sym),
                early=early,
                ram=ram, sc=sc, audio=audio, sym=sym,
                executed=vcs.executed, rom_reads=vcs.rom_reads)


# the duel of the title: a write must land before the beam
# reaches the figure (first pixel x: cycle (68 + x) / 3 - 2)
SCENE_WIN = {
    GRP0: [(0, (68 + look.SCENE_KNIGHT["x"] + 3) // 3 - 2)],
    COLUP0: [(0, (68 + look.SCENE_KNIGHT["x"] + 3) // 3 - 2)],
    GRP1: [(0, (68 + look.SCENE_KING["x"] + 4) // 3 - 2)],
    COLUP1: [(0, (68 + look.SCENE_KING["x"] + 4) // 3 - 2)]}


def _scene_win(sc):
    """The windows of the scene of an end screen (0.8): its
    players as SCENE_WIN; a player that is not there, the whole
    line."""
    out = {}
    for key, g, c, off in (("p0", GRP0, COLUP0, H_OFFSET),
                           ("p1", GRP1, COLUP1, DOUBLE_OFFSET)):
        fig = sc[key]
        last = 75 if not fig else (68 + fig["x"] + (
            off if fig.get("nus") else H_OFFSET)) // 3 - 2
        out[g] = out[c] = [(0, last)]
    return out


END_SCENE_WIN = {k: _scene_win(look.END_SCENES[k])
                 for k in look.END_KINDS}


def end_kind(ram, sym):
    """The end screen the RAM shows (0.8): "victory" (won),
    "gameover" (over), or None (the title)."""
    if ram[sym["won"] - 0x80]:
        return "victory"
    return "gameover" if ram[sym["over"] - 0x80] else None


def scene_line(v):
    return look.TITLE_SETUP <= v < look.TITLE_SCENE + look.SCENE_H


def decor_line(v, end=None):
    """A line of the title (0.8: or of an end screen) drawn by
    the decor loop."""
    if not 4 <= v < look.TITLE_LINES or scene_line(v):
        return False
    if end:
        for name, top in look.END_BLOCKS[end]:
            if top <= v < top + len(look.end_block_lines(name)):
                return False
        return True
    for name, top in look.TITLE_BLOCKS:
        if top <= v < top + len(look.title_block_lines(name)):
            return False
    return True


def line_kind(scr, v, end=None):
    if not scr:
        if end:
            return "end decor" if decor_line(v, end) else None
        return "title decor" if decor_line(v) else None
    if 26 <= v < 32:
        return f"HUD {v}"
    r = v - look.HUD_LINES
    if not 0 <= r < 160:
        return None
    kind = ("A" if r % 2 == 0 else "B") + str((r % 8) // 2)
    # 0.7: the lines of the throne kernel apart
    return "T " + kind if STEP >= 6 and dungeon.throne(scr - 1) \
        else kind


# the writes of the seam (0.6)
SEAM_REGS = {0x0C: "REFP1", 0x11: "RESP1", 0x2A: "HMOVE"}


def seam_check(log, ram, kz, sym):
    """In every frame drawn in a room with a seam (course c):
    REFP1 in line A2 (8c + 4) after the cycle 55, RESP1 in A3
    (8c + 6) at the cycle 19 + 5 x zcoarse, HMOVE at the cycle
    2 of B3 (8c + 7); in the other rooms none of them. The
    rooms of the frames from the RAM after them, the counts
    from the RAM when the kernel starts (kz)."""
    bad, n, cols = [], 0, set()
    for f in range(1, len(ram) - 1):
        r = ram[f + 1]
        if not r[sym["screen"] - 0x80]:
            continue
        room, want, ok, zc = seam_frame(f, r, log.get(f, []), kz, sym)
        if want:
            n += 1
            cols.add(zc)
        if not ok:
            bad.append(dict(frame=f, room=room, want=want,
                            got=log.get(f, [])))
    return dict(frames=n, wrong=len(bad), first=bad[:3],
                counts=sorted(cols))


def seam_frame(f, r, got, kz, sym, early=False):
    """The seam of frame f, drawn with the RAM r after it, its
    writes got: (room, the writes wanted, right, zcoarse).
    Early (during the run) a count not known yet is right: the
    check after the run decides."""
    room = r[sym["room"] - 0x80]
    if not r[sym["screen"] - 0x80]:
        return room, [], True, None
    if room >= len(dungeon.ROOMS):      # (a mutant's RAM)
        return room, [("a room", None, None)], False, None
    c = dungeon.seam(room) if STEP >= 5 else None    # (the chain)
    if c is None:
        return room, [], not got, None
    if early and f + 1 not in kz:
        return room, [], True, None
    zc = kz.get(f + 1, -1)      # (log frame f: game frame f + 1)
    want = [("REFP1", 8 * c + 4, None),
            ("RESP1", 8 * c + 6, 19 + 5 * zc),
            ("HMOVE", 8 * c + 7, 2)]
    ok = len(got) == len(want) and all(
        g[0] == w[0] and g[1] == w[1] and (
            55 <= g[2] <= 60 if w[2] is None else g[2] == w[2])
        for g, w in zip(got, want))
    return room, want, ok, zc


def compare_model(d, sim, n=None):
    """The state of the model and the RAM, and the sound
    registers, after each frame (the first n)."""
    sym = sim["sym"]
    diffs = []
    for k, g in enumerate(d.states[:n], 1):
        if k >= len(sim["ram"]):
            diffs.append(dict(frame=k, var="the frame never ended",
                              model="", ram=""))
            break
        ram = sim["ram"][k]
        for name, want in g.state().items():
            base, _, off = name.partition("+")
            got = sim["sc"][k][int(off)] if base == "SC" else \
                ram[sym[base] - 0x80 + int(off or 0)]
            if got != want:
                diffs.append(dict(frame=k, var=name, model=want,
                                  ram=got))
        for name, want in g.audio.items():
            got = sim["audio"][k][name]
            if got != want:
                diffs.append(dict(frame=k, var="AUD" + name,
                                  model=want, ram=got))
    return diffs


def sim_checks(tv, s):
    t = TV[tv]
    why = []
    if s["frames_ended"] < s["frames_wanted"] and \
            not s.get("stopped"):
        why.append(f"only {s['frames_ended']} of "
                   f"{s['frames_wanted']} frames ended")
    if s["lines"] != [t["lines"]]:
        why.append(f"lines {s['lines']}")
    if s["vsync"] != [228]:
        why.append(f"VSYNC {s['vsync']}")
    if s["sc_bad"]:
        why.append(f"{s['sc_bad']} reads of the SC write side")
    if s["window_error_count"]:
        e = s["window_errors"][0]
        why.append(f"{s['window_error_count']} writes out of "
                   f"window ({e['reg']} at {e['cycle']}, line "
                   f"{e['line']}, frame {e['frame']})")
    for k, what in (("vblank_left_min", ""), (
            "title_vblank_left_min", " on the title"), (
            "end_vblank_left_min", " on an end screen")):
        if s[k] is not None and not 0 < s[k] < 0x80:
            why.append(f"VBLANK overrun{what} ({s[k]})")
    if s["overscan_left_min"] is not None and \
            not 0 < s["overscan_left_min"] < 0x80:
        why.append(f"overscan overrun ({s['overscan_left_min']})")
    if s["seam"]["wrong"]:
        e = s["seam"]["first"][0]
        why.append(f"{s['seam']['wrong']} frames with the seam "
                   f"wrong (frame {e['frame']}, room {e['room']}: "
                   f"{e['got']} for {e['want']})")
    return why


# ---------------------------------------------------------
# D. the extremes

def extremes():
    """Frames of values put in the RAM (and the Superchip RAM:
    "SC+n") after the logic."""
    p = []
    for kdir in (0, 8):
        for kx in range(rules.X_MAX + 1):
            p.append(dict(kx=kx, kdir=kdir, ky=69, kpose=3))
    # 0.6: in rooms with a seam, Sir Roderick at every height
    # in every pose (through the lines of the seam), the guard
    # below in every column, both ways, alive and dead
    for r in (0, 14):
        p.append(dict(room=r, screen=r + 1, kx=60, ky=69,
                      energy=16, hurt=0, over=0))
        p += [{}] * 3
        for kpose in range(len(POSES)):
            for ky in range(rules.TOP_MIN, rules.TOP_MAX + 1, 2):
                p.append(dict(kx=5 + (ky * 7) % 140,
                              kdir=8 * (ky % 4 == 1), ky=ky,
                              kpose=kpose, energy=16, hurt=0))
        for live in (3, 2):
            for sd in (0, 8):
                for x in range(3, rules.X_MAX + 1):
                    q, m = divmod(x - 3, 15)
                    p.append({"SC+60": x, "SC+62": sd,
                              "SC+64": live, "zcoarse": q + 1,
                              "SC+66": ((m - 15) & 0xFF ^ 7) << 4
                              & 0xFF, "energy": 16, "hurt": 0,
                              "kx": 60, "ky": 17})
    # player 1 above in every column (0.9.2: room 2 has two
    # guards and a seam now, as every room with serpents: the
    # second guard, above the seam, alone; the first, below,
    # never left of column 3, every column in rooms 0 and 14)
    p.append(dict(room=2, screen=3, kx=60, ky=69, energy=16,
                  over=0))
    p += [{}] * 3
    for x in range(rules.X_MAX + 1):
        p.append({"SC+61": x, "SC+63": 8, "SC+64": 2,
                  "energy": 16, "hurt": 0, "kx": 60, "ky": 69})
    for r in range(len(dungeon.ROOMS)):     # every room
        p.append(dict(room=r, screen=r + 1, kx=60, ky=69,
                      energy=16, over=0))
        p += [{}] * 15
    for r in range(len(dungeon.ROOMS)):     # all open, a key
        p.append(dict(room=r, screen=r + 1, kx=60, ky=69,
                      opened=0xFF, key=r // 4 + 1, energy=16,
                      over=0))
        p += [{}] * 15
    return p + throne_extremes()


END_SCORES = (0, 999999, 102030, 888888)


def end_extremes(tv):
    """0.8, the end screens: each kind with each score of
    END_SCORES. A RESET first (a new game: the frames before
    may have left one going to its end); then for each: in a
    game, the count of the end at its end and the score put in
    after the logic (the end screen from the next frame),
    three frames of it, RESET, a frame of the game. Returns
    the inputs and the values for each frame."""
    rs = (NONE, False, True, False)
    inputs, pokes = [rs, OFF], [{}, {}]
    for kind in look.END_KINDS:
        for sc in END_SCORES:
            t = rules.table(tv)
            p = sim_poke(dict(score=sc))
            if kind == "victory":
                p["won"] = t["VIC_FRAMES"]
            else:
                p["over"] = t["GO_FRAMES"]
            inputs += [OFF] * 4 + [rs, OFF]
            pokes += [p] + [{}] * 5
    return inputs, pokes


def throne_extremes():
    """0.7, the throne room (its kernel in bank 2): Sir Roderick
    in every column in the thrust, facing both ways, and at
    every height in every pose; the King at every top line,
    plain, spitting (the venom beside his mouth), flashing, in
    both frames, facing both ways; the venom at every pixel it
    can have, the King high, in the middle and low; the crown
    and its pieces (VICTORY)."""
    th = dungeon.THRONE
    keep = dict(energy=16, hurt=0, parry=0, over=0, won=0)
    p = [dict(room=th["room"], screen=th["room"] + 1, kx=20, ky=69,
              **keep, **{"SC+74": 0})]
    p += [{}] * 3
    for kdir in (0, 8):
        for kx in range(rules.X_MAX + 1):
            p.append(dict(kx=kx, kdir=kdir, ky=69, kpose=3, **keep))
    for kpose in range(len(POSES)):
        for ky in range(rules.TOP_MIN, rules.TOP_MAX + 1, 2):
            p.append(dict(kx=5 + (ky * 7) % 140, kdir=8 * (ky % 4 == 1),
                          ky=ky, kpose=kpose, **keep))
    t0, t1 = th["top"]
    # (vd, kf, frames): plain, spitting, flashing, both; frames
    # 0/16 the King's frame a or b, 4/20 the flash on
    looks = ((0, 0, 0), (1, 0, 16), (0, 1, 4), (2, 1, 20),
             (0, 0, 16), (2, 0, 0), (0, 1, 20), (1, 1, 4))
    for top in range(t0, t1 + 1, 2):
        lo, hi = dungeon.venom_span(top)
        for k, (vd, kf, frames) in enumerate(looks):
            p.append({"kx": 20 if k % 2 else 120, "ky": 69,
                      "kpose": 0, "frames": frames, **keep,
                      "SC+67": top, "SC+69": kf, "SC+72": vd,
                      "SC+71": dungeon.venom_start(vd == 1),
                      "SC+68": 0, "SC+70": 200, "SC+74": 0})
    for top in (t0, (t0 + t1) // 2 | 1, t1):
        lo, hi = dungeon.venom_span(top)
        for vp in range(lo, hi - 6):
            p.append({"kx": 20 if vp % 2 else 120, "ky": 69,
                      "kpose": 0, **keep, "SC+67": top, "SC+69": 0,
                      "SC+72": 1 + vp % 2, "SC+71": vp, "SC+70": 200,
                      "SC+74": 0})
    for crown, won in ((1, 0), (2, 1)):
        for f in range(16):
            p.append({"kx": 96, "ky": 23, "kpose": 0, **keep,
                      "won": won, "SC+74": crown, "SC+72": 0})
    return p


# ---------------------------------------------------------
# E. the expected pictures

def figure_pixels(pic, name, x, top, mirror, wide, colours,
                  first_line, window=(0, 159)):
    """Draw a figure; its top line is room line `top`; only on
    the room lines of the window (0.6: its band). wide: False
    or 1, True or 2 (twice as wide), 4 (0.7: four times)."""
    f = 2 if wide is True else (wide or 1)
    lines = look.figure_lines(name)
    for j, (bits, _) in enumerate(lines):
        if not window[0] <= top + j <= window[1]:
            continue
        y = first_line + top + j
        for i in range(8):
            b = 7 - i if mirror else i
            if bits & (0x80 >> b):
                for w in range(f):
                    xx = (x + f * i + w) % 160
                    pic[y][xx] = colours[j]


def expected(tv, g):
    """The picture (visible lines x 160 TIA values) of what the
    model's frame showed (g.pic: the state after the logic of
    the VBLANK, before the things of the overscan)."""
    t = TV[tv]
    p = g.pic
    pic = [[0] * 160 for _ in range(t["visn"])]
    top = t["top"]
    if p["screen"] == 0:
        x0 = 52 + BLOCK_OFFSET                  # TITLE_X
        rows = look.end_picture(p["end"], tv, x0, p["score"]) \
            if p.get("end") else look.title_picture(tv, x0,
                                                    p["mode"])
        for i, row in enumerate(rows):
            pic[top + i] = row
        return pic
    r = p["room"]
    room = dungeon.ROOMS[r]
    frames = p["frames"]
    if STEP >= 3:               # (the chain: the HUD from step 3)
        hud(pic, p, room, tv, top)
    room_and_figures(pic, p, r, room, frames, tv, top)
    return pic


def hud(pic, p, room, tv, top):
    """The HUD: six digits, energy bar, LEVEL n and the key."""
    x0 = 51 + BLOCK_OFFSET                      # SCORE_X
    col = look.tv_colour(look.HUD_SCORE_COLOUR, tv)
    for d, ch in enumerate(f"{p['score']:06d}"):
        for j, row in enumerate(art.DIGITS[int(ch)]):
            for i, c in enumerate(row):
                if c == "#":
                    pic[top + look.HUD_DIGITS + j][x0 + 8 * d + i] \
                        = col
    col = look.tv_colour(look.HUD_TEXT_COLOUR, tv)
    text = look.victory_rows() if p["won"] else \
        look.game_over_rows() if p["over"] else \
        look.hud_text_rows(room["level"], bool(p["key"]))
    for j, row in enumerate(text):
        for i, c in enumerate(row):
            if c == "#":
                pic[top + look.HUD_TEXT + j][x0 + i] = col
    for j, c in enumerate(look.HUD_BAR_COLOURS):
        y = top + look.HUD_BAR + j
        for k in range(p["energy"]):
            for x in range(76 - 4 * k, 80 - 4 * k):
                pic[y][x] = look.tv_colour(c, tv)
                pic[y][159 - x] = look.tv_colour(c, tv)


def room_and_figures(pic, p, r, room, frames, tv, top):
    """The room, its grate, its plates, the ball over its plug;
    the figures."""
    flick = (frames >> 2) & 1
    shim = (frames >> 3) & 1
    lv = rooms.LEVELS[room["level"]]
    closed = STEP >= 4 and bool(dungeon.door(r)) and not \
        p["opened"] & dungeon.door_bit(room["level"])
    rp = look.room_picture(room, tv,
                           flick if rooms.torches(room) else 0,
                           shim if lv["shimmer"] else 0,
                           dungeon.plug(r), closed=closed,
                           raised=bool(p["raised"]))
    first = top + look.HUD_LINES
    for line in range(160):
        pic[first + line] = rp[line]
    # player 1 in its two bands (0.6), then the blade and Sir
    # Roderick above it (he flashes after a wound), then the
    # comb of the seam's HMOVE over all of them
    wins = dungeon.windows(r) if STEP >= 5 else ((0, 159), None)
    for band, win in zip((p["band_a"], p["band_b"]), wins):
        if not band or band["kind"] == "none":
            continue
        kind = band["kind"]
        wide = {"king": 2, "crown": 4, "crown_broken": 4}.get(kind, 1)
        if kind in ("serpent", "king"):
            oname = f"{kind}_{'ab'[(frames >> 4) & 1]}"
        else:
            oname = kind
        if kind == "king":          # 0.7: plain, spitting, flashing
            cols = look.king_colours(tv, band["spit"], band["flash"])
        else:
            cols = look.pose_colours(oname, tv, room["level"]
                                     if kind == "serpent" else None)
        figure_pixels(pic, oname, band["x"] + (DOUBLE_OFFSET if wide > 1
                                               else H_OFFSET),
                      band["top"], band["dir"] == 8, wide, cols,
                      first, win)
    # the venom (0.7): missile 1, 8 pixels on the two lines of
    # the King's mouth, in the colour of that pair
    if p["venom"]:
        vp, line = p["venom"]
        col = look.king_colours(tv, True, p["band_a"]["flash"])[
            art.KING_MOUTH]
        for y in (line, line + 1):
            for x in range(vp, vp + 8):
                pic[first + y][x % 160] = col
    kname = POSES[p["kpose"]]
    kcols = look.pose_colours(kname, tv)
    if p["flash"]:
        kcols = [look.tv_colour(rules.FLASH_COLOUR, tv)] * len(kcols)
    blade = p["blade"]
    if blade:
        x0, w = blade
        for j, (_, cname) in enumerate(art.ALL[kname]):
            if cname == art.BLADE_COLOUR:
                for x in range(x0, x0 + w):
                    pic[first + p["ky"] + j][x] = kcols[j]
    figure_pixels(pic, kname, p["kx"] + H_OFFSET, p["ky"],
                  p["kdir"] == 8, False, kcols, first)
    c = dungeon.comb_line(r) if STEP >= 5 else None
    if c is not None:
        pic[first + c][0:8] = [0] * 8


# ---------------------------------------------------------
# D2. the figures in bank 0: what the kernel reads

def figure_windows(tv):
    """For every top line Sir Roderick can have, in every pose,
    and for every thing player 1 can show in each band of each
    room (dungeon.p1_shows: the thing closed and open, the
    guards, nothing), the bytes the kernel reads through the
    pointer (base of the figure + top line, the bases from the
    tables of bank 7) on the lines of the band
    (dungeon.windows: 0.6, the seam cuts the room in two) must
    be the lines of the figure where it is and zero elsewhere;
    the colours of the thrust too (they switch the blade).
    0.7: the same for Sir Roderick in bank 2 (the throne
    kernel reads his bytes there, through the same pointers),
    and in the throne room (bank 2) for the King at every top
    line, the crown and its pieces; the King's colours while
    he spits (they switch the venom) are his colours where he
    is and zero elsewhere, the others his colours where he is.
    Read from the cartridge."""
    sym = symbols(tv)
    rom = open(os.path.join(BUILD, f"scalecrown_{tv}.bin"),
               "rb").read()
    info = json.load(open(os.path.join(ASSETS, "generated",
                                       "game.json")))
    none = [n for n, _ in info["obj_frames"]].index("none")

    def rd(bank, addr):         # a byte of a bank: $x000-$xFFF
        return rom[0x1000 * bank + (addr & 0xFFF)]

    def b7(label, i):           # bank 7: $F000-$FFFF
        return rd(7, sym[label] + i)

    def window(lo, hi, i, top, lines, win=(0, 159), bank=0,
               zeros=True):
        """Wrong bytes; zeros: outside the figure too."""
        base = b7(lo, i) | b7(hi, i) << 8
        bad = 0
        for line in range(win[0], win[1] + 1):
            y = 159 - line
            inside = 0 <= line - top < len(lines)
            if not inside and not zeros:
                continue
            want = lines[line - top] if inside else 0
            if rd(bank, base + top + y) != want:
                bad += 1
        return bad

    bad, n = [], 0
    for bank in (0, 2):         # 0.7: the same bytes in bank 2
        for i, name in enumerate(POSES):
            gl = [b for b, _ in look.figure_lines(name)]
            for top in range(rules.TOP_MIN, rules.TOP_MAX + 1, 2):
                n += 1
                if window("KG_LO", "KG_HI", i, top, gl, bank=bank):
                    bad.append(f"bank {bank}: {name} at {top}")
            cl = look.pose_colours(name, tv)
            thrust = name == art.BLADE_POSE
            for top in range(rules.TOP_MIN, rules.TOP_MAX + 1, 2):
                n += 1
                if window("KC_LO", "KC_HI", i, top, cl, bank=bank,
                          zeros=thrust):
                    bad.append(f"bank {bank}: colours of {name} "
                               f"at {top}")
        fl = [look.tv_colour(rules.FLASH_COLOUR, tv)] * \
            rules.KNIGHT_H
        for top in range(rules.TOP_MIN, rules.TOP_MAX + 1, 2):
            n += 1
            if window("KC_LO", "KC_HI", len(POSES), top, fl,
                      bank=bank, zeros=False):
                bad.append(f"bank {bank}: the flash at {top}")
    for r in range(len(dungeon.ROOMS)):
        wins = dungeon.windows(r)
        th = dungeon.thing_item(r)
        for band, kind, top in dungeon.p1_shows(r):
            if kind == "none":
                k = none
            elif th and kind == th["kind"]:
                k = b7("OB_KIND0", r)
            elif th and kind == dungeon.open_kind(th["kind"]):
                k = b7("OB_KIND1", r)
            else:
                k = b7("S_KIND", r)
            names = {"serpent": ("serpent_a", "serpent_b")}.get(
                kind, (kind,) * 2)
            win = wins[0] if band == "A" else wins[1]
            for f, name in enumerate(names):
                gl = [b for b, _ in look.figure_lines(name)]
                n += 1
                if window("OG_LO", "OG_HI", k + f, top, gl, win):
                    bad.append(f"room {r} band {band} {name} at "
                               f"{top}")
    # 0.7: the throne room, bank 2
    tf, tc = info["throne_frames"], info["throne_colours"]
    for kind, top in dungeon.throne_shows():
        names = ("king_a", "king_b") if kind == "king" else (kind,)
        for name in names:
            gl = [b for b, _ in look.figure_lines(name)]
            n += 1
            if window("TG_LO", "TG_HI", tf.index(name), top, gl,
                      bank=2):
                bad.append(f"throne room: {name} at {top}")
        if kind == "king":
            sets = [("king", False, False), ("king_spit", True, False),
                    ("king_flash", False, True),
                    ("king_flash_spit", True, True)]
            for cname, spit, flash in sets:
                cl = look.king_colours(tv, spit, flash)
                n += 1
                if window("TC_LO", "TC_HI", tc.index(cname), top, cl,
                          bank=2, zeros=spit):
                    bad.append(f"throne room: colours {cname} at "
                               f"{top}")
        else:
            cl = look.pose_colours(kind, tv)
            n += 1
            if window("TC_LO", "TC_HI", tc.index(kind), top, cl,
                      bank=2, zeros=False):
                bad.append(f"throne room: colours {kind} at {top}")
    return dict(windows=n, wrong=len(bad), first=bad[:4])


def compare(pic, png, tv, palette):
    """Stella's picture against the expected one."""
    from PIL import Image
    t = TV[tv]
    im = Image.open(png).convert("RGB")
    px = im.load()
    wrong, first = 0, None
    for v in range(t["visn"]):
        y = t["row0"] + v
        for x in range(160):
            want = tuple(palette[f"{pic[v][x]:02X}"])
            a, b = px[2 * x, y], px[2 * x + 1, y]
            if a != want or b != want:
                wrong += 1
                if first is None:
                    first = dict(line=v, x=x,
                                 want=f"{pic[v][x]:02X}",
                                 got=list(a))
    return dict(pixels=160 * t["visn"], wrong=wrong, first=first)


def save_expected(pic, palette, path):
    from PIL import Image
    im = Image.new("RGB", (320, len(pic)))
    for y, row in enumerate(pic):
        for x, v in enumerate(row):
            c = tuple(palette[f"{v:02X}"])
            im.putpixel((2 * x, y), c)
            im.putpixel((2 * x + 1, y), c)
    im.save(path)


def measure_palette(stella, out):
    """The palette of this Stella (tools/stella_palette.py)."""
    path = os.path.join(ASSETS, "palette_stella.json")
    keep = path + ".kept"
    shutil.copy(path, keep)
    try:
        subprocess.run([sys.executable, os.path.join(
            ROOT, "tools", "stella_palette.py"), "--stella",
            stella], check=True, capture_output=True)
        shutil.copy(path, os.path.join(out, "palette_stella.json"))
        pal = json.load(open(path))
    finally:
        shutil.move(keep, path)
    return pal


# ---------------------------------------------------------
# the checks of one cartridge

def flicker(d):
    """The flicker, measured on the route (0.6): for every stay
    in a room where two things share band A, the frames, those
    with both things there, how many frames showed each, and
    the longest run of frames without one of them while both
    were there."""
    out, cur, last = [], None, {}
    for k, g in enumerate(d.states, 1):
        p = g.pic
        room = p.get("room") if p.get("screen") else None
        if room is None or len(dungeon.band_a(room)) < 2:
            if cur:
                out.append(cur)
            cur = None
            continue
        if cur is None or cur["room"] != room:
            if cur:
                out.append(cur)
            cur = dict(room=room, first_frame=k, frames=0, both=0,
                       shown={}, longest_gap=0)
            last = {}
        a = p["band_a"]
        cur["frames"] += 1
        cur["shown"][a["kind"]] = cur["shown"].get(a["kind"], 0) + 1
        if a["turns"]:
            cur["both"] += 1
            # (0.9.2: the chest opened while they take turns, in
            # room 0, is the same thing: the open chest)
            last[{"chest_open": "chest"}.get(a["kind"],
                                             a["kind"])] = k
            for kind, f in last.items():
                cur["longest_gap"] = max(cur["longest_gap"],
                                         k - f - 1)
        else:
            last = {}
    if cur:
        out.append(cur)
    return out


def serpent_facts(d, tv):
    """0.9.4: what the serpents did on the route (from the
    model's state after each frame, out of the throne room):
    first blows (wounds: pushed KNOCK_PX, or less to the east
    or west end of the path), kills, returns (at the end
    farther from him), returned serpents killed, the frames
    stunned and those blinking, the most pixels a chasing
    serpent crawled in a frame (the sprint: 2 only in PAL)."""
    f = dict(wounds=0, kills=0, returns=0, returned_killed=0,
             stunned_frames=0, blink_frames=0, pushes=0,
             pushes_to_east_end=0, pushes_to_west_end=0,
             return_far=0, sprint_max=0, sprint_2=0)
    back = set()
    for a, b in zip(d.states, d.states[1:]):
        if not (a.screen and b.screen and a.room == b.room) or \
                dungeon.throne(b.room):
            back = set()
            continue
        for k, s in enumerate(dungeon.ROOMS[b.room]["guards"]):
            lo, hi = s["path"]
            al, bl = a.live >> k & 1, b.live >> k & 1
            wound = bl and b.live >> (k + 2) & 1 and \
                not a.live >> (k + 2) & 1
            dx = abs(b.sx[k] - a.sx[k])
            if wound:
                f["wounds"] += 1
                if dx < rules.KNOCK_PX and b.sx[k] == hi:
                    f["pushes_to_east_end"] += 1
                elif dx < rules.KNOCK_PX and b.sx[k] == lo:
                    f["pushes_to_west_end"] += 1
                elif dx == rules.KNOCK_PX:
                    f["pushes"] += 1
            if al and not bl:
                f["kills"] += 1
                if k in back:
                    f["returned_killed"] += 1
                    back.discard(k)
            if bl and not al:
                f["returns"] += 1
                back.add(k)
                far = hi if b.kx <= (lo + hi) // 2 else lo
                f["return_far"] += b.sx[k] == far
            if bl and b.gt[k]:
                f["stunned_frames"] += 1
                f["blink_frames"] += b.blinking[k]
            if al and bl and not wound:
                f["sprint_max"] = max(f["sprint_max"], dx)
                f["sprint_2"] += dx == 2
    f["pass"] = f["wounds"] >= 10 and f["kills"] >= 10 and \
        f["pushes"] + f["pushes_to_east_end"] + \
        f["pushes_to_west_end"] == f["wounds"] and \
        f["pushes_to_east_end"] >= 1 and \
        f["pushes_to_west_end"] >= 1 and f["returns"] >= 1 and \
        f["return_far"] == f["returns"] and \
        f["returned_killed"] >= 1 and f["blink_frames"] >= 1 and \
        f["sprint_max"] == (2 if tv == "pal" else 1) and \
        (f["sprint_2"] >= 1) == (tv == "pal")
    return f


def throne_facts(d):
    """What happened in the throne room on the route (from the
    model's state after each frame): spits, venom parried, the
    wounds of the venom and of the King's bite, the venom gone
    on stone, blows, the crown, VICTORY."""
    f = dict(frames=0, spits=0, parried=0, venom_wounds=0,
             king_bites=0, venom_on_stone=0, blows=0, crown=0,
             victory=0, victory_score=None, energy_left=None)
    vd, kh, cr = f"SC+{model.SC_VD}", f"SC+{model.SC_KH}", \
        f"SC+{model.SC_CROWN}"
    for a, b in zip(d.states, d.states[1:]):
        if not (a.screen and b.screen and b.room == a.room and
                dungeon.throne(b.room)):
            continue
        sa, sb = a.state(), b.state()
        f["frames"] += 1
        hit = b.energy < a.energy
        if not sa.get(vd) and sb.get(vd):
            f["spits"] += 1
        if sb["parry"] > sa["parry"]:
            f["parried"] += 1
        # the venom's wound: it is gone in the same frame (0.9.1:
        # the King's bite takes 3 too, as much as the venom)
        if hit and a.energy - b.energy == rules.VENOM_DAMAGE and \
                sa.get(vd) and not sb.get(vd):
            f["venom_wounds"] += 1
        elif hit:
            f["king_bites"] += 1
        if sa.get(vd) and not sb.get(vd) and not hit and \
                sb["parry"] <= sa["parry"] and not sb[cr]:
            f["venom_on_stone"] += 1
        if sb.get(kh, 0) > sa.get(kh, 0):
            f["blows"] += 1
        if sb[cr] == 1 and sa[cr] == 0:
            f["crown"] += 1
        if sb["won"] and not sa["won"]:
            f["victory"] += 1
            f["victory_score"] = int(f"{sb['score']:02X}"
                                     f"{sb['score+1']:02X}"
                                     f"{sb['score+2']:02X}")
            f["energy_left"] = b.energy
    f["pass"] = f["spits"] >= 5 and f["parried"] >= 2 and \
        f["venom_wounds"] == 2 and f["king_bites"] == 1 and \
        f["venom_on_stone"] >= 1 and \
        f["blows"] == rules.KING_HITS and f["crown"] == 1 and \
        f["victory"] == 1
    return f


# the tests of each start bank (0.9): the parts, side by side
PARTS = ("route", "random0", "random1", "songs", "extremes")
SEEDS = {"route": 11, "songs": 77, "random0": 99, "random1": 199,
         "extremes": 5}
SIM_KEYS = ("lines", "vsync", "idle", "vblank_left_min",
            "title_vblank_left_min", "end_vblank_left_min",
            "end_frames", "sound_cycles", "things_cycles",
            "overscan_left_min", "stack_lowest", "room_changes",
            "setup_cycles", "copy_cycles", "change_vblank_left",
            "seam")
_MADE = {}
SETS = {}       # tv -> what ran (the chain, D.5): written to
#                 coverage_sets_<tv>.json next to report.json


def made(tv, part):
    """The inputs of a part of the tests, made once in a process
    (the model plays them: the same in every process)."""
    key = (tv, part)
    if key not in _MADE:
        if part == "route":
            _MADE[key] = route(tv)
        elif part == "songs":
            _MADE[key] = songs(tv)
        elif part.startswith("random"):
            mode = int(part[-1])
            _MADE[key] = random_game(tv, seed=2600 + mode, mode=mode)
        else:
            p = extremes()
            ei, ep = end_extremes(tv)
            _MADE[key] = (INTO_GAME + [OFF] * len(p) + ei,
                          [{}] * len(INTO_GAME) + p + ep,
                          len(p) + len(ei))
    return _MADE[key]


def sim_job(job):
    """One part of the tests from one start bank in the
    simulator (0.9; a process of its own): its checks, the
    differences from the model, what the cartridge executed and
    read. The RAM and the Superchip RAM at random, a seed for
    each bank."""
    tv, b, part = job
    x = made(tv, part)
    seed = SEEDS[part] + b
    if part == "extremes":
        inputs, pokes, frames = x
        s = simulate(tv, b, seed, inputs, pokes=pokes)
        d = None
    else:
        d = x
        s = simulate(tv, b, seed, d.inputs,
                     pokes=d.pokes if any(d.pokes) else None)
        frames = len(d.inputs)
    why = sim_checks(tv, s)
    diffs = compare_model(d, s) if d else []
    if diffs:
        e = diffs[0]
        why.append(f"{len(diffs)} differences from the model "
                   f"(first: frame {e['frame']} {e['var']} "
                   f"model {e['model']} RAM {e['ram']})")
    out = {k: s[k] for k in SIM_KEYS}
    out.update(tv=tv, start_bank=b, part=part, frames=frames,
               window_errors=s["window_error_count"],
               model_differences=len(diffs), why=why,
               executed=set(s["executed"]),
               rom_reads=set(s["rom_reads"]))
    if part == "route":
        out["ram"] = s["ram"]
        sf = sound_facts(d, s["audio"])
        out["sound"] = sf
        if not sf["passed"]:
            why.append("the songs started and the silence")
    if part == "songs":
        sf = sound_facts(d, s["audio"])
        sf["all_ends"] = songs_pass(sf, tv)
        out["sound"] = sf
        if not (sf["passed"] and sf["all_ends"]):
            why.append("the songs of the ends")
    if part in ("route", "songs") and b == 7:
        out["audio"] = s["audio"]
    if part == "extremes" and \
            s["end_frames"] != 3 * len(END_SCORES) * 2:
        why.append(f"{s['end_frames']} frames of end screens, "
                   f"not {3 * len(END_SCORES) * 2}")
    if part.startswith("random"):
        rg = d
        out.update(
            mode=int(part[-1]),
            rooms=sorted(set(g.room for g in rg.states
                             if g.screen)),
            things_opened=max(bin(g.opened).count("1")
                              for g in rg.states),
            hurts=sum(1 for a, c in zip(rg.states, rg.states[1:])
                      if c.energy < a.energy),
            thrusts=sum(1 for g in rg.states
                        if g.thrust == g.t["THRUST_FRAMES"]),
            kills=sum(1 for a, c in zip(rg.states, rg.states[1:])
                      if c.screen and a.screen and c.room == a.room
                      and bin(c.live).count("1") <
                      bin(a.live).count("1")),
            game_overs=sum(1 for a, c in zip(rg.states,
                                             rg.states[1:])
                           if c.over == 1 and a.over == 0))
    return out


def run_jobs(tv, workers):
    """Every part from every bank: the longest first, in
    `workers` processes."""
    jobs = [(tv, b, part) for part in PARTS for b in range(8)]
    for part in PARTS:          # made here, inherited where the
        made(tv, part)          # processes are forked
    if workers <= 1:
        return [sim_job(j) for j in jobs]
    with concurrent.futures.ProcessPoolExecutor(workers) as ex:
        return list(ex.map(sim_job, jobs))


WORKERS = max(1, min(4, os.cpu_count() or 1))


# ---------------------------------------------------------
# H. the coverage (0.9)

def listing_instructions(tv):
    """Every instruction of the listing: bank, addr ($1000 + the
    offset in the bank, as the simulator keeps them), file,
    listing line, text."""
    ops = {m[0].lower() for m in MPU_NAMES}
    out, cur = [], None
    lst = os.path.join(BUILD, f"scalecrown_{tv}.lst")
    for n, line in enumerate(open(lst, errors="replace"), 1):
        if "------- FILE" in line:
            cur = line.split("FILE")[1].split()[0]
            continue
        m = re.match(r"\s*\d+\s+([0-9a-fA-F]{4})\s+"
                     r"((?:[0-9a-fA-F]{2}\s)+)\s*(.*)$", line)
        if not m:
            continue
        toks = m.group(3).split(";")[0].split()
        if any(t.lower().split(".")[0] in ops for t in toks[:2]):
            a = int(m.group(1), 16)     # the origin: the offset
            out.append(dict(bank=a >> 12, addr=0x1000 | a & 0xFFF,
                            file=cur, line=n,
                            text=" ".join(m.group(3).split())))
    return out


def coverage(tv, executed):
    """The instructions the tests never ran, each with its
    reason (tests/coverage_notes.py); a reason that no longer
    holds is wrong too."""
    ins = listing_instructions(tv)
    sym = symbols(tv)
    never = [i for i in ins if (i["bank"], i["addr"]) not in executed]
    why, unexplained = {}, []
    for i in never:
        r = coverage_notes.reason(i, sym, tv)
        if r is None:
            unexplained.append(f"{i['file']} listing line "
                               f"{i['line']}: {i['text']}")
        else:
            why[r] = why.get(r, 0) + 1
    stale = sorted(coverage_notes.reasons(tv) - set(why))
    by_file = {}
    for i in ins:
        f = by_file.setdefault(i["file"], [0, 0])
        f[0] += 1
        f[1] += (i["bank"], i["addr"]) in executed
    return dict(instructions=len(ins), executed=len(ins) - len(never),
                never=len(never), reasons=why,
                unexplained=unexplained[:40],
                unexplained_count=len(unexplained), stale=stale,
                by_file={k: dict(instructions=v[0], executed=v[1])
                         for k, v in sorted(by_file.items())},
                passed=not unexplained and not stale)


def check(tv, stella, palette, banks=range(8), keep=True,
          sim_banks=range(8), full=True, audio=False, d=None,
          given=None, workers=None):
    """Everything for one television. Full (0.9): every part of
    the tests from every bank (run_jobs), the coverage, Stella
    from every bank with its access counters. Not full (the
    mutations): the route d (or its head) from sim_banks, given
    the simulations already made (bank -> simulate)."""
    rom = os.path.join(BUILD, f"scalecrown_{tv}.bin")
    d = d or route(tv)
    rep = dict(cartridge=f"scalecrown_{tv}", sha256=hashlib.sha256(
        open(rom, "rb").read()).hexdigest(),
        route_frames=len(d.inputs), shots=d.shots,
        shot_states={k: dict(d.states[k - 1].pic) | dict(
            name=dungeon.ROOMS[d.states[k - 1].pic.get("room", 0)][
                "name"] if d.states[k - 1].pic["screen"] else
            d.states[k - 1].pic.get("end") or "title")
            for k in d.shots},
        flicker=flicker(d), throne=throne_facts(d),
        serpents=serpent_facts(d, tv),
        ends=end_facts(d), sim=[], stella=[])
    ok = all(f["longest_gap"] <= 1 and len(f["shown"]) >= 2
             for f in rep["flicker"] if f["both"])
    sims = {}
    if full:
        ok &= rep["throne"]["pass"]
        ok &= rep["serpents"]["pass"]       # 0.9.4
        ok &= ends_pass(rep["ends"])
        _MADE[(tv, "route")] = d
        res = run_jobs(tv, workers or WORKERS)
        by = {(r["part"], r["start_bank"]): r for r in res}
        # B. the route from every bank
        for b in range(8):
            r = by[("route", b)]
            sims[b] = r
            rep["sim"].append({k: r[k] for k in SIM_KEYS} | dict(
                start_bank=b, frames=r["frames"],
                window_errors=r["window_errors"],
                model_differences=r["model_differences"],
                why=r["why"]))
        rep["route_sound"] = by[("route", 7)]["sound"]
        if keep:
            wav(by[("route", 7)]["audio"], tv,
                f"route_sound_{tv}.wav")
        # A2. the songs (0.8), C. the random games, D. the
        # extremes: bank 7 in full, the others in the table
        r = by[("songs", 7)]
        rep["songs"] = dict(frames=r["frames"], lines=r["lines"],
                            model_differences=r["model_differences"],
                            end_frames=r["end_frames"],
                            end_vblank_left_min=r[
                                "end_vblank_left_min"],
                            sound_cycles=r["sound_cycles"],
                            overscan_left_min=r["overscan_left_min"],
                            facts=r["sound"], why=r["why"])
        if keep:
            wav(r["audio"], tv, f"songs_sound_{tv}.wav")
        rep["random"] = []
        for part in ("random0", "random1"):
            r = by[(part, 7)]
            rep["random"].append(dict(
                (k, r[k]) for k in (
                    "mode", "frames", "rooms", "things_opened",
                    "hurts", "things_cycles", "thrusts", "kills",
                    "game_overs", "idle", "vblank_left_min",
                    "sound_cycles", "room_changes",
                    "change_vblank_left", "overscan_left_min",
                    "model_differences", "why")))
        r = by[("extremes", 7)]
        rep["extremes"] = dict(frames=r["frames"], lines=r["lines"],
                               idle=r["idle"],
                               window_errors=r["window_errors"],
                               end_frames=r["end_frames"],
                               end_vblank_left_min=r[
                                   "end_vblank_left_min"],
                               seam=r["seam"], why=r["why"])
        rep["banks"] = [dict(part=r["part"], start_bank=r["start_bank"],
                             frames=r["frames"], lines=r["lines"],
                             vsync=r["vsync"],
                             window_errors=r["window_errors"],
                             model_differences=r["model_differences"],
                             vblank_left_min=r["vblank_left_min"],
                             overscan_left_min=r["overscan_left_min"],
                             stack_lowest=r["stack_lowest"],
                             why=r["why"]) for r in res]
        ok &= all(not r["why"] for r in res)
        fw = figure_windows(tv)
        rep["figures"] = fw
        ok &= not fw["wrong"]
        # H. the coverage, from all the parts of all the banks
        executed = set().union(*(r["executed"] for r in res))
        rep["coverage"] = coverage(tv, executed)
        ok &= rep["coverage"]["passed"]
        # (the chain, D.5: what ran, for the register of the
        # book, tools/chain_register.py: every part of the tests,
        # and the route alone, the one Stella plays too)
        SETS[tv] = dict(executed=sorted(executed), route=sorted(
            set().union(*(by[("route", b)]["executed"]
                          for b in range(8)))), stella=set())
        del res, by
    else:
        for b in sim_banks:
            n = len(d.inputs)
            s = (given or {}).get(b) or simulate(tv, b, 11 + b,
                                                 d.inputs)
            sims[b] = s
            why = sim_checks(tv, s)
            diffs = compare_model(d, s, n)
            if diffs:
                e = diffs[0]
                why.append(f"{len(diffs)} differences from the model "
                           f"(first: frame {e['frame']} {e['var']} "
                           f"model {e['model']} RAM {e['ram']})")
            rep["sim"].append(dict(start_bank=b, frames=n,
                                   model_differences=len(diffs),
                                   why=why))
            ok &= not why
    # E. Stella, from every bank (0.9)
    shots = sorted(d.shots)
    if stella:
        for b in banks:
            st = stella_run.run(
                stella, rom, len(d.inputs),
                joystick=lambda k: d.inputs[k - 1],
                shots=shots, startbank=b,
                keep=os.path.join(EVID, "stella") if keep else None)
            sim = sims[b] if b in sims else simulate(
                tv, b, 11 + b, d.inputs)
            n = len(d.inputs)
            if full and tv in SETS:
                SETS[tv]["stella"] |= st["reads"]
            # Stella's dump after frame k and the RAM of the
            # simulator when frame k+1 begins
            same = sum(1 for a, c in zip(st["ram"], sim["ram"][1:])
                       if a is not None and a == c)
            pics = {}
            why = []
            if same != n:
                bad = [k for k, (a, c) in enumerate(
                    zip(st["ram"], sim["ram"][1:]), 1)
                    if a is None or a != c][:3]
                why.append(f"Stella RAM {same}/{n} (frames {bad})")
            for k in shots:
                if k not in st["shots"]:
                    why.append(f"frame {k}: no picture")
                    continue
                g = d.states[k - 1]
                pic = expected(tv, g)
                cmp = compare(pic, st["shots"][k], tv, palette)
                pics[k] = dict(what=d.shots[k], wrong=cmp["wrong"],
                               first=cmp["first"])
                if keep and b == 7:
                    save_expected(pic, palette, os.path.join(
                        EVID, "expected",
                        f"scalecrown_{tv}_f{k:04d}.png"))
                if cmp["wrong"]:
                    why.append(f"frame {k} ({d.shots[k]}): "
                               f"{cmp['wrong']} pixels differ "
                               f"({cmp['first']})")
            # 0.9: the ROM bytes Stella's counters say were read
            # are the ones the simulator read (outside the window
            # of the Superchip RAM, $x000-$x0FF, which Stella
            # counts as reads of bank 0)
            reads = None
            if full:
                a_ = {(bk, o & 0xFFF) for bk, o in sim["rom_reads"]
                      if o & 0xFFF >= 0x100}
                b_ = {x for x in st["reads"] if x[1] >= 0x100}
                reads = dict(simulator=len(a_), stella=len(b_),
                             only_simulator=len(a_ - b_),
                             only_stella=len(b_ - a_))
                if a_ != b_:
                    why.append(f"ROM reads: {len(a_ - b_)} only in "
                               f"the simulator, {len(b_ - a_)} only "
                               f"in Stella")
            rep["stella"].append(dict(start_bank=b,
                                      version=st["version"],
                                      seconds=st["seconds"],
                                      ram_equal=f"{same}/{n}",
                                      reads=reads,
                                      pictures=pics, why=why))
            ok &= not why
            shutil.rmtree(st["work"], ignore_errors=True)
    if stella and audio:
        a = audio_check.check(stella, rom, tv, EVID)
        rep["audio"] = {k: v for k, v in a.items()}
        if a["recorded"]:
            ok &= a["passed"]
        elif audio == "required":
            ok = False
    rep["pass"] = ok
    return rep


# ---------------------------------------------------------
# F. mutations: one-line defects the checks must catch

MUTATIONS = [
    ("room_kernel.asm", "        sty     ENAM0           ; 11 the "
     "blade: bit 1\n", "", "the store of the blade left out"),
    ("room_kernel.asm", "        sty     ENAM0           ; 11 the "
     "blade: bit 1\n", "        sty     $2C             ; 11 the "
     "blade: bit 1\n", "the blade never switched on (same cycles)"),
    ("room_kernel.asm", "        ldy     znpf2\n        nop\n",
     "        ldy     znpf2\n", "PF2 written before the right half"),
    ("knight.asm", "        cmp     #X_MAX+1",
     "        cmp     #X_MAX", "the east opening one pixel early"),
    ("knight.asm", "        adc     #KNIGHT_H-1     ; bottom line",
     "        adc     #KNIGHT_H-9     ; bottom line",
     "the feet not tested"),
    ("knight.asm", "        lda     #8\n        sta     kdir",
     "        lda     #0\n        sta     kdir",
     "facing right when walking left"),
    ("knight.asm", "        lda     #THRUST_FRAMES",
     "        lda     #THRUST_FRAMES-1", "the thrust a frame short"),
    ("knight.asm", "        cmp     #TOP_MIN+2",
     "        cmp     #TOP_MIN", "off the top of the screen"),
    ("knight.asm", "        adc     #H_FRAC",
     "        adc     #H_FRAC+1", "the walk a little too fast"),
    ("main.asm", "        lda     swres\n        sta     RESMP0\n",
     "", "the blade never hidden"),
    ("hud.asm", "        sta     COLUPF          ; the room's PF2 "
     "unseen\n", "", "the room's first PF2 shows in the HUD"),
    ("hud.asm", "        sta.w   RESP0", "        sta     RESP0",
     "Sir Roderick 3 pixels to the left"),
    ("scalecrown.asm", "M_OFFSET = 2 ", "M_OFFSET = 3 ",
     "the blade a pixel off"),
    ("build_assets.py",
     "            vals.append(sum(0x80 >> i for i in range(8)",
     "            vals.append(sum(1 << i for i in range(8)",
     "the bits of the collision map reversed"),
    # the sound (0.3)
    ("sound.asm", "        ldy     mclock\n        beq     mu_set   "
     "       ; the last frame of the note\n", "",
     "the last frame of a note not silent"),
    ("sound.asm", "        dec     mclock          ; 0: a step's "
     "last frame\n        ldx     #1", "        dec     mclock   "
     "       ; 0: a step's last frame\n        ldx     #0",
     "the melody's volume never written"),
    ("sound.asm", "        bcs     mu_hold", "        bcc     mu_hold",
     "the envelope held from the start"),
    ("music.py", '    lines += table("NOTE_F", [0] + audf)',
     '    lines += table("NOTE_F", [0] + [x + 1 for x in audf])',
     "every note lower (AUDF one more)"),
    ("main.asm", "        inx\n        cpx     #3\n        bcc     "
     "fr_mode", "        inx\n        cpx     #2\n        bcc     "
     "fr_mode", "SELECT skips SILENT"),
    ("knight.asm", "        lda     #SFX_SWORD      ; the sound of "
     "the sword\n        sta     sfxreq          ; (in the SOUND FX "
     "mode)\n", "", "the sword silent"),
    ("main.asm", "kd_sound:                       ; the sound (bank "
     "5)\n        jsr     TO_SOUND\n", "kd_sound:                    "
     "   ; the sound (bank 5)\n", "no sound at all"),
    ("title_kernel.asm", "        beq     tm_go0\n",
     "        bne     tm_go0\n", "the title shows the wrong mode"),
    # the dungeon (0.4)
    ("knight.asm", "        lsr                     ; its byte in "
     "the row, 0-2\n", "", "the wall test in the wrong byte"),
    ("build_assets.py", "        vals = map_bytes(dungeon.walls(r))",
     "        vals = map_bytes(rooms.walls(dungeon.ROOMS[r]))",
     "the plug not in the collision map"),
    ("room_kernel.asm", "        lda     plug            ; the ball: "
     "black on black\n        sta     ENABL           ; until the "
     "room starts\n", "", "the ball never on"),
    ("room_kernel.asm", "        sta     ENABL           ;  5 the "
     "ball off (pixel 0\n", "", "the ball left on after the room"),
    ("build_assets.py", '{None: 0, "west": 158,',
     '{None: 0, "west": 157,', "the west plug a pixel off"),
    ("knight.asm", "        adc     #GRID-1         ; + GRID",
     "        adc     #GRID           ; + GRID",
     "the stair to the wrong room"),
    ("knight.asm", "        bcc     kn_pose         ; the first "
     "level: he stays\n", "", "up through the broken gate"),
    ("knight.asm", "        ldx     #TOP_MIN        ; in at the top",
     "        ldx     #TOP_MIN+2      ; in at the top",
     "in at the wrong end of the stair"),
    ("knight.asm", "        inx                     ; the room east",
     "        dex                     ; the room east",
     "east to the room west"),
    ("main.asm", "        lda     room            ; the name of the "
     "level\n        lsr\n        lsr\n", "        lda     room      "
     "      ; the name of the level\n        lsr\n",
     "the name of the wrong level"),
    ("build_assets.py", '            cb0.append(f"RC_FLAME+{k}")',
     '            cb0.append(f"RC_FLAME+{1 - k}")',
     "the flames of the other level"),
    ("dungeon.asm", "        ldy     #59", "        ldy     #58",
     "the copy a byte short"),
    ("main.asm", "        lda     OB_X,x", "        lda     OB_MIN,x",
     "the guard starts in the wrong place"),
    # the stairs drawn (0.4.1)
    ("build_assets.py", "        st = look.stone(rm, 0, closed=True)\n",
     "        st = look.stone(rm, 0, closed=True, stairs=False)\n",
     "the stairs not drawn in the cartridge"),
    # the things (0.5)
    ("main.asm", "        jsr     TO_THINGS       ; the room (bank 4) "
     "and the\n", "", "the things never looked at"),
    ("things.asm", "        sty     key\n", "",
     "the chest gives no key"),
    ("things.asm", "        cpy     key             ; a door: only "
     "with the key\n        bne     th_done         ; of its level\n",
     "        cpy     key             ; a door: only with the key\n",
     "a door opens without the key"),
    ("things.asm", "        sta     key             ; the key is used "
     "up\n", "", "the key not used up"),
    ("things.asm", "        adc     score+1\n        sta     score+1",
     "        adc     score+2\n        sta     score+1",
     "the points in the wrong digits"),
    ("things.asm", "points: sed\n", "points: nop\n",
     "the points added in binary"),
    ("things.asm", "        lda     #DOOR_BCD", "        lda     "
     "#CHEST_BCD", "a door worth a chest"),
    ("things.asm", "        lda     #SFX_DOOR", "        lda     "
     "#SFX_CHEST", "a door that sounds like a chest"),
    ("things.asm", "th_hit: lda     #SPIKE_DAMAGE", "th_hit: lda     "
     "#0", "the spikes never hurt"),
    ("things.asm", "        lda     #HURT_FRAMES", "        lda     "
     "#1", "the spikes hurt every frame"),
    ("things.asm", "        eor     #1\n        sta     spup",
     "        eor     #0\n        sta     spup",
     "the plates never go up"),
    ("things.asm", "        ldx     SPU4,y          ; the raised "
     "version", "        ldx     SPD4,y          ; the raised "
     "version", "the raised plates not drawn"),
    ("things.asm", "        lda     DOP4,x          ; the grate opens "
     "(the gate:", "        lda     #0              ; the grate opens "
     "(the gate:", "the open grate not drawn when it opens"),
    ("dungeon.asm", "        lda     RDOOR3,x        ; the door of the "
     "room open:", "        lda     #0              ; the door of the "
     "room open:", "the open grate not drawn on the way back"),
    ("main.asm", "        lda     CMC_LO,x\n        ldy     CMC_HI,x\n",
     "        lda     CM_LO,x\n        ldy     CM_HI,x\n",
     "a closed door lets him through"),
    ("main.asm", "        ldy     OB_KIND1,x      ; open",
     "        ldy     OB_KIND0,x      ; open",
     "the chest still closed when open"),
    ("main.asm", "        adc     #8\nrs_key:", "        adc     #0\n"
     "rs_key:", "the key not shown in the HUD"),
    ("main.asm", "        lda     #0\n        sta     spup",
     "        lda     #1\n        sta     spup",
     "the plates start up in a new room"),
    ("things.asm", "        adc     CRAWL,x", "        adc     #0",
     "the guards never crawl"),
    ("build_assets.py", '"TH_DOWN", rules.spike_frames(tv)[0]',
     '"TH_DOWN", [x + 1 for x in rules.spike_frames(tv)[0]]',
     "the plates down a frame too long"),
    ("build_assets.py", "map_bytes(dungeon.walls(r, closed=True))",
     'map_bytes(dungeon.walls(\n                r, closed=dungeon.door(r) == "grate"))',
     "the gate does not close the way"),
    ("build_assets.py", "    post = [max([0] + [t - l0 for t, l0, _ in u])",
     "    post = [max([0] + [t - l0 - 2 for t, l0, _ in u])",
     "too few zeros above the figures"),
    # the serpents, the seam, GAME OVER (0.6)
    ("room_kernel.asm", "        ldx     zcoarse         ; 17\n",
     "        nop\n        ldx     zcoarse         ; 17\n",
     "RESP1 of the seam two cycles late"),
    ("room_kernel.asm", "        sta     HMOVE           ;  2 B3: the "
     "fine move\n", "", "the fine move of the seam left out"),
    ("room_kernel.asm", "        sta     REFP1           ; 57 (player 1 "
     "is empty)", "        sta     $2D             ; 57 (player 1 is "
     "empty)", "the guard below faces as the thing above"),
    ("build_assets.py", '    b7 += data_lines("SEAM", [0 if c is None '
     'else c + 1', '    b7 += data_lines("SEAM", [0 if c is None else '
     'c + 2', "the seam a course late"),
    ("room_kernel.asm", "        sta     sgfx\n", "        sta     "
     "tmp+1\n", "the graphics of the guard below not taken"),
    ("room_kernel.asm", "        sta     scol\n", "        sta     "
     "tmp+1\n", "the colours of the guard below not taken"),
    ("room_kernel.asm", "        bne     k_b1c           ; 33 (k_b1c)",
     "        bpl     k_b1c           ; 33 (k_b1c)",
     "the test of the seam wrong"),
    ("hud.asm", "        lda     SCR+SC_HM       ; 0.6: the fine move "
     "of the\n        sta     HMP1            ; seam (its HMOVE uses "
     "it)\n", "", "the fine move of the seam never written"),
    ("main.asm", "        bcs     pb_show         ; both: odd frames "
     "the guard", "        bcc     pb_show         ; both: odd frames "
     "the guard", "the flicker the other way round"),
    ("things.asm", "        ldy     #0\ngu_div: iny",
     "        ldy     #1\ngu_div: iny",
     "the delay of the seam a count too long"),
    ("main.asm", "        lda     S_X,x           ; at their start",
     "        lda     S_X+16,x        ; at their start",
     "the first guard starts where the second does"),
    ("main.asm", "        lda     #3              ; both alive,",
     "        lda     #1              ; both alive,",
     "the second guard not back in a room"),
    ("main.asm", "        and     #FLASH_FRAMES   ; in the thrust: they "
     "switch", "        and     #0              ; in the thrust: they "
     "switch", "no flash after a wound"),
    ("main.asm", "        cmp     #GO_FRAMES\n",
     "        cmp     #2\n", "GAME OVER cut short"),
    ("main.asm", "        dex                     ; GAME OVER\n",
     "", "GAME OVER written as VICTORY"),
    ("things.asm", "        lda     #BITE_DAMAGE    ; bitten",
     "        lda     #1              ; bitten", "a bite takes 1"),
    ("things.asm", "wo_en:  sta     energy\n        lda     "
     "#BITE_FRAMES", "wo_en:  sta     energy\n        lda     #1",
     "no rest after a bite"),
    ("things.asm", "; bitten\n        jsr     wound\n        lda     "
     "#SFX_BITE\n", "; bitten\n        jsr     wound\n        lda     "
     "#0\n", "the bite silent"),
    ("things.asm", "        cmp     #15\n", "        cmp     #8\n",
     "the blade too short to kill"),
    ("things.asm", "        and     SCR+SC_LIVE\n        sta     "
     "SCW+SC_LIVE\n", "        and     SCR+SC_LIVE\n        sta     "
     "tmp\n", "a serpent struck does not die"),
    ("things.asm", "ga_tl:  lda     #8              ; it turns",
     "ga_tl:  lda     #0              ; it turns",
     "the serpents do not turn"),
    ("things.asm", "        lda     #1\n        sta     over",
     "        lda     #0\n        sta     over", "no GAME OVER"),
    # the Serpent King, the venom, the shield, the crown,
    # VICTORY; the throne kernel (0.7)
    ("throne_kernel.asm", "        sta     ENAM1           ; 20 the "
     "venom: bit 1\n", "", "the venom never drawn"),
    ("throne_kernel.asm", "        sty     ENAM0           ; 11 the "
     "blade: bit 1\n", "        sty     $2C             ; 11 the "
     "blade: bit 1\n", "the blade never shown in the throne room"),
    ("throne_kernel.asm", "        sty     PF2             ; 62+ after "
     "the right half\n", "        sty     $2D             ; 62+ after "
     "the right half\n", "the throne room's PF2 never changes"),
    ("hud.asm", "        beq     hu_throne\n", "",
     "the throne room drawn by the kernel of the other rooms"),
    ("main.asm", "        lda     #0\n        sta     RESMP1\n",
     "        lda     #2\n        sta     RESMP1\n",
     "the venom always hidden"),
    ("main.asm", "        lda     #2\n        sta     RESMP1\n",
     "        lda     #0\n        sta     RESMP1\n",
     "the venom shown when it does not fly"),
    ("main.asm", "        sbc     #M_OFFSET\n        bcs     pr_vcol",
     "        sbc     #M_OFFSET-1\n        bcs     pr_vcol",
     "the venom a pixel off"),
    ("main.asm", "        ldx     #8              ; facing Sir "
     "Roderick", "        ldx     #0              ; facing Sir "
     "Roderick", "the King never faces west"),
    ("main.asm", "        inx                     ; flashing (+ 2)\n"
     "        inx\n", "", "the King never flashes"),
    ("main.asm", "        lda     #SPIT_FIRST\n",
     "        lda     #1\n", "the King spits at once"),
    ("main.asm", "        sta     parry           ; the King on his "
     "throne\n        sta     SCW+SC_CROWN\n", "        sta     parry"
     "           ; the King on his throne\n",
     "the crown stays broken in a new game"),
    ("main.asm", "        cmp     #VIC_FRAMES     ; the end screen "
     "(0.8)", "        cmp     #2              ; the end screen "
     "(0.8)", "VICTORY cut short"),
    ("main.asm", "        ldx     #5              ; VICTORY (0.7)",
     "        ldx     #4              ; VICTORY (0.7)",
     "VICTORY written as GAME OVER"),
    ("knight.asm", "        lda     #PARRY_POSE\n",
     "        lda     #0\n", "the shield never shown"),
    ("things.asm", "        ora     won             ; stops\n", "",
     "the King goes on after VICTORY"),
    ("things.asm", "        lda     #VENOM_DAMAGE\n",
     "        lda     #VENOM_DAMAGE-1\n", "the venom takes 2"),
    ("things.asm", "        bcs     tr_vside        ; faces right\n"
     "        eor     #8\n", "        bcs     tr_vside        ; faces "
     "right\n", "the shield on the wrong side"),
    ("things.asm", "        lda     kpose           ; in the thrust: "
     "no parry\n        cmp     #THRUST_POSE\n        beq     "
     "tr_vhit\n", "", "the shield in the thrust too"),
    ("things.asm", "        lda     #PARRY_FRAMES   ; parried",
     "        lda     #1              ; parried",
     "the parry too short"),
    ("things.asm", "        cmp     VSPAN_LO,x\n        bcc     "
     "tr_vgone\n", "", "the venom through the stone"),
    ("things.asm", "        adc     #VEN_FRAC\n",
     "        adc     #VEN_FRAC/2\n", "the venom too slow"),
    ("things.asm", "        lda     #KHIT_FRAMES\n",
     "        lda     #1\n", "a blow counts every frame"),
    ("things.asm", "        cmp     #KING_HITS\n",
     "        cmp     #KING_HITS-1\n", "the King beaten a blow early"),
    ("things.asm", "        bcs     tr_side\n",
     "        bcc     tr_side\n", "the venom flies away from him"),
    ("things.asm", "        sbc     #2              ; up (carry is "
     "set)", "        sbc     #4              ; up (carry is set)",
     "the King steps up 4 lines"),
    ("things.asm", "        lda     SPIT,x\n", "        lda     SPIT\n",
     "the King never spits faster"),
    ("things.asm", "        sbc     #KBITE_X0\n",
     "        sbc     #KBITE_X0+1\n", "the King's bite a pixel late"),
    ("things.asm", "tr_en:  lda     #ENERGY_BCD",
     "tr_en:  lda     #KHIT_BCD", "500 points for each unit of energy"),
    ("build_assets.py", '                tv, spit="spit" in name, '
     'flash="flash" in name)))', '                tv, spit=False, '
     'flash="flash" in name)))',
     "the King's colours while he spits not made"),
    ("build_assets.py", '               f"bank {suffix or 0}", "",',
     '               f"bank {suffix or 0}", "" if not suffix else '
     '"        .byte 0",', "Sir Roderick's bytes moved in bank 2"),
    # the states and the sound: the end screens, the songs (0.8)
    ("sound.asm", "fetch:  txa\n        clc\n        adc     song\n",
     "fetch:  txa\n        clc\n        adc     #0\n",
     "every song reads the streams of the theme"),
    ("sound.asm", "        txa                     ; $FF: to the loop "
     "point\n        clc\n        adc     song\n",
     "        txa                     ; $FF: to the loop point\n"
     "        clc\n        adc     #0\n",
     "the loop points of the theme for every song"),
    ("music.py", "            lp = len(data)      # the end: a rest, "
     "for ever\n", "", "the songs of the end again after their rest"),
    ("things.asm", "        lda     #SONG_GAMEOVER  ; 0.8: the lament "
     "(MUSIC)", "        lda     #SONG_THEME     ; 0.8: the lament "
     "(MUSIC)", "GAME OVER plays the theme"),
    ("things.asm", "        lda     #SONG_VICTORY   ; 0.8: the fanfare "
     "(MUSIC)", "        lda     #SONG_GAMEOVER  ; 0.8: the fanfare "
     "(MUSIC)", "VICTORY plays the lament"),
    ("things.asm", "        lda     #$FF            ; (a new song: the "
     "player\n        sta     smode           ; silences what "
     "played)\n", "", "GAME OVER does not silence the theme"),
    ("main.asm", "theme:  lda     #SONG_THEME\n        sta     song\n"
     "        lda     #$FF\n        sta     smode\n",
     "theme:  lda     #SONG_THEME\n        sta     song\n",
     "the theme goes on from where it was left"),
    ("main.asm", "        jsr     theme           ; 0.8: the theme "
     "anew\n", "", "a new game keeps the song of the end"),
    ("main.asm", "        sta     won\n        jsr     theme\n",
     "        sta     won\n", "the title after an end keeps its song"),
    ("main.asm", "        cmp     #GO_FRAMES+END_FRAMES\n",
     "        cmp     #GO_FRAMES\n",
     "the button at once on the GAME OVER screen"),
    ("main.asm", "        bit     pressed         ; the button: the "
     "title, the\n        bpl     fe_draw", "        lda     pressed"
     "         ; the button: the title, the\n        beq     fe_draw",
     "SELECT too goes back to the title"),
    ("main.asm", "        inc     won\n        bne     fe_draw         "
     "; (never 0)\n", "        bne     fe_draw         ; (never 0)\n",
     "the VICTORY screen waits for ever"),
    ("main.asm", "        ora     won             ; or won: an end "
     "screen", "        ora     #0              ; or won: an end "
     "screen", "the VICTORY screen taken for the title"),
    ("main.asm", "        lda     pressed         ; RESET: a game at "
     "once", "        lda     #0              ; RESET: a game at "
     "once", "RESET does nothing on an end screen"),
    ("main.asm", "        bcs     es_lo           ; odd: the low "
     "nibble", "        bcc     es_lo           ; odd: the low "
     "nibble", "the digits of the end screens swapped in pairs"),
    ("main.asm", "        sta     SCW,x           ; the empty line\n",
     "", "the empty line of the digits not written"),
    ("ends_kernel.asm", "        beq     go_screen\n",
     "        bne     go_screen\n", "the two end screens swapped"),
    ("ends_kernel.asm", "        DECOR   4, GOE_TOP, GO, E\n",
     "        DECOR   4, GOE_TOP, VI, E\n",
     "GAME OVER in the colours of VICTORY at the top"),
    ("ends_kernel.asm", "        sta     VBLANK          ; the picture "
     "starts\n", "", "the end screens blank"),
    ("ends_kernel.asm", "        lda     #{1}_REF1\n        sta     "
     "REFP1\n", "        lda     #{1}_REF1\n        sta     REFP0\n",
     "the Serpent King of GAME OVER facing the wrong way"),
    ("ends_kernel.asm", "        eor     #7\n", "        eor     #6\n",
     "the players of the end screens a pixel off"),
    ("ends_kernel.asm", "        lda     #OVER_TIM\n        sta     "
     "TIM64T\n", "", "the overscan of the end screens not timed"),
    ("scalecrown.asm", "        sta     F4B6            ; $FAA: to the "
     "end screens\n", "        sta     F4B1            ; $FAA: to "
     "the end screens\n", "the trampoline to bank 1, not 6"),
    ("build_assets.py", '        b6.append(f"ESC{col} = SCR+{n * col}")',
     '        b6.append(f"ESC{col} = SCR+{n * col + 1}")',
     "the score of the end screens a line off"),
    # the final cartridge (0.9)
    ("knight.asm", "        lda     #SFX_STAIR      ; the steps (0.9; in "
     "the\n        sta     sfxreq          ; SOUND FX mode)\n", "",
     "the stairs silent"),
    ("knight.asm", "        lda     #SFX_STAIR      ; the steps",
     "        lda     #SFX_DOOR       ; the steps",
     "a stair that sounds like a door"),
    ("things.asm", "        bcs     wo_en\n        lda     #0\n",
     "        bcs     wo_en\n        lda     #1\n",
     "a wound leaves 1 unit where none is left"),
    ("things.asm", "        bcs     wo_en\n        lda     #0\n",
     "        bcs     wo_en\n", "the energy below 0 after a wound"),
    ("things.asm", "th_hit: lda     #SPIKE_DAMAGE   ; a wound (0.9: the "
     "routine\n        jsr     wound           ; of every wound), "
     "with the\n        lda     #HURT_FRAMES    ; rest of the "
     "spikes\n        sta     hurt\n", "th_hit: lda     "
     "#SPIKE_DAMAGE   ; a wound (0.9: the routine\n        jsr     "
     "wound           ; of every wound), with the\n",
     "the spikes rest as long as a bite"),
    # 0.9.1: the King and the serpents harder (rules.py); the
    # cartridge with the numbers of 0.9, the model with 0.9.1's
    ("build_assets.py", 'f"KING_HITS = {rules.KING_HITS}",',
     'f"KING_HITS = {rules.KING_HITS - 2}",',
     "the King beaten after 8 blows, as in 0.9"),
    ("build_assets.py", 'f"BITE_DAMAGE = {rules.BITE_DAMAGE}"]',
     'f"BITE_DAMAGE = {rules.BITE_DAMAGE - 1}"]',
     "the bite of 0.9, 2 units"),
    ("build_assets.py", '"SPIT", rules.spit_frames(tv), per=8))',
     '"SPIT", [n + rules.frames_of(0.4, tv) for n in '
     'rules.spit_frames(tv)], per=8))',
     "the King spits 0.4 seconds later, as in 0.9"),
    ("build_assets.py", "rules.table(tv).items()])",
     '{**rules.table(tv), "KSTEP_FRAC": rules.per_frame(15, tv)'
     '[1]}.items()])',
     "the King follows as slowly as in 0.9"),
    ("build_assets.py", "rules.table(tv).items()])",
     '{**rules.table(tv), **dict(zip(("VEN_INT", "VEN_FRAC"), '
     'rules.per_frame(90, tv)))}.items()])',
     "the venom as slow as in 0.9"),
    ("build_assets.py", 'else dungeon.ROOMS[r]["level"], tv)',
     'else dungeon.ROOMS[r]["level"], tv) * 30 // 38',
     "the serpents about as slow as in 0.9"),
    # 0.9.2: the King's head, the chase, 12 units
    ("things.asm", "        lda     #KING_HEAD+1    ; 0.9.2: his head "
     "only", "        lda     #KING_H+1       ; 0.9.2: his head only",
     "the King struck on his whole body, as in 0.9.1"),
    ("things.asm", "ga_crawl:\n        lda     ky\n", "ga_crawl:\n"
     "        jmp     ga_round\n        lda     ky\n",
     "the serpents never chase"),
    ("things.asm", "        lda     #0              ; his column right "
     "of its\n        bcs     ga_face", "        lda     #0         "
     "     ; his column right of its\n        bcc     ga_face",
     "the serpents flee"),
    # (0.9.3: the chase only with his column on the path)
    ("things.asm", "        lda     S_MAX4,x\n        cmp     kx\n"
     "        bcc     ga_round        ; right of its path\n", "",
     "a chasing serpent past the right end of its path"),
    ("build_assets.py", 'f"ENERGY_FULL = {rules.ENERGY}",',
     'f"ENERGY_FULL = {rules.ENERGY + 4}",',
     "16 units of energy, as in 0.9.1"),
    # 0.9.3: the bounds of the chase
    ("things.asm", "        lda     kx\n        cmp     S_MIN4,x\n"
     "        bcc     ga_round        ; left of its path\n", "",
     "a chasing serpent past the left end of its path"),
    ("things.asm", "        bcc     ga_round        ; left of its path\n"
     "        lda     S_MAX4,x\n        cmp     kx\n"
     "        bcc     ga_round        ; right of its path",
     "        bcc     ga_done         ; left of its path\n"
     "        lda     S_MAX4,x\n        cmp     kx\n"
     "        bcc     ga_done         ; right of its path",
     "the serpents stand still with him off their path, as the "
     "author saw in 0.9.2"),
    # 0.9.4: the sprint, two blows, the return
    ("things.asm", "        lda     tmp+1\n        and     #6         "
     "     ; the sprint, 2 x 0-2\n", "        lda     tmp+1\n"
     "        asl\n        and     #2\n",
     "the chase as slow as the round, as in 0.9.3"),
    ("things.asm", "        lda     SPRI,x\n        adc     #0\n",
     "        lda     SPRI,x\n        adc     #1\n",
     "the sprint a pixel a frame faster"),
    ("things.asm", "        adc     SPRF,x\n", "        adc     #0\n",
     "the fraction of the sprint lost: no chase in NTSC"),
    ("things.asm", "ga_blow:\n        lda     WBIT,y\n        and     "
     "SCR+SC_LIVE\n        bne     ga_kill\n",
     "ga_blow:\n        jmp     ga_kill\n",
     "one blow kills, as in 0.9.3"),
    ("things.asm", "        and     SCR+SC_LIVE\n        bne     "
     "ga_kill\n", "        and     SCR+SC_LIVE\n",
     "every blow only wounds: the serpents never die"),
    ("things.asm", "ga_pset:\n        sta     SCW+SC_SX,y\n",
     "ga_pset:\n", "the first blow pushes nothing"),
    ("things.asm", "        lda     kdir\n        bne     ga_pushl\n",
     "        lda     kdir\n        beq     ga_pushl\n",
     "the first blow pushes it towards him"),
    ("things.asm", "        lda     S_MAX4,x        ; (the end of its "
     "path)\n", "", "the push past the east end of its path"),
    ("things.asm", "        bcs     ga_pset\n        lda     S_MIN4,x\n",
     "        bcs     ga_pset\n", "the push past the west end of its "
     "path"),
    ("things.asm", "        lda     #STUN_FRAMES\n        sta     "
     "SCW+SC_GT,y\n", "", "no stun after the first blow"),
    ("things.asm", "        sta     SCW+SC_GT,y\n        rts\n        ; "
     "- the blade:", "        sta     SCW+SC_GT,y\n        jmp     "
     "ga_bite\n        ; - the blade:",
     "a stunned serpent bites and crawls"),
    ("build_assets.py", "rules.table(tv).items()])",
     '{**rules.table(tv), "STUN_FRAMES": 2}.items()])',
     "the stun shorter than a thrust: one thrust kills"),
    # (the same bytes long: a shorter bank 7 moves the kernel
    # after it, and its lines would catch it, not its picture)
    ("main.asm", "        and     #FLASH_FRAMES\n        bne     "
     "pb_noguard\n", "        and     #0\n        bne     "
     "pb_noguard\n", "a stunned serpent above the seam never blinks"),
    ("main.asm", "        and     #FLASH_FRAMES\n        bne     "
     "pb_dead\n", "        and     #0\n        bne     pb_dead\n",
     "a stunned serpent below the seam never blinks"),
    ("main.asm", "        and     #FLASH_FRAMES\n        bne     "
     "pb_noguard\n", "        and     #FLASH_FRAMES\n        beq     "
     "pb_noguard\n", "a stunned serpent blinking out of step"),
    ("things.asm", "        bne     gu_next\n        jsr     respawn\n",
     "        bne     gu_next\n", "a serpent killed never comes back"),
    ("things.asm", "        lda     #RESPAWN_FRAMES\n",
     "        lda     #STUN_FRAMES\n",
     "a serpent killed back in half a second"),
    ("things.asm", "        bcc     re_min          ; he is right of "
     "the middle\n", "        bcs     re_min          ; he is right "
     "of the middle\n", "a serpent back at the end nearer him"),
    ("things.asm", "        lda     #8\n        bne     re_face\n",
     "        lda     #0\n        beq     re_face\n",
     "a serpent back facing the wrong way"),
    ("things.asm", "        lda     GBIT,y\n        ora     WBIT,y\n",
     "        lda     GBIT,y\n",
     "a serpent back wounded: one blow kills it"),
    ("things.asm", "WBIT    .byte   4, 8", "WBIT    .byte   4, 4",
     "the wound of the second serpent on the first"),
]


def staged(tv, stella, palette):
    """The checks of a mutation, cheapest first, until one
    fails: the route in the simulator (bank 7) with the model,
    the extremes, the figures, Stella, the random games. The
    simulations stop at the first difference from the model,
    the first frame with the wrong lines, a write out of its
    window or the seam wrong (quick)."""
    d = route(tv)
    s = simulate(tv, 7, 18, d.inputs, model=d, quick=True)
    s7 = s                      # the same as check's, bank 7
    if s["early"]:
        e = s["early"][0]
        return True, (f"route: model: frame {e['frame']} {e['var']} "
                      f"{e['model']} RAM {e['ram']}")
    why = sim_checks(tv, s)
    if why:
        return True, "route: " + "; ".join(why[:2])
    sf = sound_facts(d, s["audio"])
    if not sf["passed"]:
        return True, "route: the songs " + str(
            [f for f in sf["starts"] if not f.get("ok", True)][:1])
    if not ends_pass(end_facts(d)):
        return True, "route: the end screens"
    # 0.8: the songs, the ends put in the RAM
    sg = songs(tv)
    s = simulate(tv, 7, 77, sg.inputs, pokes=sg.pokes, model=sg,
                 quick=True)
    if s["early"]:
        e = s["early"][0]
        return True, (f"songs: model: frame {e['frame']} {e['var']} "
                      f"{e['model']} RAM {e['ram']}")
    why = sim_checks(tv, s)
    sf = sound_facts(sg, s["audio"])
    if why or not sf["passed"] or not songs_pass(sf, tv):
        return True, "songs: " + "; ".join(why[:2] or [str(
            [f for f in sf["starts"] if not f.get("ok", True)][:1])])
    p = extremes()
    ei, ep = end_extremes(tv)
    s = simulate(tv, 7, 5, INTO_GAME + [OFF] * len(p) + ei,
                 pokes=[{}] * len(INTO_GAME) + p + ep, quick=True)
    why = sim_checks(tv, s)
    if s["end_frames"] != 3 * len(END_SCORES) * 2:
        why.append(f"{s['end_frames']} frames of end screens")
    if why:
        return True, "extremes: " + "; ".join(why[:2])
    fw = figure_windows(tv)
    if fw["wrong"]:
        return True, f"figures: {fw['wrong']} windows ({fw['first']})"
    # Stella: first the start of the route (the title, rooms 1,
    # 2, 3 and the seam of room 0: most pictures that differ
    # are there), then all of it
    for part in (STELLA_FIRST, None):
        rep = check(tv, stella, palette, banks=(7,), keep=False,
                    sim_banks=(7,), full=False,
                    d=d.head(part) if part else d, given={7: s7})
        if not rep["pass"]:
            return True, "Stella: " + "; ".join(
                rep["stella"][0]["why"][:2])
    for mode, seed in ((0, 2600), (1, 2601)):
        rg = random_game(tv, seed=seed, mode=mode)
        s = simulate(tv, 7, 99, rg.inputs, model=rg, quick=True)
        if s["early"]:
            e = s["early"][0]
            return True, (f"random game: model: frame {e['frame']} "
                          f"{e['var']} {e['model']} RAM {e['ram']}")
        why = sim_checks(tv, s)
        if why:
            return True, "random game: " + "; ".join(why[:2])
    return False, "nothing"


def cartridges():
    """The SHA-256 of the two cartridges just built."""
    return tuple(hashlib.sha256(open(os.path.join(
        BUILD, f"scalecrown_{tv}.bin"), "rb").read()).hexdigest()
        for tv in ("ntsc", "pal"))


def mutations(stella, palette):
    """Each mutation: built, and checked (staged). 0.9.1: a
    mutation that gives the same bytes as the cartridge cannot
    be caught by any test (an equivalent mutation: in 0.9.1 the
    bite took as much as the venom, and "the venom takes 2",
    BITE_DAMAGE for VENOM_DAMAGE, became the same program); it
    is told as such, a MISSED that is a fault of the list."""
    out = []
    base = cartridges()
    for i, (fn, old, new, what) in enumerate(MUTATIONS, 1):
        path = os.path.join(ASSETS if fn.endswith(".py") else SRC,
                            fn)
        orig = open(path).read()
        if orig.count(old) != 1:
            out.append(dict(n=i, what=what, error="not found once"))
            print(f"mutation {i}: NOT FOUND ({what})")
            continue
        try:
            open(path, "w").write(orig.replace(old, new))
            r = subprocess.run([sys.executable, os.path.join(
                ROOT, "tools", "build.py")],
                capture_output=True, text=True)
            if r.returncode:
                caught, why = True, "build"
            elif cartridges() == base:
                caught, why = False, ("the same bytes as the "
                                      "cartridge: an equivalent "
                                      "mutation, to be changed")
            else:
                try:
                    caught, why = staged("ntsc", stella, palette)
                except Exception as e:      # the mutant broke the
                    caught = True           # checks: said so
                    why = (f"the checks stopped: "
                           f"{type(e).__name__}: {e}")
            out.append(dict(n=i, what=what, caught=caught, by=why))
            print(f"mutation {i}: {'CAUGHT' if caught else 'MISSED'}"
                  f" ({what}: {why[:150]})", flush=True)
        finally:
            open(path, "w").write(orig)
    subprocess.run([sys.executable, os.path.join(
        ROOT, "tools", "build.py")], capture_output=True,
        check=True)
    return out


def main():
    global EVID
    ap = argparse.ArgumentParser()
    ap.add_argument("--stella")
    ap.add_argument("--mutations", action="store_true")
    ap.add_argument("--out", default=EVID)
    ap.add_argument("--audio", action="store_true")
    ap.add_argument("--audio-required", action="store_true")
    ap.add_argument("--workers", type=int, default=WORKERS)
    a = ap.parse_args()
    audio = "required" if a.audio_required else bool(a.audio)
    EVID = os.path.abspath(a.out)
    for d in ("", "stella", "expected"):
        os.makedirs(os.path.join(EVID, d), exist_ok=True)
    subprocess.run([sys.executable, os.path.join(
        ROOT, "tools", "build.py")], check=True)
    palette = measure_palette(a.stella, EVID) if a.stella else None
    report = dict(random_frames=RANDOM_FRAMES, cartridges=[])
    # the dungeon: the maps against the plan and the knight's
    # box (tests/check_dungeon.py), and the 16 rooms in a sheet
    r = subprocess.run([sys.executable, os.path.join(
        HERE, "check_dungeon.py"), "--out", EVID, "--sheet",
        os.path.join(EVID, f"MAPPA_DUNGEON_{MS}.png")],
        capture_output=True, text=True)
    print(r.stdout.strip().splitlines()[-1], flush=True)
    report["dungeon"] = r.returncode == 0
    ok = r.returncode == 0
    for tv in ("ntsc", "pal"):
        rep = check(tv, a.stella, palette[tv] if palette else None,
                    audio=audio, workers=a.workers)
        report["cartridges"].append(rep)
        ok &= rep["pass"]
        for s in rep["sim"]:
            print(f"{tv} sim bank {s['start_bank']}: {s['frames']} "
                  f"frames, lines "
                  f"{s['lines']} vsync {s['vsync']} windows "
                  f"{s['window_errors']} model differences "
                  f"{s['model_differences']} VBLANK left "
                  f"{s['vblank_left_min']} x 64 (title "
                  f"{s['title_vblank_left_min']}, end screens "
                  f"{s['end_vblank_left_min']} in "
                  f"{s['end_frames']} frames; {s['room_changes']} "
                  f"changes of room: setup {s['setup_cycles']}, copy "
                  f"{s['copy_cycles']} cycles, VBLANK left "
                  f"{s['change_vblank_left']} x 64), things "
                  f"{s['things_cycles']} cycles, sound "
                  f"{s['sound_cycles']} cycles, overscan left "
                  f"{s['overscan_left_min']} x 64, stack from "
                  f"${s['stack_lowest']:02X}, seam "
                  f"{s['seam']['frames']} frames "
                  f"{s['seam']['wrong']} wrong "
                  f"{'PASS' if not s['why'] else s['why']}",
                  flush=True)
        print(f"{tv} idle {rep['sim'][0]['idle']}")
        for part in PARTS:
            rs = [r for r in rep["banks"] if r["part"] == part]
            print(f"{tv} {part} from the eight banks: frames "
                  f"{rs[0]['frames']}, lines "
                  f"{sorted(set(x for r in rs for x in r['lines']))}, "
                  f"windows {sum(r['window_errors'] for r in rs)}, "
                  f"model differences "
                  f"{sum(r['model_differences'] for r in rs)}, "
                  f"VBLANK left {min(r['vblank_left_min'] for r in rs if r['vblank_left_min'] is not None)}"
                  f" x 64, overscan left "
                  f"{min(r['overscan_left_min'] for r in rs if r['overscan_left_min'] is not None)}"
                  f" x 64, stack from "
                  f"${min(r['stack_lowest'] for r in rs):02X} "
                  f"{'PASS' if not any(r['why'] for r in rs) else [r['why'][:2] for r in rs if r['why']][:2]}")
        c = rep["coverage"]
        print(f"{tv} coverage: {c['instructions']} instructions, "
              f"{c['executed']} executed, {c['never']} never "
              f"{c['reasons']}, unexplained "
              f"{c['unexplained_count']} {c['unexplained'][:5]}, "
              f"stale {c['stale']} "
              f"{'PASS' if c['passed'] else 'FAIL'}")
        for r in rep["random"]:
            print(f"{tv} random game, mode {r['mode']}: "
                  f"{r['frames']} frames, rooms {r['rooms']} "
                  f"({r['room_changes']} changes, VBLANK left "
                  f"{r['change_vblank_left']} x 64), "
                  f"things opened {r['things_opened']}, hurts "
                  f"{r['hurts']}, kills {r['kills']}, GAME OVER "
                  f"{r['game_overs']}, "
                  f"thrusts {r['thrusts']}, model differences "
                  f"{r['model_differences']}, sound "
                  f"{r['sound_cycles']} cycles "
                  f"{'PASS' if not r['why'] else r['why']}")
        fw = rep["figures"]
        print(f"{tv} figures: {fw['windows']} windows of the kernel, "
              f"{fw['wrong']} wrong {fw['first']}")
        for f in rep["flicker"]:
            print(f"{tv} flicker: room {f['room']} from frame "
                  f"{f['first_frame']}: {f['frames']} frames, "
                  f"{f['both']} with both, shown {f['shown']}, "
                  f"longest gap {f['longest_gap']}")
        f = rep["throne"]
        print(f"{tv} throne room: {f['frames']} frames, spits "
              f"{f['spits']}, parried {f['parried']}, venom wounds "
              f"{f['venom_wounds']}, on stone {f['venom_on_stone']}, "
              f"King's bites {f['king_bites']}, blows {f['blows']}, "
              f"crown {f['crown']}, VICTORY {f['victory']} (score "
              f"{f['victory_score']}, energy {f['energy_left']}) "
              f"{'PASS' if f['pass'] else 'FAIL'}")
        f = rep["serpents"]
        print(f"{tv} serpents (0.9.4): first blows {f['wounds']} "
              f"(pushed {f['pushes']}, to the east end "
              f"{f['pushes_to_east_end']}, to the west end "
              f"{f['pushes_to_west_end']}), kills {f['kills']}, "
              f"back {f['returns']} (at the far end "
              f"{f['return_far']}, killed again "
              f"{f['returned_killed']}), stunned "
              f"{f['stunned_frames']} frames (hidden "
              f"{f['blink_frames']}), sprint at most "
              f"{f['sprint_max']} pixels a frame ({f['sprint_2']} "
              f"frames of 2) {'PASS' if f['pass'] else 'FAIL'}")
        for e in rep["ends"]:
            print(f"{tv} end screen: {e['kind']} from frame "
                  f"{e['first_frame']}, {e['frames']} frames, score "
                  f"{e['score']}, button too early "
                  f"{e['ignored_button']}, SELECT "
                  f"{e['ignored_select']}, left by {e['left_by']}")
        print(f"{tv} end screens "
              f"{'PASS' if ends_pass(rep['ends']) else 'FAIL'}")
        for what, sf in (("route", rep["route_sound"]),
                         ("songs", rep["songs"]["facts"])):
            for f in sf["starts"]:
                extra = (f" first notes {f['first_notes']}"
                         if "first_notes" in f else
                         f" sound {f['sound']} of {f['length']} "
                         f"frames, then silence {f['silence']}"
                         f"{' (cut)' if f['cut'] else ''}"
                         if "sound" in f else "")
                print(f"{tv} {what}: frame {f['frame']} {f['song']} "
                      f"({f['why']}, mode {f['mode']}){extra}"
                      f"{'' if f.get('ok', True) else ' WRONG'}")
            print(f"{tv} {what}: songs "
                  f"{'PASS' if sf['passed'] else 'FAIL'}")
        r = rep["songs"]
        print(f"{tv} songs: {r['frames']} frames, lines {r['lines']}, "
              f"model differences {r['model_differences']}, end "
              f"screens {r['end_frames']} frames (VBLANK left "
              f"{r['end_vblank_left_min']} x 64), sound "
              f"{r['sound_cycles']} cycles, overscan left "
              f"{r['overscan_left_min']} x 64, every end in every "
              f"mode {r['facts']['all_ends']} "
              f"{'PASS' if not r['why'] else r['why']}")
        r = rep["extremes"]
        print(f"{tv} extremes: end screens {r['end_frames']} frames, "
              f"VBLANK left {r['end_vblank_left_min']} x 64, idle "
              f"end decor {r['idle'].get('end decor')}")
        print(f"{tv} extremes: seam {r['seam']['frames']} frames "
              f"{r['seam']['wrong']} wrong, counts "
              f"{r['seam']['counts']}")
        print(f"{tv} extremes: {r['frames']} frames, lines "
              f"{r['lines']}, windows {r['window_errors']}, idle "
              f"HUD {[(k, v) for k, v in r['idle'].items() if k.startswith('HUD')]} "
              f"{'PASS' if not r['why'] else r['why']}")
        for s in rep["stella"]:
            bad = [k for k, v in s["pictures"].items() if v["wrong"]]
            print(f"{tv} Stella bank {s['start_bank']}: RAM "
                  f"{s['ram_equal']} ROM reads {s['reads']} pictures "
                  f"{len(s['pictures']) - len(bad)}/"
                  f"{len(s['pictures'])} equal "
                  f"{'PASS' if not s['why'] else s['why'][:3]}",
                  flush=True)
        if "audio" in rep:
            r = rep["audio"]
            if r["recorded"]:
                print(f"{tv} Stella sound: {len(r['notes'])} notes, "
                      f"worst {r['worst_cents']} cents (mean "
                      f"{r['mean_cents']}), least likeness "
                      f"{r['least_like']}, recordings "
                      f"{len(r.get('attempts', [1]))} "
                      f"{'PASS' if r['passed'] else r['why'][:3]}")
            else:
                print(f"{tv} Stella sound: not recorded "
                      f"({'; '.join(r['why'])[:100]})")
    if a.mutations and a.stella:
        report["mutations"] = mutations(a.stella, palette["ntsc"])
        ok &= all(m.get("caught") for m in report["mutations"])
    report["pass"] = ok
    with open(os.path.join(EVID, "report.json"), "w") as f:
        json.dump(report, f, indent=1)
    for tv, s in SETS.items():
        # (bank, address $1000-$1FFF) for the simulator, (bank,
        # offset in the bank) for Stella's counters (every byte
        # read, the instructions' first bytes among them)
        with open(os.path.join(EVID, f"coverage_sets_{tv}.json"),
                  "w") as f:
            json.dump(dict(executed=s["executed"], route=s["route"],
                           stella=sorted(s["stella"])), f)
    print("ALL PASS" if ok else "FAILURES")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
