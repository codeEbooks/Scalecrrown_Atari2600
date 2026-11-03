# Scalecrown: the chain of the book

Nine steps, each one a complete program that builds and runs on
its own, NTSC and PAL, from the first room to the finished game.
Every step is made from the same source, the finished game (the
master source in `game/`: `game/src` and `game/assets`, built by
`tools/build.py`), by `tools/make_chain.py`; the last step is
Scalecrown 1.0, byte for byte.

| Step | Folder | What it adds |
|---|---|---|
| 1 | `01-first-room` | the start, the eight banks and their tails, the frame, the Superchip, the room kernel: The Broken Gate, Sir Roderick standing |
| 2 | `02-knight` | the joystick, the walk, the walls, the sword (missile 0), RESET |
| 3 | `03-dungeon` | the sixteen rooms, the openings, the stairs, the plugs (the ball), the colours of the levels, the torches, the water, the HUD |
| 4 | `04-keys-doors` | player 1: chests, keys, grates, the golden gate; the spikes go up and down; the points |
| 5 | `05-serpents` | the serpents, the seam, the flicker, the sword kills, the bite, the hurt, GAME OVER |
| 6 | `06-serpent-king` | the throne room (bank 2): the King, the venom (missile 1), the shield, the crown, VICTORY |
| 7 | `07-sound` | the sound player (bank 5): the theme, the effects |
| 8 | `08-title-and-ends` | the title (bank 1), SELECT, the end screens (bank 6), the lament and the fanfare |
| 9 | `09-the-hunt` | the hunt: chase, sprint, two blows, the return; the King struck on his head: the 1.0 |

Each folder has its `README.md`. To make the chain again from the
source and build every step:

    python3 tools/make_chain.py --assemble

(it writes `chain/chain.json`: for each step its files, its lines,
the bytes free in each bank and the SHA-256 of its two
cartridges, and checks that the last step is the 1.0).

## The tests of the chain

From the folder that holds `game/`, `chain/` and `tests/` (Python
3.10 or later, py65 1.2.0 and Pillow; dasm 2.20.14.1 on the PATH
and Stella 7.0):

- `python3 tests/verify_chain.py --stella PATH --mutations`: each
  step plays a route of its own (what the step can do) against
  the model of the step (`tests/model.py`, the game without what
  the step does not have yet), in the simulator from banks 0 and
  7 and in Stella from bank 0: the RAM of every frame, the lines,
  VSYNC, the writes to the TIA in their windows, the pictures
  pixel by pixel; NTSC and PAL. Three one-line mutations of each
  step must be caught.
- `python3 tools/make_variants.py --stella PATH`: the two variants
  and the break of each step (`tools/variants.py`), each one made
  from the step's folder, built, played on the head of the step's
  route next to the step, and checked against what it claims (the
  timing, the first variable of the RAM that changes, the
  pictures, the sound).
- `python3 tools/chain_figures.py --stella PATH`: the figures of
  the book (`tools/figure_list.py`), each one a frame of a step's
  route captured twice in Stella (the two files must be the same),
  with the facts of its caption checked on the RAM of that frame.
- `python3 tools/chain_register.py`: every instruction of the
  finished game with the step that brings it, its chapter, and
  whether it ran in the tests (the simulator and Stella's
  counters); the seams of the earlier steps.
