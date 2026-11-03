"""model.py - Scalecrown played in Python, frame by frame
(milestones 0.2-0.9.4).

What the cartridge must do, written from the design (rules.py,
dungeon.py, rooms.py, art.py) and the rules of its design,
not from the
6507 code: the tests run the same joystick through this model
and through the cartridge and compare, frame by frame, the
state of the game; the expected pictures are drawn from the
model's state.

A frame, in the order the cartridge does it:
1. the buttons: pressed = down now and up in the frame before
   (fire, SELECT and RESET);
2. on the title SELECT chooses the next sound mode (MUSIC,
   SOUND FX, SILENT, then MUSIC again), then the button or RESET
   starts a game; in a game RESET starts it again (SELECT does
   nothing there); after GAME OVER (0.6) nothing moves: a count
   of rules.GAME_OVER_S, then (0.8) the end screen: the same
   count goes on for rules.END_S more, then the button goes
   back to the title (RESET on an end screen starts a game);
   VICTORY the same, after rules.VICTORY_S; a new game, GAME
   OVER, VICTORY and the title start their song (0.8: the
   theme, the lament, the fanfare), silencing what played;
   otherwise Sir Roderick moves:
   - in a thrust he stands still until it is over;
   - the button starts a thrust (rules.THRUST_S) and asks for
     the sound of the sword;
   - left or right: the step of this frame (whole part and
     fraction of rules.WALK_PX_S), tried against the walls
     (and the plugs: dungeon.walls); past the edge of the
     screen he goes through the opening to the room beside
     and comes in on the other side, at the same height (not
     up or down in that frame);
   - then up or down: a step of 2 lines when the fraction of
     rules.CLIMB_STEPS_S carries, tried against the walls;
     at the bottom of the screen the stair takes him to the
     room below, in at the top; at the top the stair to the
     room above, in at the bottom, but not in the first level
     (the broken gate of room 1); a stair is a step, and
     (0.9) asks for the sound of the steps;
   - the pose: WALK every STRIDE units walked while he
     moves, 0 when he does not;
3. a new room: the plates of the spikes down, for the time
   of the level (rules.py), and drawn down; its guards (0.6)
   at their start, alive, facing left, no fraction of their
   crawl yet (the army is infinite);
4. what the things of the room say (0.5): the thing of player
   1 open or closed; the collision map that Sir Roderick will
   meet in the next frame has the door open or closed; the
   HUD shows the key if he has one, or GAME OVER;
5. player 1 (0.6, dungeon.py): in band A the thing and the
   guard of the band, each when it is there, both in turn
   (the thing in even frames), or nothing; in band B, below
   the seam, the first guard, or nothing once it is dead;
   Sir Roderick flashes while a wound counts down;
   -- here the picture of the frame is drawn: `pic` keeps the
   state it shows --
6. in the overscan of a game (not after GAME OVER):
   - the plates turn when their time is over (down for the
     time of the level, up for rules.SPIKES_UP_S), and are
     drawn so from the next frame;
   - a count of the hurt goes down; when it is over and the
     plates are up, if his top line puts his feet (the last
     8 lines of his box) on the plates' lines and the middle
     of his feet is over a plate (dungeon.plate_zones), he
     loses rules.SPIKE_DAMAGE units (not below 0), the count
     starts again (rules.HURT_S) and the hurt sounds;
   - the guards (0.6), the first then the second, each alive:
     (0.9.4) a stunned one only counts its stun down; a
     serpent the blade touches (its pixels and lines meet
     the serpent's 8 x 16) dies, rules.SERPENT_POINTS (0.9.4:
     the first blow wounds it: pushed rules.KNOCK_PX away
     along its path, facing him, stunned for rules.STUN_S,
     the sound of a blow; the second kills it, and it comes
     back after rules.RESPAWN_S at the end of its path
     farther from him); one whose box meets his, when no
     wound counts down, bites: rules.BITE_DAMAGE, a count of
     rules.BITE_S; then they crawl a pixel when the fraction
     of their speed carries (rules.crawl), turning at the
     ends of their path (the King only sways), or chase him
     (0.9.2-0.9.4: on his lines, his column on the path,
     rules.sprint pixels a frame); a dead one counts down
     to its return;
   - if the thing of the room is closed and he touches it
     (dungeon.zone): a chest opens, he has the key of the
     level, rules.CHEST_POINTS; a door opens only if he has
     the key of its level, which is used up, and
     rules.DOOR_POINTS; each with its sound;
   - energy 0: GAME OVER (he stands, no flash, its sound);
   - in the throne room (0.7), in place of the guards, the
     Serpent King (throne(), dungeon.THRONE, rules.py): his
     flash after a blow or a blow of the blade (eight beat
     him: the crown), his bite, the venom flying (stone, the
     edge, Sir Roderick: the shield parries what comes from
     the side he faces, not in the thrust, and he shows the
     parry), or his step towards Sir Roderick and his spit;
     the crown struck: VICTORY (everything stops, after
     rules.VICTORY_S the end screen);
7. in the overscan the sound (tests/sound_model.py).

The chain of the book: Game(tv, step) plays step 1-9
of the chain (chain/NN-name), the
game without what the step does not have yet; step 9, the
default, is the whole game, the 1.0:
- 1: the first room, Sir Roderick standing (no buttons);
- 2: the joystick, the walls, the sword, RESET; the edges of
  the screen and the gaps of the stairs stop him;
- 3: the 16 rooms, the openings, the stairs, the plugs, the
  HUD (score 0, the energy full); every door open;
- 4: player 1 (the thing of the room over the whole room), the
  chests, the keys, the doors, the plates going up and down,
  the points;
- 5: the guards (one blow kills, no chase), the seam, the
  bite, the spikes that hurt, the flash, GAME OVER (everything
  stops; RESET); the throne room has no King and no guard;
- 6: the throne room, the King (struck anywhere on his body),
  the venom, the shield, the crown, VICTORY (everything stops);
- 7: the sound: SELECT in a game chooses the mode, a new game
  starts the theme;
- 8: the title and the end screens (no hunt: the 0.9.4 rules
  of the serpents and the King's head are step 9's);
- 9: the hunt.
Steps 1-7 start the game at power-on (no title).
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "game",
                                "assets"))
import art                                      # noqa: E402
import dungeon                                  # noqa: E402
import rules                                    # noqa: E402
import sound_model                              # noqa: E402

RIGHT, LEFT, DOWN, UP = 0x80, 0x40, 0x20, 0x10
FIRE, SELECT, RESET = 0x80, 0x02, 0x01
# the effects (sfx.ORDER)
SWORD, CHEST, DOOR, HURT, BITE, KILL, GAMEOVER = 1, 2, 3, 4, 5, \
    6, 7
SPIT, PARRY, KING_HIT, KING_DIES, VICTORY = 8, 9, 10, 11, 12
STAIR = 13                                      # 0.9
# the lines of the blade in the thrust: the pair coloured
# "blade" (art.py)
BLADE_LINE = 12
# the Superchip RAM of the guards (0.6)
SC_SX, SC_SD, SC_LIVE, SC_ACC, SC_HM = 60, 62, 64, 65, 66
# 0.9.4: the stun or the return of each guard, the sprint
SC_GT, SC_SPR = 75, 77
# the Superchip RAM of the Serpent King (0.7)
SC_KT, SC_KH, SC_KF, SC_KS, SC_VP, SC_VD, SC_VA, SC_CROWN = \
    67, 68, 69, 70, 71, 72, 73, 74
NUS_KING, NUS_CROWN = 0x35, 0x37
# the songs (0.8: score.SONG_ORDER, 2 x the song in the RAM)
SONG_THEME, SONG_GAMEOVER, SONG_VICTORY = 0, 2, 4


# the RAM of each step: a name of state() and the step that
# brings it (the others are there from step 1)
STATE_STEP = dict(held=2, pressed=2, kdist=2, hacc=2, vacc=2,
                  thrust=2, plug=3, energy=3, score=3, ox=4, oy=4,
                  odir=4, onus=4, key=4, opened=4, spk=4, spup=4,
                  zcoarse=5, zref=5, over=5, hurt=5, won=6,
                  parry=6, mode=7, sfxreq=7, song=7)
SC_STEP = {SC_HM: 5, SC_LIVE: 5, SC_ACC: 5, SC_SX: 5, SC_SX + 1: 5,
           SC_SD: 5, SC_SD + 1: 5, SC_GT: 9, SC_GT + 1: 9,
           SC_SPR: 9}


class Game:
    def __init__(self, tv, step=9):
        self.tv = tv
        self.nstep = step               # of the chain
        self.t = rules.table(tv)
        self.frames = 0
        self.screen = 0
        self.room = 0
        self.held = 0
        self.pressed = 0
        self.kx = self.ky = self.kdir = self.kpose = 0
        self.kdist = self.hacc = self.vacc = self.thrust = 0
        self.ox = self.oy = self.odir = 0
        self.onus = 0
        self.score = 0
        self.energy = 0
        self.key = self.opened = self.hurt = 0
        self.spk = self.spup = 0
        self.pf_up = 0              # the plates as drawn
        self.map_open = False       # the door in the map
        self.over = 0               # 0.6: GAME OVER count
        self.won = 0                # 0.7: VICTORY count
        self.parry = 0              # 0.7: the parry
        # the King (0.7): top line, blows, flash, time before a
        # spit; the venom: first pixel, 0/1 right/2 left, its
        # fraction; the crown (0 the King, 1, 2 broken); the
        # Superchip bytes of these the cartridge has written
        self.kt = self.kh = self.kf = self.ks = 0
        self.vp = self.vd = self.va = 0
        self.crown = 0
        self.known = set()
        self.sx, self.sd = [0, 0], [8, 8]   # the guards
        self.live, self.acc = 0, 0
        self.gt, self.spr = [0, 0], 0       # 0.9.4
        self.zcoarse = self.zref = self.hm = 0  # the seam
        self.band_a = self.band_b = None
        self.pic = {}               # what the frame showed
        self.shown = None
        self.mode = 0
        self.request = 0
        self.song = 0               # 0.8: 2 x the song
        self.restart = False        # a song to start
        self.started = False        # ... started in this frame
        self.sound = sound_model.Sound(tv)
        self.audio = self.sound.reg
        self.silent = dict(self.sound.reg)  # before step 7
        if step < 8:                    # no title: a game at once
            self.new_game()

    # -- the map -------------------------------------------
    def guards_of(self, r):
        """The guards of room r in this step (before step 6 the
        Serpent King is not one: the throne room is empty)."""
        if self.nstep < 6 and dungeon.throne(r):
            return []
        return dungeon.ROOMS[r]["guards"]

    def walls(self):
        return dungeon.walls(self.room, closed=not self.map_open)

    def free(self, x, top):
        """Sir Roderick's 8 x 24 box at column x, top line top,
        touches no stone (every pixel and line of it tested)."""
        w = self.walls()
        x0 = x + rules.FIRST_PIXEL
        for line in range(top, top + rules.KNIGHT_H):
            for px in range(x0, x0 + rules.KNIGHT_W):
                if w[line // 16][px // 8]:
                    return False
        return True

    # -- a frame -------------------------------------------
    def new_game(self):
        st = dungeon.START
        self.room = st["room"]
        self.screen = self.room + 1
        self.kx, self.ky = st["x"], st["top"]
        self.kdir = 0 if st["facing"] == "right" else 8
        self.kpose = self.kdist = self.hacc = self.vacc = 0
        self.thrust = 0
        self.score = 0
        self.energy = rules.ENERGY
        self.key = self.opened = self.hurt = 0
        self.over = self.won = self.parry = 0
        self.crown = 0
        if self.nstep >= 6:
            self.known.add(SC_CROWN)
        self.shown = None
        if self.nstep >= 7:
            self.theme()

    def theme(self):
        """The theme from its start (0.8)."""
        self.song, self.restart = SONG_THEME, True

    def step(self, swcha=0xFF, fire=False, reset=False,
             select=False, poke=None):
        """One frame with this joystick (SWCHA: 0 = pushed).
        poke (the tests, 0.8): values put in after the logic,
        before the picture, as the tests put them in the RAM of
        the cartridge (over, won, song, score, request; restart
        True: a song to start, $FF in smode)."""
        self.frames = (self.frames + 1) & 0xFF
        down = (FIRE if fire else 0) | (RESET if reset else 0) | \
            (SELECT if select else 0)
        if self.nstep < 2:               # no buttons yet
            down = 0
        self.pressed = down & ~self.held
        self.held = down
        self.logic(swcha)
        for name, val in (poke or {}).items():
            setattr(self, name, val)
        self.pic = self.picture_state()
        if self.screen:
            self.things()
        if self.nstep >= 7:
            self.audio = self.sound.frame(self.mode, self.request,
                                          self.song, self.restart)
        else:
            self.audio = dict(self.silent)
        self.started = self.restart     # a song started (0.8)
        self.request = 0
        self.restart = False

    def ends(self):
        """An end screen (0.8): RESET starts a game (True); over
        or won go on counting rules.END_S more, then the button
        goes back to the title and its theme."""
        if self.pressed & RESET:
            self.new_game()
            return True
        name, end = ("won", "VIC_FRAMES") if self.won else \
            ("over", "GO_FRAMES")
        if getattr(self, name) < self.t[end] + self.t["END_FRAMES"]:
            setattr(self, name, getattr(self, name) + 1)
        elif self.pressed & FIRE:
            self.over = self.won = 0
            self.theme()
        self.shown = None
        return False

    def logic(self, swcha):
        if self.screen == 0 and (self.over or self.won):
            if not self.ends():
                return
        elif self.screen == 0:
            if self.pressed & SELECT:
                self.mode = (self.mode + 1) % 3
            if self.pressed & (FIRE | RESET):
                self.new_game()
            else:
                self.shown = None
                return
        else:
            if self.nstep == 7 and self.pressed & SELECT:
                self.mode = (self.mode + 1) % 3     # step 7 only
            if self.pressed & RESET:
                self.new_game()
            elif self.won or self.over:
                if self.nstep < 8:       # steps 5-7: it stops
                    pass
                else:
                    name, end = ("won", "VIC_FRAMES") if self.won \
                        else ("over", "GO_FRAMES")
                    if getattr(self, name) < self.t[end]:
                        setattr(self, name, getattr(self, name) + 1)
                    else:
                        self.screen = 0     # the end screen (0.8)
                        if not self.ends():
                            return
            elif self.nstep >= 2:
                self.knight(swcha)
        r = self.room
        lv = dungeon.ROOMS[r]["level"]
        st = self.nstep
        if self.shown != self.screen:
            self.shown = self.screen
            g = self.guards_of(r)
            if st >= 4:
                self.spk = rules.spike_frames(self.tv)[0][lv - 1]
                self.spup = self.pf_up = 0
                self.onus = 5 if g and g[0]["kind"] == "king" else 0
            if st >= 5:
                self.acc, self.live, self.sd = 0, 3, [8, 8]
                self.sx = [g[k]["x"] if len(g) > k
                           else dungeon.ABSENT_X for k in (0, 1)]
                self.place_seam()
            if st >= 9:
                self.gt, self.spr = [0, 0], 0   # 0.9.4
            if st >= 6 and dungeon.throne(r):   # 0.7: the King
                self.kt = dungeon.THRONE["start"]
                self.kh = self.kf = self.vd = self.va = 0
                self.ks = self.t["SPIT_FIRST"]
                self.known |= {SC_KT, SC_KH, SC_KF, SC_KS, SC_VD,
                               SC_VA}
        door = dungeon.door(r)
        self.map_open = st < 4 or not door or bool(
            self.opened & dungeon.door_bit(lv))
        if st >= 4:
            self.bands()

    def thing_kind(self):
        """The thing of band A as it is now, or None (none, or
        the gate once open)."""
        t = dungeon.thing_item(self.room)
        if not t:
            return None
        k = t["kind"]
        if self.opened & dungeon.thing_bit(self.room):
            k = dungeon.open_kind(k)
        return None if k == "none" else k

    def bands(self):
        """What player 1 shows in the two bands (0.6); in the
        throne room (0.7) the King or the crown."""
        r = self.room
        if self.nstep >= 6 and dungeon.throne(r):
            self.band_b = None
            th = dungeon.THRONE
            if self.crown:
                c = th["crown"]
                a = dict(kind="crown" if self.crown == 1
                         else "crown_broken", x=c["x"], top=c["top"],
                         dir=0, spit=False, flash=False)
                self.onus = NUS_CROWN
            else:
                a = dict(kind="king", x=th["x"], top=self.kt,
                         dir=8 if self.kx < dungeon.spit_left() else 0,
                         spit=bool(self.vd),
                         flash=bool(self.kf and
                                    self.frames & rules.FLASH_FRAMES))
                self.onus = NUS_KING
            a["turns"] = False
            self.band_a = a
            self.ox, self.oy, self.odir = a["x"], a["top"], a["dir"]
            return
        seam = dungeon.seam(r) if self.nstep >= 5 else None
        g = self.guards_of(r) if self.nstep >= 5 else []
        slot = 1 if seam is not None else 0
        t = dungeon.thing_item(r)
        tk = self.thing_kind()
        guard = len(g) > slot and self.live >> slot & 1 and \
            not self.blinks(slot)
        if guard and (not tk or self.frames & 1):
            a = dict(kind=g[slot]["kind"], x=self.sx[slot],
                     top=g[slot]["top"], dir=self.sd[slot])
        elif tk:
            a = dict(kind=tk, x=t["x"], top=t["top"], dir=8)
        else:
            a = dict(kind="none", x=t["x"] if t else 1,
                     top=t["top"] if t else dungeon.NONE_TOP, dir=8)
        a["turns"] = bool(guard and tk)     # two in turn
        self.band_a = a
        self.ox, self.oy, self.odir = a["x"], a["top"], a["dir"]
        self.band_b = None
        if seam is not None:
            self.band_b = dict(
                kind=g[0]["kind"] if self.live & 1 and
                not self.blinks(0) else "none",
                x=self.sx[0], top=g[0]["top"], dir=self.sd[0])
            self.zref = self.sd[0]

    def blinks(self, k):
        """0.9.4: guard k stunned, hidden every other
        FLASH_FRAMES frames."""
        return bool(self.gt[k] and self.frames & rules.FLASH_FRAMES)

    def place_seam(self):
        """The column of the first guard for the seam: the
        delay before RESP1 and the fine move, as place does
        it for the column - 3 (x - 3 = 15 q + m, q + 1 counts,
        HMP1 moves the rest; the RESP1 of the seam writes a
        cycle after place's)."""
        q, m = divmod(self.sx[0] - 3, 15)
        self.zcoarse = q + 1
        self.hm = (((m - 15) & 0xFF) ^ 7) << 4 & 0xFF

    def flash(self):
        return bool(self.hurt and self.frames & rules.FLASH_FRAMES
                    and self.kpose != rules.THRUST_POSE)

    def things(self):
        """The overscan of a game (0.5-0.7)."""
        if self.over or self.won or self.nstep < 4:
            return
        st = self.nstep
        rm = dungeon.ROOMS[self.room]
        lv = rm["level"]
        down, up, hurt = rules.spike_frames(self.tv)
        self.spk = (self.spk - 1) % 256
        if self.spk == 0:
            self.spup ^= 1
            self.spk = up if self.spup else down[lv - 1]
            self.pf_up = self.spup
        if st >= 5 and self.hurt:
            self.hurt -= 1
        if st >= 5 and not self.hurt and self.spup and \
                rm.get("plate") is not None:
            xs, (y0, y1) = dungeon.plate_zones(self.room)
            if y0 <= self.ky <= y1 and any(a <= self.kx <= b
                                           for a, b in xs):
                self.energy = max(0, self.energy - rules.SPIKE_DAMAGE)
                self.hurt = hurt
                self.request = HURT
        if st >= 6 and dungeon.throne(self.room):
            self.throne()
        elif st >= 5 and not dungeon.throne(self.room):
            self.guards()
        bit = dungeon.thing_bit(self.room)
        z = dungeon.zone(self.room)
        if bit and not self.opened & bit and \
                z[0][0] <= self.kx <= z[0][1] and \
                z[1][0] <= self.ky <= z[1][1]:
            if rm.get("chest"):
                self.opened |= bit
                self.key = lv
                self.request = CHEST
                self.score += rules.CHEST_POINTS
            elif self.key == lv:
                self.opened |= bit
                self.key = 0
                self.request = DOOR
                self.score += rules.DOOR_POINTS
        if st >= 5 and self.energy == 0:
            self.over = 1
            self.hurt = self.kpose = self.thrust = self.parry = 0
            if st >= 6:
                self.vd = 0
                self.known.add(SC_VD)
            self.request = GAMEOVER
            if st >= 8:
                self.song, self.restart = SONG_GAMEOVER, True

    # -- the throne room (0.7) -----------------------------
    def wound(self, n):
        self.energy = max(0, self.energy - n)
        self.hurt = self.t["BITE_FRAMES"]

    def blade_on(self, x0, x1, t0, t1):
        """The blade of a thrust on pixels x0-x1, lines t0-t1."""
        b = self.blade()
        if not b:
            return False
        y0 = self.ky + BLADE_LINE
        return b[0] <= x1 and b[0] + b[1] - 1 >= x0 and \
            y0 <= t1 and y0 + 1 >= t0

    def king_box(self):
        a, b = dungeon.king_pixels()
        return a, b, self.kt, self.kt + dungeon.height("king") - 1

    def king_head(self):
        """Where the blade strikes him (0.9.2: his first
        THRONE["head"] lines)."""
        a, b = dungeon.king_pixels()
        return a, b, self.kt, self.kt + dungeon.THRONE["head"] - 1

    def throne(self):
        """The King, or the crown (rules.py, dungeon.THRONE)."""
        th = dungeon.THRONE
        if self.crown:
            if self.crown == 1 and self.blade_on(*dungeon.crown_box()):
                self.crown = 2
                self.won = 1
                self.request = VICTORY
                if self.nstep >= 8:
                    self.song, self.restart = SONG_VICTORY, True
                self.score += rules.CROWN_POINTS + \
                    rules.ENERGY_POINTS * self.energy
            return
        if self.kf:
            self.kf -= 1
        elif self.blade_on(*(self.king_head() if self.nstep >= 9
                             else self.king_box())):
            self.kf = self.t["KHIT_FRAMES"]
            self.request = KING_HIT
            self.score += rules.KING_HIT_POINTS
            self.kh += 1
            if self.kh == rules.KING_HITS:
                self.crown = 1
                self.vd = 0
                self.request = KING_DIES
                self.score += rules.KING_POINTS
                return
        x0, x1, t0, t1 = self.king_box()
        kx0 = self.kx + rules.FIRST_PIXEL
        if not self.hurt and kx0 <= x1 and \
                kx0 + rules.KNIGHT_W - 1 >= x0 and \
                self.ky <= t1 and self.ky + rules.KNIGHT_H - 1 >= t0:
            self.wound(rules.BITE_DAMAGE)
            self.request = BITE
        if self.vd:
            self.va += self.t["VEN_FRAC"]
            step = self.t["VEN_INT"] + self.va // 256
            self.va %= 256
            lo, hi = dungeon.venom_span(self.kt)
            gone = False
            if self.vd == 1:
                if self.vp + step + 7 > hi:
                    gone = True
                else:
                    self.vp += step
            elif self.vp < step or self.vp - step < lo:
                gone = True
            else:
                self.vp -= step
            if not gone:
                line = self.kt + th["mouth"]
                if self.vp <= kx0 + rules.KNIGHT_W - 1 and \
                        self.vp + 7 >= kx0 and \
                        self.ky <= line + 1 and \
                        self.ky + rules.KNIGHT_H - 1 >= line:
                    gone = True
                    faces = self.kdir == (8 if self.vd == 1 else 0)
                    if self.kpose != rules.THRUST_POSE and faces:
                        self.parry = self.t["PARRY_FRAMES"]
                        self.request = PARRY
                    elif not self.hurt:
                        self.wound(rules.VENOM_DAMAGE)
                        self.request = BITE
            if gone:
                self.vd = 0
            return
        t0, t1 = th["top"]
        target = min(t1, max(t0, self.ky + 2))
        self.acc += self.t["KSTEP_FRAC"]
        if self.acc >= 256:
            self.acc -= 256
            if self.kt != target:
                self.kt += 2 if self.kt < target else -2
        if self.ks:
            self.ks -= 1
            return
        if self.kt == target:
            right = self.kx >= dungeon.spit_left()
            self.vd = 1 if right else 2
            self.vp = dungeon.venom_start(right)
            self.va = 0
            self.ks = rules.spit_frames(self.tv)[self.kh]
            self.request = SPIT
            self.known |= {SC_VP}

    def guards(self):
        """The guards of the room (0.6; 0.9.4: two blows, the
        stun, the sprint, the return), serpents all: the King
        has throne (0.7; 0.9.4 took out what was left here of
        his sway, as in the cartridge)."""
        g = self.guards_of(self.room)
        lv = dungeon.ROOMS[self.room]["level"]
        self.acc += rules.crawl(lv, self.tv)
        step = self.acc >= 256
        self.acc %= 256
        sprint = 0
        if self.nstep >= 9:              # the hunt (0.9.4)
            whole, frac = rules.sprint(lv, self.tv)
            self.spr += frac
            sprint = whole + (self.spr >= 256)
            self.spr %= 256
        for k, s in enumerate(g):
            if not self.live >> k & 1:
                if self.gt[k]:
                    self.gt[k] -= 1
                    if not self.gt[k]:
                        self.respawn(k, s)
                continue
            if self.gt[k]:                  # stunned
                self.gt[k] -= 1
                continue
            if self.blade_hits(k):
                if self.nstep >= 9:
                    self.blow(k, s)
                else:                       # one blow kills
                    self.live &= ~(1 << k)
                    self.request = KILL
                    self.score += rules.SERPENT_POINTS
                continue
            if not self.hurt and self.bites(k):
                self.energy = max(0, self.energy - rules.BITE_DAMAGE)
                self.hurt = self.t["BITE_FRAMES"]
                self.request = BITE
            self.crawl(k, s, step, sprint)
        self.place_seam()

    def blow(self, k, s):
        """0.9.4: a blow of the blade on guard k: the first
        wounds, pushes and stuns it, the second kills it."""
        a, b = s["path"]
        if self.live >> (k + 2) & 1:
            self.live &= ~(1 << k | 1 << (k + 2))
            self.gt[k] = self.t["RESPAWN_FRAMES"]
            self.request = KILL
            self.score += rules.SERPENT_POINTS
            return
        self.live |= 1 << (k + 2)
        self.gt[k] = self.t["STUN_FRAMES"]
        self.request = KING_HIT
        if self.kdir == 0:          # he faces right: pushed right
            self.sd[k] = 8
            self.sx[k] = min(b, self.sx[k] + rules.KNOCK_PX)
        else:
            self.sd[k] = 0
            self.sx[k] = max(a, self.sx[k] - rules.KNOCK_PX)

    def respawn(self, k, s):
        """0.9.4: guard k alive again, unwounded, at the end of
        its path farther from him, facing the other end."""
        a, b = s["path"]
        if self.kx <= (a + b) // 2:
            self.sx[k], self.sd[k] = b, 8
        else:
            self.sx[k], self.sd[k] = a, 0
        self.live |= 1 << k

    def crawl(self, k, s, step, sprint):
        """A step of guard k (0.9.2-0.9.4: a serpent on his
        lines, as for the bite, with his column on its path,
        faces him and crawls towards him, sprint pixels in
        this frame (0.9.4), and waits on his column; otherwise
        back and forth when step (the fraction carries),
        turning at the ends, also where a chase left it. 0.9.2
        chased him off its path too, and waited at its end: an
        easy mark)."""
        a, b = s["path"]
        x0, x1, t0, t1 = self.guard_box(k)
        if self.nstep >= 9 and self.ky <= t1 and \
                self.ky + rules.KNIGHT_H - 1 >= t0 and \
                a <= self.kx <= b:
            for _ in range(sprint):
                if self.kx == self.sx[k]:
                    return
                if self.kx > self.sx[k]:
                    self.sd[k] = 0
                    self.sx[k] += 1
                else:
                    self.sd[k] = 8
                    self.sx[k] -= 1
            return
        if not step:
            return
        if self.sd[k] == 0:
            if self.sx[k] >= b:
                self.sd[k] = 8
                return
            self.sx[k] += 1
            if self.sx[k] == b:
                self.sd[k] = 8
        else:
            if self.sx[k] <= a:
                self.sd[k] = 0
                return
            self.sx[k] -= 1
            if self.sx[k] == a:
                self.sd[k] = 0

    def guard_box(self, k):
        """(first pixel, last pixel, first line, last line) of
        guard k."""
        s = self.guards_of(self.room)[k]
        x0 = self.sx[k] + rules.FIRST_PIXEL
        h = dungeon.height(s["kind"])
        return x0, x0 + 7, s["top"], s["top"] + h - 1

    def blade_hits(self, k):
        b = self.blade()
        if not b:
            return False
        x0, x1, t0, t1 = self.guard_box(k)
        b0, w = b
        y0 = self.ky + BLADE_LINE
        return b0 <= x1 and b0 + w - 1 >= x0 and \
            y0 <= t1 and y0 + 1 >= t0

    def bites(self, k):
        x0, x1, t0, t1 = self.guard_box(k)
        kx0 = self.kx + rules.FIRST_PIXEL
        return kx0 <= x1 and kx0 + rules.KNIGHT_W - 1 >= x0 and \
            self.ky <= t1 and self.ky + rules.KNIGHT_H - 1 >= t0

    def picture_state(self):
        """What the picture of this frame shows (the things of
        the overscan come after it)."""
        if not self.screen:
            if self.over or self.won:       # 0.8: an end screen
                return dict(screen=0, mode=self.mode,
                            end="victory" if self.won else
                            "gameover", score=self.score)
            return dict(screen=0, mode=self.mode)
        return dict(screen=self.screen, room=self.room,
                    kx=self.kx, ky=self.ky, kdir=self.kdir,
                    kpose=self.kpose, blade=self.blade(),
                    flash=self.flash(),
                    ox=self.ox, oy=self.oy, odir=self.odir,
                    frames=self.frames, score=self.score,
                    energy=self.energy, key=self.key,
                    opened=self.opened, raised=self.pf_up,
                    over=self.over, won=self.won,
                    venom=(self.vp, self.kt + dungeon.THRONE["mouth"])
                    if self.nstep >= 6 and
                    dungeon.throne(self.room) and self.vd and
                    not self.crown else None,
                    band_a=dict(self.band_a) if self.band_a else None,
                    band_b=dict(self.band_b) if self.band_b else None,
                    seam=dungeon.seam(self.room) if self.nstep >= 5
                    else None)

    def knight(self, swcha):
        if self.parry:                  # 0.7: the shield
            self.parry -= 1
            self.kpose = rules.PARRY_POSE
            return
        if self.thrust:
            self.thrust -= 1
            if self.thrust:
                self.kpose = rules.THRUST_POSE
                return
        if self.pressed & FIRE:
            self.thrust = self.t["THRUST_FRAMES"]
            self.kpose = rules.THRUST_POSE
            self.request = SWORD
            return
        moved = False
        vertical = True
        if swcha & (RIGHT | LEFT) != RIGHT | LEFT:
            self.hacc += self.t["H_FRAC"]
            dx = self.t["H_INT"] + self.hacc // 256
            self.hacc %= 256
            right = not swcha & RIGHT
            self.kdir = 0 if right else 8
            nx = self.kx + dx if right else self.kx - dx
            if (nx > rules.X_MAX or nx < rules.X_MIN) and \
                    self.nstep < 3:
                pass                    # the edge stops him
            elif nx > rules.X_MAX or nx < rules.X_MIN:
                way = "east" if right else "west"
                self.room = dungeon.exits(self.room)[way]
                self.screen = self.room + 1
                self.kx = rules.X_MIN if right else rules.X_MAX
                self.kdist = (self.kdist + dx) % 256
                moved, vertical = True, False
            elif self.free(nx, self.ky):
                self.kx = nx
                self.kdist = (self.kdist + dx) % 256
                moved = True
        if vertical and swcha & (UP | DOWN) != UP | DOWN:
            self.vacc += self.t["V_FRAC"]
            if self.vacc >= 256:
                self.vacc -= 256
                up = not swcha & UP
                ny = self.ky - 2 if up else self.ky + 2
                way = "north" if up else "south"
                nxt = dungeon.exits(self.room)[way]
                if not rules.TOP_MIN <= ny <= rules.TOP_MAX:
                    if nxt is not None and self.nstep >= 3:  # a stair
                        self.room = nxt
                        self.screen = nxt + 1
                        self.ky = rules.TOP_MAX if up \
                            else rules.TOP_MIN
                        self.kdist = (self.kdist + 1) % 256
                        moved = True
                        self.request = STAIR    # 0.9
                elif self.free(self.kx, ny):
                    self.ky = ny
                    self.kdist = (self.kdist + 1) % 256
                    moved = True
        self.kpose = rules.WALK[(self.kdist // rules.STRIDE) % 4] \
            if moved else 0

    # -- what the picture shows ------------------------------
    def blade(self):
        """(first pixel, width) of the blade, or None."""
        if self.screen == 0 or self.kpose != rules.THRUST_POSE:
            return None
        if self.kdir == 0:
            x0 = self.kx + rules.FIRST_PIXEL + rules.KNIGHT_W
            for w in (8, 4, 2, 1):
                if x0 + w <= 160:
                    return (x0, w)
            return None
        end = self.kx + rules.FIRST_PIXEL - 1
        for w in (8, 4, 2, 1):
            if end - w + 1 >= 0:
                return (end - w + 1, w)
        return None

    def state(self):
        """The variables the cartridge keeps, by RAM name
        ("SC+n": the Superchip RAM)."""
        s = dict(frames=self.frames, screen=self.screen,
                 held=self.held, pressed=self.pressed,
                 mode=self.mode, sfxreq=0, zcoarse=self.zcoarse,
                 zref=self.zref, over=self.over, won=self.won,
                 song=self.song)
        if not self.screen and (self.over or self.won):
            # 0.8: the digits of the end screen in the Superchip
            # RAM, columns of 9 bytes, bottom first
            for k, ch in enumerate(f"{self.score:06d}"):
                rows = art.DIGITS[int(ch)]
                s[f"SC+{9 * k}"] = 0
                for j in range(8):
                    s[f"SC+{9 * k + 1 + j}"] = int(
                        (rows[7 - j] + "..").replace("#", "1")
                        .replace(".", "0"), 2)
        if self.screen:
            # (the Superchip RAM is not cleared at the start: its
            # bytes count from the first room set up)
            s[f"SC+{SC_HM}"] = self.hm
            bcd = int(f"{self.score:06d}", 16)
            s.update(room=self.room, kx=self.kx, ky=self.ky,
                     kdir=self.kdir, kpose=self.kpose,
                     kdist=self.kdist, hacc=self.hacc,
                     vacc=self.vacc, thrust=self.thrust,
                     ox=self.ox, oy=self.oy, odir=self.odir,
                     onus=self.onus,
                     plug=2 if dungeon.plug(self.room) else 0,
                     energy=self.energy, key=self.key,
                     opened=self.opened, spk=self.spk,
                     spup=self.spup, hurt=self.hurt,
                     over=self.over, won=self.won,
                     parry=self.parry)
            s["score"] = bcd >> 16
            s["score+1"] = (bcd >> 8) & 0xFF
            s["score+2"] = bcd & 0xFF
            s[f"SC+{SC_LIVE}"] = self.live
            s[f"SC+{SC_ACC}"] = self.acc
            s[f"SC+{SC_SPR}"] = self.spr        # 0.9.4
            for k in (0, 1):
                s[f"SC+{SC_GT + k}"] = self.gt[k]
            for k in (0, 1):
                s[f"SC+{SC_SX + k}"] = self.sx[k]
                s[f"SC+{SC_SD + k}"] = self.sd[k]
            # 0.7: the bytes of the King the cartridge has written
            king = {SC_KT: self.kt, SC_KH: self.kh, SC_KF: self.kf,
                    SC_KS: self.ks, SC_VP: self.vp, SC_VD: self.vd,
                    SC_VA: self.va, SC_CROWN: self.crown}
            for i in sorted(self.known):
                s[f"SC+{i}"] = king[i]
        if self.nstep < 9:               # what the step's RAM has
            for name in list(s):
                base, _, off = name.partition("+")
                if base == "SC":
                    i = int(off)
                    need = SC_STEP.get(i, 6 if i in king_bytes()
                                       else 8)
                elif base == "score":
                    need = 3
                else:
                    need = STATE_STEP.get(base, 1)
                if self.nstep < need:
                    del s[name]
        return s


def king_bytes():
    return (SC_KT, SC_KH, SC_KF, SC_KS, SC_VP, SC_VD, SC_VA, SC_CROWN)
