# Experiment 1b: Sir Roderick comes in further west

Chapter 2, "The 6507, the memory and the cartridge", prints this experiment and explains it: a guided variant ("Make it yours"). This folder is step 01 (`chain/01-first-room`) with the change below, built: `game/build` holds its two cartridges, made by its own `tools/build.py` with dasm 2.20.14.1.

## The change

In `game/assets/dungeon.py`, the line

```text
START = dict(room=1, x=73, top=17, facing="right")
```

becomes

```text
START = dict(room=1, x=41, top=17, facing="right")
```

## What its test saw

`tools/make_variants.py` built it and played it beside step 01, with the same inputs (the head of the step's route, 48 frames on NTSC from bank 0), in the simulator, and in Stella 7.0 for the pictures: 262 lines; kx from frame 1; 2 of 2 pictures. It passed, as a guided variant: it keeps the time of every frame and changes what it says it changes. Chapter 16 has it in Table 16.9.

The report of the test is `evidence/1b.json`. `evidence/1b_step.png` and `evidence/1b_change.png` are a picture of the step and the same picture of the experiment, as Stella 7.0 drew them.

## The cartridges

| Cartridge | SHA-256 |
|---|---|
| `game/build/scalecrown_ntsc.bin` | `75c50e9d636184b86de2c7722ef00ec1fddcc485aeb9fa3e73458b1359db9089` |
| `game/build/scalecrown_pal.bin` | `ec2476d78ff67ca5bbf9573ae66a147c2729fbfd3e3bccb71dc0f2472bdae1c1` |

## Back to the step

To undo the change in your own copy, copy the file back from `chain/01-first-room`. Leave this folder as it is: `verify.py` checks that it is the step with this change and nothing else.
