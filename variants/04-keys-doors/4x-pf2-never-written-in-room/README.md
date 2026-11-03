# Experiment 4x: PF2 never written in the room

Chapter 7, "Keys, doors and treasure", prints this experiment and explains it: a "Where it breaks" version. This folder is step 04 (`chain/04-keys-doors`) with the change below, built: `game/build` holds its two cartridges, made by its own `tools/build.py` with dasm 2.20.14.1.

## The change

In `game/src/room_kernel.asm`, the line

```text
        sty     PF2             ; 61+ after the right half
```

is taken out.

## What its test saw

`tools/make_variants.py` built it and played it beside step 04, with the same inputs (the head of the step's route, 983 frames on NTSC from bank 0), in the simulator, and in Stella 7.0 for the pictures: 262 lines; the RAM the same; 5 of 5 pictures. It passed, as a "Where it breaks" version: it breaks what the chapter says it breaks. Chapter 16 has it in Table 16.9.

The report of the test is `evidence/4x.json`. `evidence/4x_step.png` and `evidence/4x_change.png` are a picture of the step and the same picture of the experiment, as Stella 7.0 drew them.

## The cartridges

| Cartridge | SHA-256 |
|---|---|
| `game/build/scalecrown_ntsc.bin` | `4ebafac6fe07e89034b9bafcd2a34d73708540c8b4762c0382a942fabafd7e49` |
| `game/build/scalecrown_pal.bin` | `2919d2a6acbeaa2a1adabb1e34c30d3335fe7cf7fc91ce0c6116c45f78846afa` |

## Back to the step

To undo the change in your own copy, copy the file back from `chain/04-keys-doors`. Leave this folder as it is: `verify.py` checks that it is the step with this change and nothing else.
