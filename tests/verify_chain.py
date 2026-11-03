"""verify_chain.py - the tests of the steps of the chain of the
book.

    python3 tests/verify_chain.py --stella PATH [--steps 1-9]
                                  [--tv ntsc,pal] [--banks 0,7]
                                  [--mutations] [--out FOLDER]

Each step of the chain (chain/NN-name, built by
tools/make_chain.py) is a whole program; it is tested as the
milestones were, with the model of the game (tests/model.py)
played as the step: Game(tv, step), the game without what the
step does not have yet. For each step and television:

A. a route of its own, planned on the step's model (the
   Director of tests/verify_0_9.py): what the step adds, and
   pictures of it;
B. the simulator, from the start banks given (0 and 7), with
   the RAM and the Superchip RAM at random: in every frame 262
   or 312 lines, VSYNC of 228 cycles, the writes to the TIA in
   their windows, the seam where the step has it, no read of
   the write side of the Superchip, the VBLANK and the overscan
   never overrun; after every frame the RAM of the step equal to
   the model's state (only the variables the step has), and the
   six sound registers (silent before step 7);
C. Stella 7.0 from bank 0: the RAM of every frame equal to the
   simulator's, the pictures equal to the ones drawn from the
   model's frame (tests/verify_0_9.py: expected, with the
   step: no HUD before step 3, no player 1 before step 4, the
   doors open in step 3, no seam before step 5);
D. with --mutations: three one-line defects in each step's
   source that the tests of the step must catch (the route in
   the simulator from bank 7 and in Stella from bank 0).

Step 9 is the 1.0, whose own tests (tests/verify_0_9.py, 1.0
evidence) go much further; here it runs the same way as the
others, with the route of the 1.0.
"""
import argparse
import copy
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "game", "assets"))
import verify_0_9 as v9                             # noqa: E402
import stella_run                                   # noqa: E402
import dungeon                                      # noqa: E402
import rules                                        # noqa: E402

STEPS = {1: "01-first-room", 2: "02-knight", 3: "03-dungeon",
         4: "04-keys-doors", 5: "05-serpents", 6: "06-serpent-king",
         7: "07-sound", 8: "08-title-and-ends", 9: "09-the-hunt"}
CHAIN = os.path.join(ROOT, "chain")
NONE, RIGHT, LEFT, DOWN, UP = v9.NONE, v9.RIGHT, v9.LEFT, v9.DOWN, \
    v9.UP


def use(step, build=None):
    """The tests of verify_0_9 on the cartridges of a step."""
    v9.STEP = step
    v9.BUILD = build or os.path.join(CHAIN, STEPS[step], "game",
                                     "build")


# ---------------------------------------------------------
# A. the routes

class Director(v9.Director):
    """The Director of tests/verify_0_9.py; its trials (where it
    tries a strike on a copy) wait for the spikes as a careful
    one does. Before the hunt of step 9 a serpent does not come
    to him: a trial walks longer, and the plates would hurt him
    on the way."""

    def trial(self):
        t = Director(self.tv, careful=False, keep=False,
                     step=self.g.nstep)
        t.g = copy.deepcopy(self.g)
        t.spikes = True
        return t

    def danger(self, swcha, margin=24):
        if getattr(self, "spikes", False) and not self.careful:
            self.careful = True         # (for the spikes only)
            try:
                return super().danger(swcha, margin)
            finally:
                self.careful = False
        return super().danger(swcha, margin)


def director(tv, step, careful=False):
    return Director(tv, careful=careful, step=step)


def route1(tv):
    d = director(tv, 1)
    d.wait(4)
    d.shot("the first room: The Broken Gate, Sir Roderick standing")
    d.wait(40)
    d.shot("40 frames later: nothing moves")
    d.wait(4)
    return d


