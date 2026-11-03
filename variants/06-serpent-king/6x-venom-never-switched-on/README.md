# Experiment 6x: The venom never switched on

Chapter 10, "The throne room", prints this experiment and explains it: a "Where it breaks" version. This folder is step 06 (`chain/06-serpent-king`) with the change below, built: `game/build` holds its two cartridges, made by its own `tools/build.py` with dasm 2.20.14.1.

## The change

In `game/src/throne_kernel.asm`, the line

```text
        sta     ENAM1           ; 20 the venom: bit 1
```

becomes

```text
        sta     $2D             ; 20 the venom: bit 1
```

## What its test saw

`tools/make_variants.py` built it and played it beside step 06, with the same inputs (the head of the step's route, 11 728 frames on NTSC from bank 0), in the simulator, and in Stella 7.0 for the pictures: 262 lines; the RAM the same; 1 of 29 pictures. It passed, as a "Where it breaks" version: it breaks what the chapter says it breaks. Chapter 16 has it in Table 16.9.

The report of the test is `evidence/6x.json`. `evidence/6x_step.png` and `evidence/6x_change.png` are a picture of the step and the same picture of the experiment, as Stella 7.0 drew them.

## The cartridges

| Cartridge | SHA-256 |
|---|---|
| `game/build/scalecrown_ntsc.bin` | `b37b33272e2052a96f5e3a07d6a2d76ed84c47ef9c47d7629b6fae27c1fc2440` |
| `game/build/scalecrown_pal.bin` | `5cadac799959259dfb533b9959c9bc1bb0c9c2f70b8b59f29e9b6b7ef9f483d9` |

## Back to the step

To undo the change in your own copy, copy the file back from `chain/06-serpent-king`. Leave this folder as it is: `verify.py` checks that it is the step with this change and nothing else.
