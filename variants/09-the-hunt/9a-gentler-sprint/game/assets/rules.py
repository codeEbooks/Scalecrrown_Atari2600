"""rules.py - how the game moves, in seconds and pixels.

The rules of the whole game, written once: Sir Roderick, the
spikes, the damage, the points, the serpents, the bite, GAME
OVER, the Serpent King, the venom, the shield, the crown,
VICTORY. How hard the game is was found by playing it, in
three rounds: the King and the serpents a little faster and
stronger; then less energy, more serpents (dungeon.py),
serpents that chase him and the King struck only on his head;
then the way to the throne a little harder: the serpents
sprint when they chase him, take two blows, and come back a
while after they die. Where a value was made harder after
the game was first played, the easier one stands in its
comment ("easier"). The generator turns
them into the tables of each television (build_assets.py);
the test bench of the book plays them frame by frame in
Python to know where Sir Roderick must be.

Time: the same seconds on NTSC (60
frames a second) and PAL (50). A speed is kept as a whole
part and a fraction of 1/256 per frame; the fraction is added
to an accumulator and its carry is one unit more.

Space: the room is 160 pixels x 160 lines, 20 x 10 blocks of
8 pixels x 16 lines (rooms.py). Sir Roderick is 8 x 24; his
column is the one given to the positioning routine, his first
pixel is column + 3; his top line is odd (a figure starts on
a line B of the kernel) and he moves up and down by steps of
2 lines.
"""

FPS = {"ntsc": 60, "pal": 50}

WALK_PX_S = 60          # pixels a second, left and right
CLIMB_STEPS_S = 48      # steps of 2 lines a second, up and down
THRUST_S = 0.2          # the thrust of the sword, seconds

KNIGHT_W = 8
KNIGHT_H = 24
FIRST_PIXEL = 3         # pixel of column 0 of the figure
X_MIN, X_MAX = 0, 149   # columns of Sir Roderick
TOP_MIN, TOP_MAX = 1, 135

# poses: 0 stand, 1 and 2 the two steps, 3 the thrust; the
# walk shows 1, 0, 2, 0, a pose every STRIDE units walked
# (a pixel left or right, or a step up or down)
WALK = (1, 0, 2, 0)
STRIDE = 8
THRUST_POSE = 3

# the blade: up to 8 pixels beside the hand, shortened to
# 4, 2 or 1 near the edge of the screen
BLADE_W = 8

# the rooms, the ways between them and the start: dungeon.py
# the energy: units (easier: 16)
ENERGY = 12

# --- the spikes, the keys, the doors, the points -----------
# the spikes: the plates stay down, then up, and again; down
# for less time in the lower levels (seconds, by level)
SPIKES_DOWN_S = {1: 2.0, 2: 1.8, 3: 1.6, 4: 1.4}
SPIKES_UP_S = 1.0
# a raised plate under his feet takes SPIKE_DAMAGE units of
# energy, and again every HURT_S seconds while he stays on it
SPIKE_DAMAGE = 1
HURT_S = 0.5
# points: multiples of 100 below 10 000, so that
# they are added to the middle byte of the score (BCD)
CHEST_POINTS = 500
DOOR_POINTS = 1000

# --- the serpents, the bite, the sword, GAME OVER ----------
# the serpents crawl faster in the lower levels (pixels a
# second, by level; easier: 30, 36, 42, 48); the Serpent
# King sways in front of his throne. A serpent moves a pixel
# a frame at most (crawl), below 50 on PAL
SERPENT_PX_S = {1: 38, 2: 42, 3: 46, 4: 49}
KING_PX_S = 30
# a bite takes BITE_DAMAGE units; after any wound (a bite, the
# spikes) he flashes and nothing hurts him for a while: BITE_S
# after a bite, HURT_S after the spikes (so the spikes hurt
# every HURT_S)
BITE_DAMAGE = 3          # easier: 2
BITE_S = 1.0
SERPENT_POINTS = 100
# the hunt (the way to the throne made harder: serpents that
# sprint, that take two blows, that come back):
# - the sprint: a serpent chasing him (dungeon.py, model.crawl)
#   crawls SPRINT_PX_S, by level, slower than his walk (he can
#   still get away) but faster than its round; on PAL above
#   50 a second: a whole pixel a frame and a fraction
SPRINT_PX_S = {1: 40, 2: 44, 3: 48, 4: 50}
# - two blows: the first wounds it (no points): it is pushed
#   KNOCK_PX away along its path (the side the blade came
#   from), faces him and for STUN_S does not crawl, bite or take
#   a blow, and blinks (hidden every other FLASH_FRAMES
#   frames); the second kills it (SERPENT_POINTS)
SERPENT_BLOWS = 2
KNOCK_PX = 12
STUN_S = 0.5
# - the return: RESPAWN_S after it dies it comes back, alive
#   and unwounded, at the end of its path farther from him,
#   facing the other end (when he comes into the room again,
#   all of them, as before)
RESPAWN_S = 4.0
# energy 0: GAME OVER; everything stops, and after GAME_OVER_S
# the button goes back to the title (RESET starts a new game)
GAME_OVER_S = 1.0
# the flash of a wound: the colours of the flash every other
# FLASH_FRAMES frames
FLASH_FRAMES = 4
FLASH_COLOUR = 0x0E