def knight_room(d):
    """The walls, the sword, RESET and the edges in room 1 (the
    route of the 0.2, then of every milestone)."""
    d.wait(3)
    d.until_stuck(UP, "ky")
    d.wait(20, UP)
    d.shot("up into the gap of the broken gate: nothing above")
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
    d.until_stuck(LEFT, "kx")
    d.shot("left to a pillar")
    d.press()
    d.wait(2)
    d.shot("thrust left")
    d.wait(12)
    d.wait(60, RIGHT & DOWN)
    d.shot("down and right, along the walls")
    d.frame(reset=True)
    d.wait(2)
    d.shot("RESET")
    d.go(lambda p: p[1] == 69)
    d.until(LEFT, lambda g: g.kx == 0)
    d.press()
    d.wait(2)
    d.shot("thrust left, the closest to the edge")
    d.wait(12)
    d.until(RIGHT, lambda g: g.kx >= 148)
    d.press()
    d.wait(2)
    d.shot("thrust right, a shorter blade")
    d.wait(12)
    d.until(RIGHT, lambda g: g.kx == rules.X_MAX)


def route2(tv):
    d = director(tv, 2)
    knight_room(d)
    d.wait(30, RIGHT)
    d.shot("step 2: the east edge stops him")
    d.until(LEFT, lambda g: g.kx == 0)
    d.wait(30, LEFT)
    d.shot("step 2: the west edge stops him")
    d.wait(4)
    return d


# the tour of step 3: every room, by the openings and the stairs
TOUR = ["west", "east", "east", "east", "south", "north", "south",
        "west", "west", "west", "east", "south", "east", "east",
        "west", "west", "west", "south", "east", "east", "east"]


def route3(tv):
    d = director(tv, 3)
    knight_room(d)
    for way in TOUR:
        d.leave(way, f"from the {way}")
    d.go(lambda p: p[1] == 69)
    d.until_stuck(RIGHT, "kx")
    d.shot("room 15, the east plug stops him")
    d.wait(4)
    return d


def keys_and_doors(d, hunt):
    """The game of the plan: chests, keys, doors (and, with hunt,
    the serpents of each room killed first)."""
    def h():
        if hunt:
            d.hunt_all()
    d.leave("east", "a corridor")                   # 2
    h()
    d.leave("east", "the grate closed")             # 3
    h()
    d.touch()
    d.wait(20, DOWN)
    d.shot("room 3: no key, the grate stays shut")
    d.leave("west")
    d.leave("west")
    d.leave("west", "the chest")                    # 0
    h()
    d.touch()
    d.wait(2)
    d.shot("room 0: the chest open, the key, 500 points")
    d.leave("east")
    d.leave("east")
    d.leave("east")                                 # 3
    h()
    d.touch()
    d.shot("room 3: the grate opens, 1000 points, the key used")
    d.leave("south", "down the stair")              # 7
    d.leave("north", "back up: the grate stays open")
    d.leave("south")
    d.leave("west", "level 2")                      # 6
    h()
    d.leave("west", "the torches, the grate of level 2")   # 5
    h()
    d.leave("west", "the chest")                    # 4
    h()
    d.touch()
    d.shot("room 4: the chest of level 2")
    d.leave("east")                                 # 5
    h()
    d.touch()
    d.shot("room 5: the grate of level 2 opens")
    d.leave("south", "down to level 3")             # 9
    h()
    d.leave("east", "the reeds")                    # 10
    h()
    d.leave("east", "the cistern", settle=1)        # 11
    d.wait(8)
    h()
    d.touch()
    d.shot("room 11: the chest of level 3, the water")
    d.leave("west")
    h()
    d.leave("west")
    h()
    d.leave("west", "the grate of level 3")         # 8
    h()
    d.touch()
    d.shot("room 8: the grate of level 3 opens")
    d.leave("south", "down to level 4")             # 12
    h()
    d.leave("east", "the hall of coils, its chest")  # 13
    d.leave("east", "the golden gate")              # 14
    d.touch()
    d.wait(20, RIGHT)
    d.shot("room 14: no key, the gate stays shut")
    d.leave("west")                                 # 13
    h()
    d.touch()
    d.shot("room 13: the chest of level 4")
    d.leave("east")                                 # 14
    h()
    d.touch()
    d.shot("room 14: the golden gate opens")
    d.leave("east", "the throne room")              # 15


def plates_up(d):
    """Wait in this room for its plates to go up: a picture."""
    d.wait_until(lambda g: g.pf_up, limit=600)
    d.wait(2)
    d.shot(f"room {d.g.room}: the spikes up")


