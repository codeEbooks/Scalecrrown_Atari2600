# Experiment 1x: A WSYNC forgotten

Chapter 3, "Racing the beam: the frame", prints this experiment and explains it: a "Where it breaks" version. This folder is step 01 (`chain/01-first-room`) with the change below, built: `game/build` holds its two cartridges, made by its own `tools/build.py` with dasm 2.20.14.1.

## The change

In `game/src/room_kernel.asm`, the line

```text
k_top:  sta     WSYNC
```

becomes

```text
k_top:
```

## What its test saw

`tools/make_variants.py` built it and played it beside step 01, with the same inputs (the head of the step's route, 48 frames on NTSC from bank 0), in the simulator, and in Stella 7.0 for the pictures: 261 lines; 2 of 2 pictures. It passed, as a "Where it breaks" version: it breaks what the chapter says it breaks. Chapter 16 has it in Table 16.9.

The report of the test is `evidence/1x.json`. `evidence/1x_step.png` and `evidence/1x_change.png` are a picture of the step and the same picture of the experiment, as Stella 7.0 drew them.

## The cartridges

| Cartridge | SHA-256 |
|---|---|
| `game/build/scalecrown_ntsc.bin` | `21bacd886bdb419e77c0f204d794b584299106d99fc2d89301c8ed46e860eca5` |
| `game/build/scalecrown_pal.bin` | `7f7c7742746407d7272bb0752359e4768824705d07d112ae602b270cd6bb9100` |

## Back to the step

To undo the change in your own copy, copy the file back from `chain/01-first-room`. Leave this folder as it is: `verify.py` checks that it is the step with this change and nothing else.