# --- the Serpent King, the venom, the shield, the crown,
# VICTORY ------------------------------------------------
# the King stays in the middle of the throne room, in front of
# the throne, and goes up and down (steps of 2 lines) towards
# the line where his mouth meets Sir Roderick's middle; there
# he spits the venom (missile 1) towards him and stays still
# while it flies (the venom is drawn on the lines of his
# mouth: the colour of that pair switches it, like the blade)
KING_STEPS_S = 19        # easier: 15
KING_HITS = 10          # blows of the sword to beat him
#                         (easier: 8)
KING_HIT_S = 0.5        # after a blow he flashes, no blow counts
# seconds between two spits, by the blows he has had: the more
# blows, the more often he spits (easier: 2.0, 1.8, 1.6,
# 1.4, 1.2, 1.0, 0.9, 0.8)
SPIT_S = (1.6, 1.5, 1.4, 1.3, 1.2, 1.1, 1.0, 0.9, 0.8, 0.7)
VENOM_PX_S = 112         # easier: 90
VENOM_DAMAGE = 3
# the shield: venom reaching him from the side he faces is
# parried (not in the thrust); he shows the parry for PARRY_S
# and stands still
PARRY_S = 0.25
PARRY_POSE = 4
KING_HIT_POINTS = 500
KING_POINTS = 5000
CROWN_POINTS = 10000    # the first byte of the score
ENERGY_POINTS = 200     # for each unit left at the end
VICTORY_S = 2.0         # then the end screen
# the end screens: after GAME_OVER_S or VICTORY_S the
# room gives way to its end screen; END_S later the button goes
# back to the title (RESET starts a game at once)
END_S = 1.0


def frames_of(seconds, tv):
    return int(round(seconds * FPS[tv]))


def spike_frames(tv):
    """(frames down by level 1-4, frames up, frames of the
    hurt) on one television."""
    return ([frames_of(SPIKES_DOWN_S[lv], tv) for lv in (1, 2, 3, 4)],
            frames_of(SPIKES_UP_S, tv), frames_of(HURT_S, tv))