def route4(tv):
    d = director(tv, 4)
    d.wait(3)
    keys_and_doors(d, hunt=False)
    d.wait(4)
    d.leave("west")
    plates_up(d)
    d.wait(4)
    return d


def spikes_hurt(d):
    """On a plate of the room when it goes up: a wound."""
    xs, (y0, y1) = dungeon.plate_zones(d.g.room)
    d.go(lambda p: p[1] == y1 and p[0] == xs[0][0] - 12)
    d.wait_until(lambda g: not g.pf_up and not g.hurt)
    d.go(lambda p: p[1] == y1 and
         xs[0][0] + 4 <= p[0] <= xs[0][1] - 4)
    e0 = d.g.energy
    d.wait_until(lambda g: g.energy < e0)
    d.wait(2)
    d.shot(f"room {d.g.room}: on the plate, hurt, he flashes")
    d.until(LEFT, lambda g: not d.on_plate(g), stay=False)


def game_over(d, label):
    """East to room 2, bitten until the energy is gone."""
    d.leave("east")
    v9.die(d)
    d.wait(2)
    d.shot(label)


def route5(tv):
    d = director(tv, 5, careful=True)
    d.wait(3)
    d.leave("east", "a serpent")                    # 2
    d.bitten(0)
    d.shot("room 2: bitten, he flashes")
    d.hunt(0)
    d.wait(2)
    d.shot("room 2: the serpent killed, 100 points")
    spikes_hurt(d)
    d.leave("west")
    d.frame(reset=True)
    d.wait(3)
    keys_and_doors(d, hunt=True)
    d.wait(2)
    d.shot("room 15: step 5, the throne room still empty")
    d.leave("west")                                 # 14
    v9.die(d)
    d.wait(2)
    d.shot("GAME OVER: everything stops")
    d.wait(60, RIGHT)
    d.shot("GAME OVER: the joystick does nothing")
    d.frame(reset=True)
    d.wait(4)
    d.shot("RESET: a new game")
    d.wait(10)
    return d


def throne_fight(d, step):
    """tests/verify_0_9.py throne_fight for steps 6-8: the King
    struck anywhere on his body (no blade on the coils that does
    not count); after VICTORY, before step 8, everything stops."""
    v = v9
    d.until(RIGHT, lambda g: g.kx >= 24)
    d.frame(LEFT)
    d.wait_until(lambda g: g.vd)
    d.wait(1)
    d.shot("room 15: the King spits")
    e0 = d.g.energy
    d.wait_until(lambda g: not g.vd)
    if d.g.energy != e0 - rules.VENOM_DAMAGE:
        raise RuntimeError("route: the venom from behind missed")
    d.wait(2)
    d.shot("room 15: the venom from behind, 3 units")
    d.go(lambda p: p[0] == v.LEFT_X)
    if d.g.kdir != 0:
        d.frame(RIGHT)
    d.wait_until(lambda g: g.parry, limit=2000)
    d.wait(2)
    d.shot("room 15: the shield, the venom parried")
    d.wait_until(lambda g: not g.parry)
    e0 = d.g.energy
    d.until(RIGHT, lambda g: g.energy < e0, stay=True, limit=200)
    d.wait(2)
    d.shot("room 15: the King's bite")
    d.go(lambda p: p[0] == v.RIGHT_X)
    if d.g.kdir != 8:
        d.frame(LEFT)
    v.blows(d, "room 15: a blow, 500 points, the King flashes")
    d.wait(2)
    d.shot("room 15: the King beaten, the crown on the throne")
    x0, x1, t0, t1 = v.CROWN_GOAL
    d.go(lambda p: x0 <= p[0] <= x1 and t0 <= p[1] <= t1)
    if d.g.kdir != 8:
        d.frame(LEFT)
    d.press()
    d.wait_until(lambda g: g.won, limit=20)
    d.wait(2)
    d.shot("VICTORY: the crown broken")
    if step < 8:
        d.wait(80, RIGHT)
        d.shot("VICTORY: everything stops")
        d.frame(reset=True)
        d.wait(4)
        d.shot("RESET: a new game")
        return
    d.wait_until(lambda g: not g.screen)
    d.wait(2)
    d.shot("the VICTORY screen")
    d.wait_until(lambda g: g.won >= g.t["VIC_FRAMES"] +
                 g.t["END_FRAMES"])
    d.wait(5)
    d.press()
    d.wait(3)
    d.shot("back to the title after VICTORY")
    d.wait(30)


