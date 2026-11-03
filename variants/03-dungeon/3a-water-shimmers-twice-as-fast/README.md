# Experiment 3a: The water shimmers twice as fast

Chapter 6, "The dungeon and the HUD", prints this experiment and explains it: a guided variant ("Make it yours"). This folder is step 03 (`chain/03-dungeon`) with the change below, built: `game/build` holds its two cartridges, made by its own `tools/build.py` with dasm 2.20.14.1.

## The change

In `game/src/main.asm`, the line

```text
        and     #8
```

becomes

```text
        and     #4
```

## What its test saw

`tools/make_variants.py` built it and played it beside step 03, with the same inputs (the head of the step's route, 1 751 frames on NTSC from bank 0), in the simulator, and in Stella 7.0 for the pictures: 262 lines; the RAM the same; 1 of 22 pictures. It passed, as a guided variant: it keeps the time of every frame and changes what it says it changes. Chapter 16 has it in Table 16.9.

The report of the test is `evidence/3a.json`. `evidence/3a_step.png` and `evidence/3a_change.png` are a picture of the step and the same picture of the experiment, as Stella 7.0 drew them.

## The cartridges

| Cartridge | SHA-256 |
|---|---|
| `game/build/scalecrown_ntsc.bin` | `1ba91a626483f3b8843984e9a9a19a32c53a849c7ad019f101ca85d75f2f7976` |
| `game/build/scalecrown_pal.bin` | `600a247ab7b5e214560dc01209722d9ee59ab9661ab473bb48279a4e7f32d75b` |

## Back to the step

To undo the change in your own copy, copy the file back from `chain/03-dungeon`. Leave this folder as it is: `verify.py` checks that it is the step with this change and nothing else.