def bcd_hundreds(points):
    """The byte added to the middle byte of the score."""
    h = points // 100
    return (h // 10) << 4 | h % 10


def per_frame(rate, tv):
    """(whole, fraction/256) of a rate per second."""
    v = rate / FPS[tv]
    whole = int(v)
    frac = int(round((v - whole) * 256))
    if frac == 256:
        whole, frac = whole + 1, 0
    return whole, frac


def thrust_frames(tv):
    return int(round(THRUST_S * FPS[tv]))


def crawl(level, tv):
    """The fraction (1/256 a frame) of the serpents of a level
    (None: the Serpent King)."""
    whole, frac = per_frame(KING_PX_S if level is None
                            else SERPENT_PX_S[level], tv)
    if whole:
        raise SystemExit("a serpent faster than a pixel a frame")
    return frac


def table(tv):
    """The numbers the cartridge of one television needs."""
    hi, hf = per_frame(WALK_PX_S, tv)
    vi, vf = per_frame(CLIMB_STEPS_S, tv)
    ki, kf = per_frame(KING_STEPS_S, tv)
    vi2, vf2 = per_frame(VENOM_PX_S, tv)
    return dict(H_INT=hi, H_FRAC=hf, V_INT=vi, V_FRAC=vf,
                THRUST_FRAMES=thrust_frames(tv),
                BITE_FRAMES=frames_of(BITE_S, tv),
                GO_FRAMES=frames_of(GAME_OVER_S, tv),
                KSTEP_FRAC=kf, VEN_INT=vi2, VEN_FRAC=vf2,
                KHIT_FRAMES=frames_of(KING_HIT_S, tv),
                PARRY_FRAMES=frames_of(PARRY_S, tv),
                STUN_FRAMES=frames_of(STUN_S, tv),
                RESPAWN_FRAMES=frames_of(RESPAWN_S, tv),
                VIC_FRAMES=frames_of(VICTORY_S, tv),
                SPIT_FIRST=frames_of(SPIT_S[0], tv),
                END_FRAMES=frames_of(END_S, tv))


def sprint(level, tv):
    """(whole, fraction/256) a frame of a chasing serpent:
    the whole part 0 or 1."""
    return per_frame(SPRINT_PX_S[level], tv)


def spit_frames(tv):
    """Frames between two spits, by the blows the King has had
    (0 to KING_HITS - 1)."""
    return [frames_of(s, tv) for s in SPIT_S]


def check():
    bad = []
    for tv in FPS:
        t = table(tv)
        if t["H_INT"] > 2 or t["V_INT"] != 0:
            bad.append(f"{tv}: steps too long")
        speed = (t["H_INT"] + t["H_FRAC"] / 256) * FPS[tv]
        if abs(speed - WALK_PX_S) > 0.5:
            bad.append(f"{tv}: walk {speed:.2f} px/s")
        climb = (t["V_FRAC"] / 256) * FPS[tv]
        if abs(climb - CLIMB_STEPS_S) > 0.5:
            bad.append(f"{tv}: climb {climb:.2f} steps/s")
    if TOP_MIN % 2 == 0 or TOP_MAX % 2 == 0:
        bad.append("top lines must be odd")
    if TOP_MAX + KNIGHT_H > 160:
        bad.append("Sir Roderick below the room")
    if X_MAX + FIRST_PIXEL + KNIGHT_W > 160:
        bad.append("Sir Roderick past the right edge")
    for tv in FPS:
        down, up, hurt = spike_frames(tv)
        if not all(0 < n < 256 for n in down + [up, hurt]):
            bad.append(f"{tv}: spike times in one byte")
    for tv in FPS:
        for lv in (1, 2, 3, 4, None):
            try:
                crawl(lv, tv)
            except SystemExit as e:
                bad.append(f"{tv}: {e}")
        t = table(tv)
        if not 0 < t["BITE_FRAMES"] < 256 or \
                not 0 < t["GO_FRAMES"] < 255:
            bad.append(f"{tv}: times of the bite, GAME OVER")
    for tv in FPS:
        t = table(tv)
        if per_frame(KING_STEPS_S, tv)[0] or not t["KSTEP_FRAC"]:
            bad.append(f"{tv}: the King a step a frame at most")
        if not 1 <= t["VEN_INT"] <= 2:
            bad.append(f"{tv}: the venom 1-2 pixels a frame")
        if not all(0 < n < 256 for n in spit_frames(tv) + [
                t["KHIT_FRAMES"], t["PARRY_FRAMES"],
                t["VIC_FRAMES"]]):
            bad.append(f"{tv}: times of the King in one byte")
        if t["VIC_FRAMES"] >= 255:
            bad.append(f"{tv}: VICTORY counts below 255")
        # on the end screen over and won go on counting
        if not 0 < t["END_FRAMES"] or max(
                t["GO_FRAMES"], t["VIC_FRAMES"]) + \
                t["END_FRAMES"] >= 255:
            bad.append(f"{tv}: the end screens count below 255")
    if len(SPIT_S) != KING_HITS or list(SPIT_S) != sorted(
            SPIT_S, reverse=True):
        bad.append("a spit time for each blow, shorter and shorter")
    for p in (KING_HIT_POINTS, KING_POINTS, ENERGY_POINTS):
        if p % 100 or not 0 < p < 10000:
            bad.append(f"points {p}: hundreds below 10 000")
    if CROWN_POINTS != 10000:
        bad.append("the crown: 10 000 (one in the first byte)")
    if ENERGY * ENERGY_POINTS // 100 > 99:
        bad.append("the energy left in one BCD byte")
    if any(SERPENT_PX_S[a] >= SERPENT_PX_S[b]
           for a, b in ((1, 2), (2, 3), (3, 4))):
        bad.append("the serpents faster in the lower levels")
    if FLASH_COLOUR & 0x01 or FLASH_FRAMES & (FLASH_FRAMES - 1):
        bad.append("the flash")
    for p in (CHEST_POINTS, DOOR_POINTS, SERPENT_POINTS):
        if p % 100 or not 0 < p < 10000:
            bad.append(f"points {p}: hundreds below 10 000")
    if ENERGY > 16:
        bad.append("the energy bar has 16 units")
    # the sprint faster than the round, slower than him,
    # at most a pixel and a fraction a frame; two blows; the
    # times in one byte
    for lv in (1, 2, 3, 4):
        if not SERPENT_PX_S[lv] < SPRINT_PX_S[lv] < WALK_PX_S:
            bad.append(f"the sprint of level {lv}")
        for tv in FPS:
            if sprint(lv, tv)[0] > 1:
                bad.append(f"{tv}: a sprint of 2 pixels a frame")
    if SERPENT_BLOWS != 2:
        bad.append("the serpents take two blows (the code)")
    for tv in FPS:
        t = table(tv)
        if not 0 < t["STUN_FRAMES"] < t["RESPAWN_FRAMES"] < 256:
            bad.append(f"{tv}: the stun and the return in a byte")
        if t["STUN_FRAMES"] <= thrust_frames(tv):
            bad.append(f"{tv}: one thrust would wound and kill")
    if not 0 < KNOCK_PX < 16:
        bad.append("the push of a blow")
    return bad


if __name__ == "__main__":
    print(check() or "rules OK")
    for tv in FPS:
        print(tv, table(tv))