def to_the_king(d):
    d.leave("east", "a serpent")                    # 2
    d.hunt(0)
    d.leave("west")
    keys_and_doors(d, hunt=True)


def route6(tv, step=6):
    d = director(tv, step, careful=True)
    d.wait(3)
    if step == 7:
        d.select()                  # MUSIC -> SOUND FX
        d.wait(2)
    to_the_king(d)
    throne_fight(d, step)
    d.wait(10)
    if step == 7:
        d.select()                  # SILENT
        d.wait(20)
        d.select()                  # MUSIC again
        d.wait(4)
        d.shot("SELECT in the game: the music again")
        d.wait(60)
    game_over(d, "GAME OVER: everything stops")
    d.wait(30)
    d.frame(reset=True)
    d.wait(4)
    d.shot("RESET after GAME OVER: a new game")
    d.wait(30)
    return d


def route7(tv):
    return route6(tv, step=7)


def route8(tv):
    """The route of the 1.0 (tests/verify_0_9.py route) without
    the hunt: one blow kills a serpent, the King is struck
    anywhere."""
    d = director(tv, 8, careful=True)
    d.wait(6)
    d.shot("title")
    d.wait(60)
    for label in ("SOUND FX", "SILENT", "MUSIC again"):
        d.select()
        d.wait(2)
        d.shot(f"title, {label}")
        d.wait(10)
    d.select()                      # the game in the SOUND FX mode
    d.wait(4)
    d.press()
    d.shot("start: the broken gate")
    knight_room(d)
    to_the_king(d)
    throne_fight(d, 8)
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
    d.select()
    d.wait(4)
    d.shot("SELECT in the game: nothing")
    d.leave("east")
    d.bitten(0)
    d.hunt(0)
    start = v9.die(d)
    d.wait(2)
    d.shot("GAME OVER, the lament")
    d.wait_until(lambda g: not g.screen)
    d.wait(2)
    d.shot("the GAME OVER screen")
    d.wait(max(0, start + v9.song_frames(d.tv, "gameover") +
               v9.SILENCE - len(d.inputs)))
    d.frame(reset=True)
    d.wait(4)
    d.shot("RESET on the GAME OVER screen: a new game")
    d.wait(30)
    d.leave("east")
    v9.die(d)
    d.wait_until(lambda g: g.over >= g.t["GO_FRAMES"] +
                 g.t["END_FRAMES"])
    d.wait(10)
    d.press()
    d.wait(3)
    d.shot("back to the title after GAME OVER")
    d.wait(30)
    return d


def route9(tv):
    return v9.route(tv)


ROUTES = {1: route1, 2: route2, 3: route3, 4: route4, 5: route5,
          6: route6, 7: route7, 8: route8, 9: route9}


# ---------------------------------------------------------
# B and C. one step, one television

def facts(step, d):
    """What the route of the step must have done (its model)."""
    g = d.g
    rooms_seen = sorted({s.room for s in d.states if s.screen})
    out = dict(frames=len(d.inputs), shots=len(d.shots),
               rooms=rooms_seen)
    want = {1: lambda: rooms_seen == [1],
            2: lambda: rooms_seen == [1],
            3: lambda: rooms_seen == list(range(16)),
            4: lambda: max(s.opened for s in d.states) == 0xFF,
            5: lambda: any(s.over for s in d.states),
            6: lambda: any(s.won for s in d.states) and
            any(s.over for s in d.states),
            7: lambda: any(s.won for s in d.states) and
            any(s.over for s in d.states) and
            {s.mode for s in d.states} == {0, 1, 2},
            8: lambda: any(s.won for s in d.states) and
            any(s.over for s in d.states),
            9: lambda: any(s.won for s in d.states)}
    out["pass"] = want[step]()
    out["score_max"] = max(s.score for s in d.states)
    return out


