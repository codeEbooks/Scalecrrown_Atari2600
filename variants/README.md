# The experiments

Each step comes with three experiments, printed in the chapters that
work on it: two guided variants ("Make it yours"), each with its safe
values and the way back, and a classic mistake made on purpose ("Where
it breaks"). Here each one is a folder: its step with the change the
chapter prints, built. The changes and what each one claims are in
`tools/variants.py`; `tools/make_variants.py` makes them again from the
steps and tests them; `variants.json` lists the changes and the
fingerprints of the cartridges, which `verify.py` checks.

| Folder | Chapter | Kind | Title | What its test saw |
|---|---|---|---|---|
| `variants/01-first-room/1a-upper-crypt-in-blue` | 4 | variant | The Upper Crypt in blue | 262 lines; the RAM the same; 2 of 2 pictures |
| `variants/01-first-room/1b-sir-roderick-comes-in-further-west` | 2 | variant | Sir Roderick comes in further west | 262 lines; `kx` from frame 1; 2 of 2 pictures |
| `variants/01-first-room/1x-wsync-forgotten` | 3 | where it breaks | A WSYNC forgotten | 261 lines; 2 of 2 pictures |
| `variants/02-knight/2a-faster-walk` | 5 | variant | A faster walk | 262 lines; `hacc` from frame 46; 3 of 4 pictures |
| `variants/02-knight/2b-longer-thrust` | 5 | variant | A longer thrust | 262 lines; `thrust` from frame 171 |
| `variants/02-knight/2x-hmove-forgotten` | 5 | where it breaks | The HMOVE forgotten | 262 lines; the RAM the same; 3 of 3 pictures |
| `variants/03-dungeon/3a-water-shimmers-twice-as-fast` | 6 | variant | The water shimmers twice as fast | 262 lines; the RAM the same; 1 of 22 pictures |
| `variants/03-dungeon/3b-red-score` | 6 | variant | A red score | 262 lines; the RAM the same; 12 of 12 pictures |
| `variants/03-dungeon/3x-row-two-cycles-early` | 6 | where it breaks | The row two cycles early | 262 lines; the RAM the same; 12 of 12 pictures |
| `variants/04-keys-doors/4a-richer-chests` | 7 | variant | Richer chests | 262 lines; `score+1` from frame 949; 1 of 5 pictures |
| `variants/04-keys-doors/4b-spikes-stay-up-longer` | 7 | variant | The spikes stay up longer | 262 lines; `spk` from frame 229 |
| `variants/04-keys-doors/4x-pf2-never-written-in-room` | 7 | where it breaks | PF2 never written in the room | 262 lines; the RAM the same; 5 of 5 pictures |
| `variants/05-serpents/5a-slower-serpents-in-first-level` | 8 | variant | Slower serpents in the first level | 262 lines; `SC_ACC` from frame 1 |
| `variants/05-serpents/5b-softer-bite` | 9 | variant | A softer bite | 262 lines; `energy` from frame 188; 2 of 3 pictures |
| `variants/05-serpents/5x-seam-without-resp1` | 8 | where it breaks | The seam without RESP1 | 262 lines; the RAM the same; the seam wrong; 2 of 3 pictures |
| `variants/06-serpent-king/6a-five-blows-beat-king` | 11 | variant | Five blows beat the King | 262 lines; `SC_KS` from frame 11 909 |
| `variants/06-serpent-king/6b-slower-venom` | 11 | variant | Slower venom | 262 lines; `SC_VA` from frame 11 698 |
| `variants/06-serpent-king/6x-venom-never-switched-on` | 10 | where it breaks | The venom never switched on | 262 lines; the RAM the same; 1 of 29 pictures |
| `variants/07-sound/7a-faster-theme` | 12 | variant | A faster theme | 262 lines; `mclock` from frame 1; the sound |
| `variants/07-sound/7b-higher-blip-serpent-killed` | 13 | variant | A higher blip for a serpent killed | 262 lines; the RAM the same; the sound |
| `variants/07-sound/7x-hiss-left-on` | 13 | where it breaks | A hiss left on | 262 lines; `sfxi` from frame 224; the sound |
| `variants/08-title-and-ends/8a-end-screen-waits-longer-button` | 14 | variant | The end screen waits longer for the button | 262 lines; `won` from frame 12 996 |
| `variants/08-title-and-ends/8b-longer-game-over` | 14 | variant | A longer GAME OVER | 262 lines; `screen` from frame 13 679; 1 of 56 pictures |
| `variants/08-title-and-ends/8x-lament-never-starts` | 14 | where it breaks | The lament never starts | 262 lines; `vpos` from frame 13 619; the sound |
| `variants/09-the-hunt/9a-gentler-sprint` | 15 | variant | A gentler sprint | 262 lines; `SC_SPR` from frame 131 |
| `variants/09-the-hunt/9b-they-come-back-sooner` | 15 | variant | They come back sooner | 262 lines; `SC_GT` from frame 945 |
| `variants/09-the-hunt/9x-serpent-that-never-comes-back` | 15 | where it breaks | A serpent that never comes back | 262 lines; `zcoarse` from frame 1 185; 1 of 21 pictures |

The `SC_` names are bytes of the Superchip's RAM, named in
`game/src/scalecrown.asm`. Make your own experiments on a copy of a
step, not in these folders.
