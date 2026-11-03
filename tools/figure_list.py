"""figure_list.py - the figures of the book taken from the chain
for tools/chain_figures.py.

Each figure is a frame of the route of a step (tests/
verify_chain.py: the route of its tests), found by the words of
a picture of that route (`shot`: the whole label, or a part of it
that only one label has) and `offset` frames after it. The
caption is the book's (English, provisional until the chapters
are written); `facts` are what the caption says, checked on the
RAM of that frame in Stella (both runs), each as

    (variable, value)                  the value in that frame
    (variable, "+n" or "-n", shot)     changed by n since the
                                       frame of that picture

The variables are those of the step's RAM (scalecrown.asm), and
`points` (the score, from its three BCD bytes) and `level` (1-4,
from the room). `chapter` is the chapter of the book that prints it
(tools/chapters.py: plan B, decided on 31 October 2026).
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))), "game", "assets"))
import rules                                        # noqa: E402

E = rules.ENERGY
THRUST, PARRY = rules.THRUST_POSE, rules.PARRY_POSE

FIGURES = [
    # step 1: the first room (chapters 1-4; the NTSC frame in
    # chapter 1, where the reader first builds and plays it: F23)
    dict(id="01", step=1, tv="ntsc", chapter=1,
         shot="the first room: The Broken Gate, Sir Roderick standing",
         caption="Step 01 in Stella, on an NTSC television: The Broken "
         "Gate, the first room of the crypt, and Sir Roderick standing "
         "where he comes in. The top 26 lines are black: there is no "
         "HUD yet.",
         facts=[("room", 1), ("kpose", 0)]),
    dict(id="02", step=1, tv="pal", chapter=3,
         shot="the first room: The Broken Gate, Sir Roderick standing",
         caption="The same frame of step 1 on a PAL television: the "
         "same source, 312 lines, 18 black lines above the HUD and 18 "
         "below the room, the PAL colours.",
         facts=[("room", 1), ("kpose", 0)]),
    # step 2: the knight (chapter 5)
    dict(id="03", step=2, tv="ntsc", chapter=5, shot="walking right",
         caption="Step 2: Sir Roderick walks right; the walk "
         "changes his figure every few pixels.",
         facts=[("room", 1), ("kdir", 0)]),
    dict(id="04", step=2, tv="ntsc", chapter=5, shot="thrust right",
         caption="The thrust: the blade is missile 0, placed next "
         "to his hand.",
         facts=[("kpose", THRUST), ("kdir", 0)]),
    dict(id="05", step=2, tv="ntsc", chapter=5, shot="thrust left",
         caption="A thrust to the left: player 0 reflected, the "
         "blade on the other side.",
         facts=[("kpose", THRUST), ("kdir", 8)]),
    dict(id="06", step=2, tv="ntsc", chapter=5,
         shot="up against a pillar",
         caption="The collision map of the room stops him under a "
         "pillar.",
         facts=[("room", 1)]),
    dict(id="07", step=2, tv="ntsc", chapter=5,
         shot="step 2: the east edge stops him",
         caption="In step 2 the edge of the screen stops him: the "
         "openings of the room lead nowhere yet.",
         facts=[("room", 1)]),
    # step 3: the dungeon and the HUD (chapter 6)
    dict(id="08", step=3, tv="ntsc", chapter=6,
         shot="room 0 RUBBLE HALL, from the west",
         caption="Step 3: the HUD (the score, the energy, LEVEL 1) "
         "above room 0, Rubble Hall.",
         facts=[("room", 0), ("level", 1), ("energy", E)]),
    dict(id="09", step=3, tv="ntsc", chapter=6,
         shot="room 3 THE IRON STAIR, from the east",
         caption="Room 3, The Iron Stair: the stair down to level 2.",
         facts=[("room", 3), ("level", 1)]),
    dict(id="10", step=3, tv="ntsc", chapter=6,
         shot="room 5 THE NARROW STEPS, from the west",
         caption="Level 2: other colours, and the torches.",
         facts=[("room", 5), ("level", 2)]),
    dict(id="11", step=3, tv="ntsc", chapter=6,
         shot="room 10 REED GALLERY, from the east",
         caption="Level 3: the water and the reeds of the Reed "
         "Gallery.",
         facts=[("room", 10), ("level", 3)]),
    dict(id="12", step=3, tv="ntsc", chapter=6,
         shot="room 13 HALL OF COILS, from the east",
         caption="Level 4: the Hall of Coils.",
         facts=[("room", 13), ("level", 4)]),
    dict(id="13", step=3, tv="ntsc", chapter=6,
         shot="room 15, the east plug stops him",
         caption="The throne room: the plug (the ball) closes the "
         "east side, and stops him.",
         facts=[("room", 15), ("level", 4)]),
    # step 4: keys, doors and treasure (chapter 7)
    dict(id="14", step=4, tv="ntsc", chapter=7,
         shot="room 0 RUBBLE HALL, the chest",
         caption="Step 4: player 1 in the kernel draws the chest of "
         "level 1 in Rubble Hall.",
         facts=[("room", 0), ("points", 0), ("key", 0)]),
    dict(id="15", step=4, tv="ntsc", chapter=7,
         shot="room 0: the chest open, the key, 500 points",
         caption="The chest opened: 500 points, and the key, shown "
         "in the HUD.",
         facts=[("room", 0), ("points", rules.CHEST_POINTS),
                ("key", 1)]),
    dict(id="16", step=4, tv="ntsc", chapter=7,
         shot="room 3: the grate opens, 1000 points, the key used",
         caption="The key opens the grate of the stair: 1000 points "
         "more, and the key is gone.",
         facts=[("room", 3), ("points", "+1000",
                              "room 0: the chest open, the key, 500 "
                              "points"), ("key", 0)]),
    dict(id="17", step=4, tv="ntsc", chapter=7,
         shot="room 14 THE GILDED GATE, the golden gate",
         caption="The golden gate before the throne room.",
         facts=[("room", 14), ("level", 4)]),
    dict(id="18", step=4, tv="ntsc", chapter=7,
         shot="room 14: the spikes up",
         caption="The plates of the spikes go up and down; in step 4 "
         "they do not hurt yet.",
         facts=[("room", 14), ("spup", 1)]),
    # step 5: the serpents (chapter 8), the sword and the damage (9)
    dict(id="19", step=5, tv="ntsc", chapter=8,
         shot="room 2 PILLAR WALK, a serpent",
         caption="Step 5: two serpents in Pillar Walk, one along the "
         "top wall and one in the corridor: player 1 draws both, "
         "the seam between them.",
         facts=[("room", 2), ("energy", E)]),
    dict(id="20", step=5, tv="ntsc", chapter=8,
         shot="room 6 SHED SKINS, level 2",
         caption="Two serpents in one room: the seam of the kernel "
         "moves player 1 from the serpent above to the one below.",
         facts=[("room", 6), ("level", 2)]),
    dict(id="21", step=5, tv="ntsc", chapter=8,
         shot="room 4 BONE NICHE, the chest",
         caption="The chest and its guard share the lines of the "
         "room: in this frame player 1 draws one of them...",
         facts=[("room", 4)]),
    dict(id="22", step=5, tv="ntsc", chapter=8,
         shot="room 4 BONE NICHE, the chest", offset=1,
         caption="...and in the next frame the other: they take "
         "turns, and both flicker.",
         facts=[("room", 4)]),
    dict(id="23", step=5, tv="ntsc", chapter=9,
         shot="room 2: bitten, he flashes",
         caption="A bite: three units of energy, and Sir Roderick "
         "flashes.",
         facts=[("room", 2), ("energy", E - rules.BITE_DAMAGE)]),
    dict(id="24", step=5, tv="ntsc", chapter=9,
         shot="room 2: the serpent killed, 100 points",
         caption="In step 5 one blow of the blade kills a serpent: "
         "100 points.",
         facts=[("room", 2), ("points", rules.SERPENT_POINTS)]),
    dict(id="25", step=5, tv="ntsc", chapter=9,
         shot="room 2: on the plate, hurt, he flashes",
         caption="On a plate when it goes up: the spikes take a unit "
         "of energy.",
         facts=[("room", 2), ("energy", "-1",
                              "room 2: the serpent killed, 100 "
                              "points")]),
    dict(id="26", step=5, tv="ntsc", chapter=9,
         shot="GAME OVER: everything stops",
         caption="No energy left: GAME OVER. In step 5 the game just "
         "stops.",
         facts=[("energy", 0)]),
    # step 6: the Serpent King (chapter 10)
    dict(id="27", step=6, tv="ntsc", chapter=10,
         shot="room 15: the King spits",
         caption="Step 6: the throne room has its own kernel. The "
         "Serpent King is player 1 twice as wide; the venom is "
         "missile 1.",
         facts=[("room", 15)]),
    dict(id="28", step=6, tv="ntsc", chapter=11,
         shot="room 15: the venom from behind, 3 units",
         caption="The venom hits him from behind: three units.",
         facts=[("room", 15), ("energy", "-3",
                               "room 15: the King spits")]),
    dict(id="29", step=6, tv="ntsc", chapter=11,
         shot="room 15: the shield, the venom parried",
         caption="Facing the venom, standing still, he raises the "
         "shield: the venom is parried.",
         facts=[("room", 15), ("kpose", PARRY)]),
    dict(id="30", step=6, tv="ntsc", chapter=11,
         shot="room 15: the King's bite",
         caption="Too close: the King bites.",
         facts=[("room", 15)]),
    dict(id="31", step=6, tv="ntsc", chapter=11,
         shot="room 15: the King beaten, the crown on the throne",
         caption="The King beaten: the crown waits on the throne.",
         facts=[("room", 15)]),
    dict(id="32", step=6, tv="ntsc", chapter=11,
         shot="VICTORY: the crown broken",
         caption="A blow breaks the crown: VICTORY. 10000 points, "
         "and 200 for each unit of energy left (here six: 1200). In "
         "step 6 the game stops here.",
         facts=[("room", 15), ("energy", 6),
                ("points", f"+{rules.CROWN_POINTS + 6 * rules.ENERGY_POINTS}",
                 "room 15: the King beaten, the crown on the throne")]),
    # step 7: the sound (chapters 11-12)
    dict(id="33", step=7, tv="ntsc", chapter=13,
         shot="SELECT in the game: the music again",
         caption="Step 7, a new game after VICTORY: SELECT, during "
         "the game in this step, has just chosen MUSIC again. The "
         "screen does not change; the sound does.",
         facts=[("mode", 0)]),
    # step 8: states, title and end screens (chapter 13)
    dict(id="34", step=8, tv="ntsc", chapter=14, shot="title",
         caption="Step 8: the title, drawn by the kernel of bank 1.",
         facts=[("screen", 0), ("mode", 0)]),
    dict(id="35", step=8, tv="ntsc", chapter=14,
         shot="title, SILENT",
         caption="SELECT on the title: the third mode, SILENT.",
         facts=[("screen", 0), ("mode", 2)]),
    dict(id="36", step=8, tv="ntsc", chapter=14,
         shot="the VICTORY screen",
         caption="The VICTORY screen (bank 6): the crown, Sir "
         "Roderick and the score.",
         facts=[("screen", 0)]),
    dict(id="37", step=8, tv="ntsc", chapter=14,
         shot="the GAME OVER screen",
         caption="The GAME OVER screen (bank 6): the crown above, the "
         "Serpent King below; the lament plays once.",
         facts=[("screen", 0), ("won", 0)]),
    dict(id="38", step=8, tv="pal", chapter=14, shot="title",
         caption="The title on a PAL television.",
         facts=[("screen", 0), ("mode", 0)]),
    # step 9: the hunt (chapter 14)
    dict(id="39", step=9, tv="ntsc", chapter=15,
         shot="room 0: the first blow: the serpent above pushed to "
         "the west end of its path, stunned, blinking", offset=2,
         caption="Step 9, the hunt: the first blow wounds a serpent, "
         "pushes it towards the end of its path and stuns it; it "
         "blinks, and here takes turns with the open chest. The "
         "second blow kills it.",
         facts=[("room", 0)]),
    dict(id="40", step=9, tv="ntsc", chapter=15,
         shot="room 2: the serpent back, at the end of its path "
         "farther from him",
         caption="A serpent killed comes back after a while, at the "
         "end of its path farther from him.",
         facts=[("room", 2)]),
    dict(id="41", step=9, tv="ntsc", chapter=15,
         shot="room 15: the blade on the coils, low: no blow",
         caption="The King can be struck only on the head: the blade "
         "on the coils does nothing.",
         facts=[("room", 15), ("kpose", THRUST)]),
    dict(id="42", step=9, tv="pal", chapter=15,
         shot="the VICTORY screen: the crown broken",
         caption="The complete game, the 1.0, on a PAL television: "
         "the VICTORY screen.",
         facts=[("screen", 0)]),
    # the finished game, the 1.0 (step 9), for chapter 1: four
    # frames in one figure, the game the book builds (F23: the
    # preview of the book should meet pictures at once)
    dict(id="43", step=9, tv="ntsc", chapter=1,
         shot="title, SOUND FX",
         caption="the title, with SELECT on SOUND FX",
         facts=[("screen", 0), ("mode", 1)]),
    dict(id="44", step=9, tv="ntsc", chapter=1,
         shot="room 6 SHED SKINS, level 2: two serpents, a seam",
         caption="level 2, Shed Skins, and its two serpents",
         facts=[("room", 6), ("level", 2)]),
    dict(id="45", step=9, tv="ntsc", chapter=1,
         shot="room 10 REED GALLERY, the reeds: a seam low in the room",
         caption="level 3, the water of the Reed Gallery",
         facts=[("room", 10), ("level", 3)]),
    dict(id="46", step=9, tv="ntsc", chapter=1,
         shot="room 15: the venom flies west",
         caption="the throne room: the Serpent King spits its venom",
         facts=[("room", 15)]),
]