def run(step, tv, stella, palette, banks=(0, 7), stella_banks=(0,),
        d=None, keep=None, quick=False):
    """The tests of one step on one television (with d: that
    route; quick: the mutations, stopping at a difference)."""
    use(step, v9.BUILD if quick else None)
    rom = os.path.join(v9.BUILD, f"scalecrown_{tv}.bin")
    pal = palette[tv] if palette else None
    t0 = time.time()
    d = d or ROUTES[step](tv)
    rep = dict(step=step, tv=tv, route=facts(step, d), sim=[],
               stella=[])
    ok = rep["route"]["pass"]
    sims = {}
    for b in banks:
        s = v9.simulate(tv, b, 11 + b, d.inputs,
                        model=d if quick else None, quick=quick)
        sims[b] = s
        why = v9.sim_checks(tv, s)
        diffs = v9.compare_model(d, s)
        if s.get("early"):
            e = s["early"][0]
            diffs = diffs or [e]
        if diffs:
            e = diffs[0]
            why.append(f"{len(diffs)} differences from the model "
                       f"(first: frame {e['frame']} {e['var']} "
                       f"model {e['model']} RAM {e['ram']})")
        rep["sim"].append(dict(
            start_bank=b, frames=len(d.inputs), lines=s["lines"],
            vsync=s["vsync"], window_errors=s["window_error_count"],
            seam=dict(frames=s["seam"]["frames"],
                      wrong=s["seam"]["wrong"]),
            vblank_left_min=s["vblank_left_min"],
            overscan_left_min=s["overscan_left_min"],
            stack_lowest=s["stack_lowest"],
            model_differences=len(diffs), why=why))
        ok &= not why
        if quick and why:
            rep["pass"] = False
            return rep
    shots = sorted(d.shots)
    if stella:
        for b in stella_banks:
            st = stella_run.run(stella, rom, len(d.inputs),
                                joystick=lambda k: d.inputs[k - 1],
                                shots=shots, startbank=b, keep=keep)
            sim = sims.get(b) or v9.simulate(tv, b, 11 + b, d.inputs)
            n = len(d.inputs)
            same = sum(1 for a, c in zip(st["ram"], sim["ram"][1:])
                       if a is not None and a == c)
            why, pics = [], {}
            if same != n:
                bad = [k for k, (a, c) in enumerate(
                    zip(st["ram"], sim["ram"][1:]), 1)
                    if a is None or a != c][:3]
                why.append(f"Stella RAM {same}/{n} (frames {bad})")
            for k in shots:
                if k not in st["shots"]:
                    why.append(f"frame {k}: no picture")
                    continue
                pic = v9.expected(tv, d.states[k - 1])
                cmp = v9.compare(pic, st["shots"][k], tv, pal)
                pics[k] = dict(what=d.shots[k], wrong=cmp["wrong"],
                               first=cmp["first"])
                if keep:
                    v9.save_expected(pic, pal, os.path.join(
                        keep, f"expected_{tv}_f{k:04d}.png"))
                if cmp["wrong"]:
                    why.append(f"frame {k} ({d.shots[k]}): "
                               f"{cmp['wrong']} pixels differ "
                               f"({cmp['first']})")
            rep["stella"].append(dict(start_bank=b, ram_equal=f"{same}/{n}",
                                      seconds=st["seconds"],
                                      version=st["version"],
                                      pictures=pics, why=why))
            ok &= not why
            shutil.rmtree(st["work"], ignore_errors=True)
            if quick and why:
                break
    rep["seconds"] = round(time.time() - t0)
    rep["pass"] = bool(ok)
    return rep


# ---------------------------------------------------------
# D. the mutations: three for each step, in the source of the step
# (file, the line as it is, the line mutated, what it breaks)

