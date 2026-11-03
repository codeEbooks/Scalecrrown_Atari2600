"""build.py - Scalecrown: data, two cartridges.

    python3 tools/build.py [--dasm PATH]

1. game/assets/build_assets.py writes the data;
2. dasm assembles game/src/scalecrown.asm for NTSC and PAL
   (32K, F4 with the Superchip);
3. any message from dasm other than "Complete. (0)" is an
   error, and so is a source line longer than 60 characters,
   and so is a branch of the 48-pixel loops (BLOCK in
   title_kernel.asm, HUD48 in hud.asm) that crosses a page:
   taken, it takes a cycle more, and those lines have none;
4. game/build/manifest.json: size, SHA-256, the free bytes
   of each bank, the end of the RAM.
"""
import argparse
import hashlib
import re
import json
import os
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "game", "src")
GEN = os.path.join(ROOT, "game", "assets", "generated")
BUILD = os.path.join(ROOT, "game", "build")
TARGETS = {"scalecrown_ntsc": [], "scalecrown_pal": ["-DPAL=1"]}
# where the tail of each bank starts ($FAA: the first
# trampoline, to the end screens)
BANK_TAIL = {b: 0x1FAA + 0x2000 * b for b in range(8)}


# the source the steps of the book were cut from (the
# finished game) ends some lines with a tag, {3} or {3-6}:
# the steps they belong to; and it keeps the lines of
# earlier steps behind ";|". The measures are those of the
# lines without them.
TAG = re.compile(r"\s*\{(\d+-?\d*|-\d+)\}$")


def untag(line):
    tag = TAG.search(line.rstrip())
    line = TAG.sub("", line.rstrip())
    if tag and re.search(r"\s;$", line):
        line = line[:-1].rstrip()       # the comment of the tag
    return line[2:] if line.startswith(";|") else line


def long_lines(folder):
    bad = []
    for f in sorted(os.listdir(folder)):
        if f.endswith(".asm"):
            for n, ln in enumerate(open(os.path.join(folder, f)), 1):
                if len(untag(ln).expandtabs(8)) > 60:
                    bad.append(f"{f}:{n}")
    return bad


KERNELS = ("room_kernel.asm", "throne_kernel.asm", "hud.asm",
           "title_kernel.asm", "ends_kernel.asm", "main.asm")
BRANCHES = {0x10, 0x30, 0x50, 0x70, 0x90, 0xB0, 0xD0, 0xF0}
# the branches whose time counts, taken: the loops of the
# 48-pixel routines (their branch comes late in a line, with
# work after it before the WSYNC), the delay of the seam and
# the test for it in line B1, the loops that put an object at
# its column (place, the HUD, the title, the end screens),
# marked in the comment
TIMED = (".bl", ".loop", "(k_sdel)", "(k_b1c)", "(pl_div)",
         "(hu_p0)", "(hu_p1)", "(tp_div)", "(ep_div)")


def page_branches(lst):
    """Branches of the kernels that cross a page, from the
    listing: (file, line of the listing, address)."""
    bad, cur = [], None
    for n, line in enumerate(open(lst, errors="replace"), 1):
        if "------- FILE" in line:
            cur = line.split("FILE")[1].split()[0]
            continue
        if cur not in KERNELS:
            continue
        m = re.match(r"\s*\d+\s+([0-9a-fA-F]{4})\s+(?:\S+\s+)?"
                     r"([0-9a-fA-F]{2}) ([0-9a-fA-F]{2})\s", line)
        if not m:
            continue
        a, op, rel = (int(m.group(i), 16) for i in (1, 2, 3))
        if op not in BRANCHES or not any(
                untag(line).endswith(t) for t in TIMED):
            continue
        nxt = a + 2
        to = nxt + (rel - 256 if rel > 127 else rel)
        if nxt >> 8 != to >> 8:
            bad.append(f"{cur}: listing line {n}, ${a:04X}")
    return bad


def symbols(path):
    out = {}
    for line in open(path):
        p = line.split()
        if len(p) >= 2 and not line.startswith("---"):
            try:
                out[p[0]] = int(p[1], 16)
            except ValueError:
                pass
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dasm", default=shutil.which("dasm") or "dasm")
    a = ap.parse_args()
    subprocess.run([sys.executable, os.path.join(
        ROOT, "game", "assets", "build_assets.py")],
        check=True)
    bad = long_lines(SRC)
    if bad:
        sys.exit("lines over 60 characters: " + ", ".join(bad))
    os.makedirs(BUILD, exist_ok=True)
    ver = subprocess.run([a.dasm], capture_output=True,
                         text=True).stdout.split("\n")[0]
    out = dict(dasm=ver, cartridges={})
    for name, flags in TARGETS.items():
        b = os.path.join(BUILD, name)
        r = subprocess.run(
            [a.dasm, "scalecrown.asm", "-f3", "-S", f"-I{GEN}",
             f"-o{b}.bin", f"-l{b}.lst", f"-s{b}.sym"]
            + flags, cwd=SRC, capture_output=True, text=True)
        msg = (r.stdout + r.stderr).split()
        if r.returncode or msg != ["Complete.", "(0)"]:
            sys.exit(f"{name}: dasm says {r.stdout + r.stderr}")
        cross = page_branches(b + ".lst")
        if cross:
            sys.exit(f"{name}: kernel branches across a page: "
                     + ", ".join(cross))
        data = open(b + ".bin", "rb").read()
        if len(data) != 32768:
            sys.exit(f"{name}: {len(data)} bytes, not 32768")
        sym = symbols(b + ".sym")
        free = {f"bank{k}": v - sym[f"bank{k}_end"]
                for k, v in BANK_TAIL.items()}
        out["cartridges"][name] = dict(
            flags=flags, bytes=len(data), free=free,
            ram_end=sym["ram_end"],
            sha256=hashlib.sha256(data).hexdigest())
        print(f"{name}: {hashlib.sha256(data).hexdigest()[:16]} "
              f"free {free} ram ${sym['ram_end']:02X}")
    with open(os.path.join(BUILD, "manifest.json"), "w") as f:
        json.dump(out, f, indent=1)


if __name__ == "__main__":
    main()
