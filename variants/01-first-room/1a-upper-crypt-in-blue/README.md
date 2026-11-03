# Experiment 1a: The Upper Crypt in blue

Chapter 4, "The playfield and the first room", prints this experiment and explains it: a guided variant ("Make it yours"). This folder is step 01 (`chain/01-first-room`) with the change below, built: `game/build` holds its two cartridges, made by its own `tools/build.py` with dasm 2.20.14.1.

## The change

In `game/assets/rooms.py`, the line

```text
            floor=0xC0, floor_lum=(0, 6), light=80, shimmer=False,
```

becomes

```text
            floor=0x80, floor_lum=(0, 6), light=80, shimmer=False,
```

## What its test saw

`tools/make_variants.py` built it and played it beside step 01, with the same inputs (the head of the step's route, 48 frames on NTSC from bank 0), in the simulator, and in Stella 7.0 for the pictures: 262 lines; the RAM the same; 2 of 2 pictures. It passed, as a guided variant: it keeps the time of every frame and changes what it says it changes. Chapter 16 has it in Table 16.9.

The report of the test is `evidence/1a.json`. `evidence/1a_step.png` and `evidence/1a_change.png` are a picture of the step and the same picture of the experiment, as Stella 7.0 drew them.

## The cartridges

| Cartridge | SHA-256 |
|---|---|
| `game/build/scalecrown_ntsc.bin` | `f391e8831235701d454d162609cc6bd345a416f7363d609beb24a66e100545e2` |
| `game/build/scalecrown_pal.bin` | `3508c6d864570ffbc8058845bb73d1c77dc5a9d3cb906645420574399a84fb34` |

## Back to the step

To undo the change in your own copy, copy the file back from `chain/01-first-room`. Leave this folder as it is: `verify.py` checks that it is the step with this change and nothing else.