MUTATIONS = {
    1: [("room_kernel.asm", "        lda     znpf2",
         "        lda     znpf1", "PF2 of line A0 from the wrong course"),
        ("main.asm", "        lda     #START_TOP",
         "        lda     #START_TOP+2", "Sir Roderick a step lower"),
        ("hud.asm", "        ldy     #25             ; lines 0-24: black",
         "        ldy     #24             ; lines 0-24: black",
         "a black line too few: frames of 261 lines")],
    2: [("knight.asm",
         "        adc     #H_FRAC         ; fraction carries",
         "        adc     #H_FRAC+1       ; fraction carries",
         "the walk a little faster"),
        ("knight.asm",
         "        adc     #KNIGHT_H-1     ; bottom line, and back",
         "        adc     #KNIGHT_H-3     ; bottom line, and back",
         "the box two lines short: into a wall"),
        ("knight.asm", "        ldx     #3              ; width: 8 pixels",
         "        ldx     #2              ; width: 8 pixels",
         "a blade of 4 pixels")],
    3: [("knight.asm", "        lda     #0              ; in on the west side",
         "        lda     #1              ; in on the west side",
         "in a column too far east"),
        ("hud.asm", "        lda     bar1",
         "        lda     bar2", "the energy bar: PF1 from PF2"),
        ("main.asm", "        lda     PLUG,x          ; the ball on or off",
         "        lda     #0              ; the ball on or off",
         "no plug")],
    4: [("things.asm", "        lda     #CHEST_BCD",
         "        lda     #DOOR_BCD", "a chest worth a door's points"),
        ("things.asm", "        lda     #SPK_UP",
         "        lda     #SPK_UP+1", "the spikes up a frame longer"),
        ("room_kernel.asm", "        nop",
         "", "PF2 of line B3 too early: over the right half")],
    5: [("things.asm", "        lda     #SERPENT_BCD",
         "        lda     #CHEST_BCD", "a serpent worth a chest's points"),
        ("things.asm", "        lda     #BITE_FRAMES",
         "        lda     #BITE_FRAMES+1", "a wound a frame longer"),
        ("room_kernel.asm", "        ldx     zcoarse         ; 17",
         "        ldx     zref            ; 17",
         "the seam: its delay from the wrong byte")],
    6: [("things.asm", "        lda     #KHIT_FRAMES",
         "        lda     #KHIT_FRAMES+1", "the King's flash a frame longer"),
        ("things.asm", "        adc     #VEN_FRAC",
         "        adc     #VEN_FRAC+1", "the venom a little faster"),
        ("main.asm", "        lda     #NUS_KING",
         "        lda     #NUS_CROWN", "the King four times as wide")],
    7: [("sound.asm", "        lda     STEPLEN,x",
         "        lda     STEPLEN+1,x", "the music out of step"),
        ("sound.asm", "        lda     SFX_V,y",
         "        lda     SFX_F,y", "the volume of the effects"),
        ("main.asm", "        bcc     fr_mode",
         "        bcs     fr_mode",
         "SELECT in the game: always back to MUSIC")],
    8: [("main.asm", "        bcc     fr_mode",
         "        bcs     fr_mode",
         "SELECT on the title: always back to MUSIC"),
        ("main.asm", "        cmp     #VIC_FRAMES+END_FRAMES",
         "        cmp     #VIC_FRAMES+END_FRAMES+1",
         "the VICTORY screen a frame longer before the button"),
        ("main.asm", "        sta     SCW,x           ; the empty line",
         "        sta     SCW+1,x         ; the empty line",
         "the digits of the end screen a line off")],
    9: [("things.asm", "        adc     #KNOCK_PX",
         "        adc     #KNOCK_PX+1", "the push of a blow a pixel more"),
        ("things.asm", "        lda     #STUN_FRAMES",
         "        lda     #STUN_FRAMES+1", "the stun a frame longer"),
        ("things.asm", "        lda     #KING_HEAD+1    ; his head only",
         "        lda     #KING_H+1       ; his head only",
         "the King struck on his body again")]}


def mutations_of(step):
    return MUTATIONS.get(step, [])


