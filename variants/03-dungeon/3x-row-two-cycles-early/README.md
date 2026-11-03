# Experiment 3x: The row two cycles early

Chapter 6, "The dungeon and the HUD", prints this experiment and explains it: a "Where it breaks" version. This folder is step 03 (`chain/03-dungeon`) with the change below, built: `game/build` holds its two cartridges, made by its own `tools/build.py` with dasm 2.20.14.1.

## The change

In `game/src/hud.asm`, the line

```text
        nop
```

is taken out.

## What its test saw

`tools/make_variants.py` built it and played it beside step 03, with the same inputs (the head of the step's route, 813 frames on NTSC from bank 0), in the simulator, and in Stella 7.0 for the pictures: 262 lines; the RAM the same; 12 of 12 pictures. It passed, as a "Where it breaks" version: it breaks what the chapter says it breaks. Chapter 16 has it in Table 16.9.

The report of the test is `evidence/3x.json`. `evidence/3x_step.png` and `evidence/3x_change.png` are a picture of the step and the same picture of the experiment, as Stella 7.0 drew them.

## The cartridges

| Cartridge | SHA-256 |
|---|---|
| `game/build/scalecrown_ntsc.bin` | `27555ec1159a063cb7ad847b4398ace1651022e15d64befffa1af2645e297d08` |
| `game/build/scalecrown_pal.bin` | `eaf82552ebd4e799561cb87ee3cf9547835e7c95b4324faf74855f3de2fca107` |

## Back to the step

To undo the change in your own copy, copy the file back from `chain/03-dungeon`. Leave this folder as it is: `verify.py` checks that it is the step with this change and nothing else.
