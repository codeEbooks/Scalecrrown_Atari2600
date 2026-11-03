"""stella_palette.py - the colours of the TIA as Stella draws them.

    python3 tools/stella_palette.py --stella PATH

Assembles game/src/palette.asm for NTSC and PAL (one colour
per line), takes a picture with Stella's debugger and reads the
128 colours of each television. Writes
game/assets/palette_stella.json: {"ntsc": {"1E": [r,g,b],
...}, "pal": {...}}. The art tools use it to show the figures
in the colours of the captures, and to find for every NTSC
colour the nearest PAL one.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tests"))
import stella_run                                    # noqa: E402

ROW0 = {"ntsc": 14, "pal": 13}    # image row of visible line 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stella", required=True)
    ap.add_argument("--dasm", default=shutil.which("dasm") or "dasm")
    a = ap.parse_args()
    from PIL import Image
    work = tempfile.mkdtemp()
    out = {}
    for tv in ("ntsc", "pal"):
        rom = os.path.join(work, f"palette_{tv}.bin")
        flags = ["-DPAL=1"] if tv == "pal" else []
        r = subprocess.run(
            [a.dasm, "palette.asm", "-f3", "-S",
             "-I" + os.path.join(ROOT, "game", "src"), "-o" + rom]
            + flags, cwd=os.path.join(ROOT, "game", "src"),
            capture_output=True, text=True)
        if (r.stdout + r.stderr).split() != ["Complete.", "(0)"]:
            sys.exit(r.stdout + r.stderr)
        st = stella_run.run(a.stella, rom, 10, shots=(10,))
        im = Image.open(st["shots"][10]).convert("RGB")
        out[tv] = {f"{2 * k:02X}": list(im.getpixel(
            (100, ROW0[tv] + k + 1))) for k in range(128)}
        out[tv + "_stella"] = st["version"]
    path = os.path.join(ROOT, "game", "assets",
                        "palette_stella.json")
    with open(path, "w") as f:
        json.dump(out, f, indent=0)
    print("written", path)


if __name__ == "__main__":
    main()