def mutate(step, mut, work):
    """The step copied into work with one line changed, built:
    its build folder, or None if it does not build."""
    name, old, new, _ = mut
    src = os.path.join(CHAIN, STEPS[step])
    dst = os.path.join(work, STEPS[step])
    shutil.rmtree(dst, ignore_errors=True)
    shutil.copytree(src, dst, ignore=shutil.ignore_patterns(
        "build", "generated", "__pycache__"))
    p = os.path.join(dst, "game", "src", name)
    lines = open(p).read().split("\n")
    hits = [i for i, ln in enumerate(lines) if ln.rstrip() == old]
    if len(hits) != 1:
        raise RuntimeError(f"step {step}, {name}: the line "
                           f"{old.strip()!r} is there {len(hits)} "
                           "times")
    if new:
        lines[hits[0]] = new
    else:
        del lines[hits[0]]
    open(p, "w").write("\n".join(lines))
    r = subprocess.run([sys.executable, "tools/build.py"], cwd=dst,
                       capture_output=True, text=True)
    if r.returncode:
        return None
    return os.path.join(dst, "game", "build")


def run_mutations(step, tv, stella, palette, d):
    out = []
    work = tempfile.mkdtemp(prefix="chain_mut_")
    try:
        for mut in mutations_of(step):
            build = mutate(step, mut, work)
            if build is None:
                out.append(dict(file=mut[0], what=mut[3],
                                caught=True, how="it does not build"))
                continue
            use(step, build)
            rep = run(step, tv, stella, palette, banks=(7,),
                      stella_banks=(0,), d=d, quick=True)
            why = [w for s in rep["sim"] + rep["stella"]
                   for w in s["why"]]
            out.append(dict(file=mut[0], line=mut[2].strip(),
                            what=mut[3], caught=bool(why),
                            how=why[0] if why else ""))
            print(f"  mutation step {step} {tv} {mut[0]}: "
                  f"{'caught' if why else 'NOT CAUGHT'} "
                  f"({why[0][:100] if why else mut[3]})", flush=True)
    finally:
        shutil.rmtree(work, ignore_errors=True)
        use(step)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stella")
    ap.add_argument("--steps", default="1-9")
    ap.add_argument("--tv", default="ntsc,pal")
    ap.add_argument("--banks", default="0,7")
    ap.add_argument("--mutations", action="store_true")
    ap.add_argument("--redo", action="store_true",
                    help="run again what has a report already")
    ap.add_argument("--out", default=os.path.join(
        ROOT, "evidence", "chain", "workspace", "d2"))
    a = ap.parse_args()
    lo, _, hi = a.steps.partition("-")
    steps = list(range(int(lo), int(hi or lo) + 1))
    banks = tuple(int(b) for b in a.banks.split(","))
    palette = json.load(open(os.path.join(ROOT, "game", "assets",
                                          "palette_stella.json")))
    os.makedirs(a.out, exist_ok=True)
    allok = True
    for step in steps:
        for tv in a.tv.split(","):
            path = os.path.join(a.out, f"step{step:02d}_{tv}.json")
            keep = os.path.join(a.out, "pictures",
                                f"step{step:02d}_{tv}")
            if os.path.exists(path) and not a.redo:
                rep = json.load(open(path))     # done before (the
                allok &= rep["pass"]            # machine restarts)
                print(f"step {step} {tv}: done before, "
                      f"{'PASS' if rep['pass'] else 'FAIL'}")
                continue
            use(step)
            d = ROUTES[step](tv)
            rep = run(step, tv, a.stella, palette, banks=banks, d=d,
                      keep=keep)
            if a.mutations:
                rep["mutations"] = run_mutations(step, tv, a.stella,
                                                 palette, d)
                rep["pass"] &= all(m["caught"]
                                   for m in rep["mutations"])
            rep["shots"] = {k: v for k, v in sorted(d.shots.items())}
            json.dump(rep, open(path, "w"), indent=1)
            allok &= rep["pass"]
            whys = [w for s in rep["sim"] + rep["stella"]
                    for w in s["why"]]
            print(f"step {step} {tv}: {'PASS' if rep['pass'] else 'FAIL'}"
                  f" route {rep['route']['frames']} frames, "
                  f"{len(rep['route']['rooms'])} rooms, "
                  f"{rep['route']['shots']} pictures; "
                  f"{rep['seconds']} s"
                  + (f"; {whys[0][:160]}" if whys else ""),
                  flush=True)
    print("CHAIN TESTS PASS" if allok else "CHAIN TESTS FAIL")
    return 0 if allok else 1


if __name__ == "__main__":
    sys.exit(main())
