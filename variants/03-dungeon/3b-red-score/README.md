# Experiment 3b: A red score

Chapter 6, "The dungeon and the HUD", prints this experiment and explains it: a guided variant ("Make it yours"). This folder is step 03 (`chain/03-dungeon`) with the change below, built: `game/build` holds its two cartridges, made by its own `tools/build.py` with dasm 2.20.14.1.

## The change

In `game/assets/look.py`, the line

```text
HUD_SCORE_COLOUR = 0x1E
```

becomes

```text
HUD_SCORE_COLOUR = 0x46
```

## What its test saw

`tools/make_variants.py` built it and played it beside step 03, with the same inputs (the head of the step's route, 813 frames on NTSC from bank 0), in the simulator, and in Stella 7.0 for the pictures: 262 lines; the RAM the same; 12 of 12 pictures. It passed, as a guided variant: it keeps the time of every frame and changes what it says it changes. Chapter 16 has it in Table 16.9.

The report of the test is `evidence/3b.json`. `evidence/3b_step.png` and `evidence/3b_change.png` are a picture of the step and the same picture of the experiment, as Stella 7.0 drew them.

## The cartridges

| Cartridge | SHA-256 |
|---|---|
| `game/build/scalecrown_ntsc.bin` | `23ec104c548dc16c8f83ac3128db4658f6a86aef2135d836aa9fbe4d05661744` |
| `game/build/scalecrown_pal.bin` | `16c18b888da99d1ca6a2747fe46bde0f1adfcbd44af0a83c077c5740ae804ff9` |

## Back to the step

To undo the change in your own copy, copy the file back from `chain/03-dungeon`. Leave this folder as it is: `verify.py` checks that it is the step with this change and nothing else.
