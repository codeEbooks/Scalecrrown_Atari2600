# Scalecrown

The code of **Scalecrown**, Volume 1 of the Atari 2600 Game Manual
Series (CODE & BOOKS) by Eric A. Norton, story and characters by
Rohan A. Banerjee: a complete game for the Atari 2600, written in the
assembly language of its processor, the 6507, and every step of it as
the book builds it.

Under the ruins of Oakhaven lies the Crypt of Scales: sixteen rooms on
four levels, a chest with a key on every level, plates of spikes,
serpents that crawl and chase, and in the last room the Serpent King
before its throne. Sir Roderick goes down with a steel sword and an oak
shield; ten blows on the King's head, and the crown on the throne can
be broken. The title offers music, sound effects or silence.

This package is the companion of the book. Every listing of the game
printed in the book is a part of a file here, line for line, and every
cartridge here can be built again and compared byte for byte
(`verify.py`). The
book's page: https://www.codeandbooksweb.com/books/scalecrown/

## Play without building

`releases/` holds the complete game, Scalecrown 1.0, as two cartridges
of 32 768 bytes: `scalecrown-1.0-ntsc.bin` for an NTSC television and
`scalecrown-1.0-pal.bin` for a PAL one. Open either in Stella, the
emulator: Stella recognises the kind of cartridge by itself, F4SC
(eight banks of 4K and the Superchip's 128 bytes of RAM), and that the
second is for PAL.

- In Stella 7.0 the arrows of the keyboard are the joystick, the space
  bar its button, F1 the SELECT switch and F2 RESET.
- On the title, SELECT chooses MUSIC, SOUND FX or SILENT; the button
  or RESET starts a game.
- In the game the stick walks in eight directions (pushed on a slant
  into a wall, Sir Roderick slides along it) and the button thrusts the
  sword. RESET starts a new game. After GAME OVER or VICTORY comes the
  end screen; then the button goes back to the title.

The game was tested in Stella 7.0 and in the book's test bench
(`tests/`), never on a real console.

| Cartridge | SHA-256 |
|---|---|
| `releases/scalecrown-1.0-ntsc.bin` | `f1e11a99db7acfd1fbe4bce81e6059a2c581dd78ce68215c688bd2891c677f7e` |
| `releases/scalecrown-1.0-pal.bin` | `f0e4da8552daf1560b5a7d4debfab83dceda125403d390880c704e65dffbd62f` |

## What is here

```text
game/          the complete game, 1.0: the master source (game/src),
               whose comments also say in which steps each line exists,
               the design and the tools that make its data (game/assets),
               and its build (game/build)
chain/         the nine steps of the book, 01 to 09: each folder has its
               own copy of every source and tool it needs, builds on its
               own and holds its build; chain.json has their fingerprints
variants/      the 27 experiments of the chapters, each a step with one
               change: 18 guided variants and 9 "Where it breaks"
               versions, built, with a README and the report of its test
               (evidence/)
tests/         the book's test bench (chapter 16)
tools/         build.py, which builds the complete game, and the tools
               that make the chain, the experiments, the figures, the
               register and the recordings
reference/     the register of every instruction of the finished game
               (chapter 16)
releases/      the complete game, NTSC and PAL
verify.py      builds everything again and compares it byte for byte
CHAPTERS.md    chapter by chapter: its step, experiments and tools
TESTING.md     what was tested, with which versions, and the limits
SHA256SUMS.txt the SHA-256 of every file
LICENSE        MIT
```

## What you need

None of these programs is included; download them from their sites.

- **dasm** 2.20.14.1, the assembler (github.com/dasm-assembler/dasm).
  Another version may give other bytes.
- **Stella** 7.0, the emulator (github.com/stella-emu/stella).
- **Python** 3.10 or later (python.org). The builds and `verify.py`
  use its standard library only.
- For the tests only: the Python libraries **py65** 1.2.0 and
  **Pillow**, and for the test of the sound (`--audio`) **numpy**:
  `pip install py65==1.2.0 pillow numpy` installs them. The tests need
  Stella 7.0: with Stella 6.7 the debugger does not press SELECT and
  RESET, and the tests fail.

`tools/build.py` and `verify.py` look for `dasm` on the PATH, the
folders where the system looks for programs; or give its full path
with `--dasm`.

## Build and play a step

Keep the steps as they are and work on a copy (chapter 1): copy
`chain/01-first-room` beside it, say as `chain/01-my-room`, open a
command prompt in the copy and type:

```text
python tools/build.py
```

On Windows, if `python` is not found, try `py`; on Linux and macOS it
may be `python3`. The build writes the data (`game/assets/generated`),
checks that no source line is longer than 60 characters, assembles
`game/src/scalecrown.asm` twice, for NTSC and for PAL, and leaves in
`game/build` the two cartridges, their listings (`.lst`), their symbols
(`.sym`) and `manifest.json`. Open `game/build/scalecrown_ntsc.bin` in
Stella. The copy makes the same cartridges as the step, byte for byte:

| Step | NTSC, SHA-256 | PAL, SHA-256 |
|---|---|---|
| `chain/01-first-room` | `649a80a2795e83a58753b931c64f8a8ee32142481833a6901cfc04c963673feb` | `7777fa9e38c937307ab53b9fc2ae7c1532681ce1076f6ce1d20e244d82002fcc` |
| `chain/02-knight` | `8b7fa99a276319b949e2ab3115e769741bfb18eb424dcc5ab304290d5317c1f5` | `7bbfe20cb0ea3f370a1d92598bc4decc08b8a8f727485be59ba48122569d9ad2` |
| `chain/03-dungeon` | `5af831b20341841bbd00afeb89c63a85e8f105ff2cc6205d90ee63864982f434` | `5f4d085703fa4ab44b8c627e2a304042ccec995fab73f950644bd714f1e00903` |
| `chain/04-keys-doors` | `cf270de8a842edc0e33839f57b48c79e6efcfc27b04eb658d00d34dc4940e7e7` | `a5dda2c0220e72ccc908f91916fabcafd55712a5ab9c9a799f1afb8449381ef6` |
| `chain/05-serpents` | `1abc5e0fad97363dd280d89b736b5a04dcea0d9a22f24ce9113dd4926fa44d2c` | `408972f621e9182b76f52774c947ff09b1a171a30bf26ca38770a8d3ef5521ae` |
| `chain/06-serpent-king` | `914e9a26314c27a55bc6ff5dc50564f7584eabd969a557e83f1e31dcaa65db26` | `7cadc14f3c02e91b2ce2e5fba46f23ebf30049a07881bdaf3a225b93f086164f` |
| `chain/07-sound` | `6a207f70996684d301019579eb914c7324485b8346b12e52f7f0f405216eda42` | `d2108e60a6770e8602f4365d1314aaa63e72135809db23f8425d16f1e2ea0a52` |
| `chain/08-title-and-ends` | `ed3242520d5a392387488487cefe210788de8803c87d2838dd1e22fe9fcb1159` | `51ca5154bec3bf1242b534b917f8f0b71d05b58e490ac9f878086b4ad87e8007` |
| `chain/09-the-hunt` | `f1e11a99db7acfd1fbe4bce81e6059a2c581dd78ce68215c688bd2891c677f7e` | `f0e4da8552daf1560b5a7d4debfab83dceda125403d390880c704e65dffbd62f` |

At the root of the package, `python tools/build.py` builds the complete
game in `game/`, from the master source.

## Check that you build the book's cartridges

```text
python verify.py
```

`verify.py` checks every file against `SHA256SUMS.txt`, builds the
complete game, the nine steps and the 27 experiments again in a
temporary folder, and compares every cartridge, byte for byte, with the
one in the package; it also checks that each experiment is its step
with the chapter's change. A file you changed on purpose is reported
as changed. Your own copies, such as `chain/01-my-room`, are not
checked: `verify.py` builds the folders listed in `chain/chain.json`
and `variants/variants.json`.

## Run the tests

The tests need Stella 7.0 (give its full path as `PATH`), py65,
Pillow and dasm on the PATH (they build the game, the experiments and
the mistakes), and they run from the root of the package:

```text
python tests/verify_chain.py --stella PATH --steps 1 --tv ntsc
python tools/make_variants.py --stella PATH --ids 1a,1b,1x
python tests/verify_0_9.py --stella PATH
```

`verify_chain.py` tests the steps: each plays a route of its own
against the model of the step, in the simulator and in Stella, and
compares the RAM of every frame and the pictures (`--mutations` adds
three mistakes per step, each to be caught). `make_variants.py` builds
the experiments and checks what each one claims. `verify_0_9.py` tests
the complete game in `game/`, from all eight banks (it builds `game/`
first, and takes hours; with `--mutations` it puts each mistake into
`game/src` or `game/assets` in turn and takes it out again). The
reports go to `evidence/`. On Linux without a display, the tests start
Stella under `xvfb-run` by themselves: it must be installed.
[TESTING.md](TESTING.md) tells what was checked, and how.

## Rights

The contents of this package, source code, data, tools, tests and
cartridges, including the figures, rooms, colours, music and sound
effects in `game/assets`, are released under the MIT License: see
[LICENSE](LICENSE). Copyright (c) 2026 Eric A. Norton.

The book is not part of this package and is not covered by this
license: its text, figures, layout and cover are copyright (c) 2026
Eric A. Norton, all rights reserved. Book by Eric A. Norton; story and
characters by Rohan A. Banerjee. ISBN 9798167326781.

Everything in the game was made for it: figures, rooms, music and sound
effects. No ROM, emulator or assembler is included. Atari, Atari 2600
and the other product names are used to identify the machine and the
tools; their respective owners retain their rights. This is an
independent project, not affiliated with or endorsed by Atari or by
those owners.
