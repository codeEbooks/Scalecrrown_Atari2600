"""make_chain.py - the chain of the book, from the master source.

    python3 tools/make_chain.py [--assemble] [--out DIR] [STEP ...]

The master is the working folder (game/src, game/assets, tools):
the complete game, the 1.0, whose comments also carry tags that
say in which steps of the chain each line exists:

  {3}       the line exists from step 3 on (the same as {3-})
  {3-6}     only in steps 3 to 6;  {-6}: up to step 6
  ;|text    a line of earlier steps only, not of the complete
            game (a seam): in the steps of its tag (which must
            end before the last step) it becomes `text` (its
            tag needs no comment: the whole line is one)
  ;{3-6}    alone on a line: the lines up to the next ";{}"
            take this range too (blocks nest; a line keeps the
            narrower range)

In the Python files the same with "#" for ";". A tag is the last
thing on its line and stands in a comment (after a ";" in the
6502 sources, a "#" in Python): the "{1}" of a dasm macro is not
a tag. Since the tags live in comments, the master assembles as
it is into the complete game, and the last step is the master
without its tags: tools/make_chain.py --assemble checks that its
two cartridges are the 1.0's, byte for byte.

For each step it writes chain/NN-name/: game/src (the 6502
files the step includes, starting from scalecrown.asm; the
generated ones come from the step's own game/assets), game/assets
and tools/build.py with the tags taken out, and README.md from
chain/readme/NN.md when there is one. --assemble runs the step's
tools/build.py (dasm, NTSC and PAL, its checks) and writes
chain/chain.json: for each step its files, lines, the bytes free
in each bank and the SHA-256 of its cartridges. Standard library
only.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
STEPS = {1: "01-first-room", 2: "02-knight", 3: "03-dungeon",
         4: "04-keys-doors", 5: "05-serpents", 6: "06-serpent-king",
         7: "07-sound", 8: "08-title-and-ends", 9: "09-the-hunt"}
LAST = max(STEPS)
APPROVED = ROOT / "milestones/1.0-approved/game/build/manifest.json"
# in the book's package there are no milestones: the 1.0 is the
# release (releases/scalecrown-1.0-ntsc.bin and -pal.bin)
RELEASES = ROOT / "releases"


def approved():
    """The SHA-256 of the two cartridges of the 1.0."""
    if APPROVED.exists():
        return {k: v["sha256"] for k, v in json.loads(
            APPROVED.read_text())["cartridges"].items()}
    return {f"scalecrown_{tv}": hashlib.sha256(
        (RELEASES / f"scalecrown-1.0-{tv}.bin").read_bytes()).hexdigest()
        for tv in ("ntsc", "pal")}
RANGE = r"\{(\d*)(-?)(\d*)\}"


def parse(first, dash, last):
    """The steps of a tag: {3} from 3 on, {3-6}, {-6}, {3-}."""
    low = int(first) if first else 1
    high = int(last) if last else LAST
    if first and not dash:
        high = LAST
    if not (1 <= low <= high <= LAST):
        raise ValueError(f"bad range {first}{dash}{last}")
    return low, high


def tagged(text, name, cc):
    """Every line of one master file that is not a block marker:
    (number, first step, last step, a seam, the line without its
    tag and without the seam's mark)."""
    tag_re = re.compile(r"\s*" + RANGE + r"$")
    block_re = re.compile("^" + re.escape(cc) + RANGE + "$")
    blocks = [(1, LAST)]
    for number, line in enumerate(text.splitlines(), 1):
        where = f"{name}:{number}"
        if line == cc + "{}":
            if len(blocks) == 1:
                raise SystemExit(f"{where}: {cc}{{}} without a block")
            blocks.pop()
            continue
        m = block_re.match(line)
        if m:
            try:
                low, high = parse(*m.groups())
            except ValueError as e:
                raise SystemExit(f"{where}: {e}")
            outer = blocks[-1]
            blocks.append((max(low, outer[0]), min(high, outer[1])))
            continue
        low, high = blocks[-1]
        earlier = line.startswith(cc + "|")
        if earlier:
            line = line[2:]
        tag = tag_re.search(line)
        if tag and not (tag.group(1) or tag.group(3)):
            tag = None                  # "{}": not a tag
        if tag and (earlier or cc in line[:tag.start()]):
            try:
                first, second = parse(*tag.groups())
            except ValueError as e:
                raise SystemExit(f"{where}: {e}")
            low, high = max(low, first), min(high, second)
            line = line[:tag.start()].rstrip()
            if re.search(r"\s" + re.escape(cc) + "$", line):
                line = line[:-1].rstrip()      # the tag's comment
        elif earlier:
            raise SystemExit(f"{where}: {cc}| line without a tag")
        if earlier and high >= LAST:
            raise SystemExit(f"{where}: {cc}| line in the last step")
        if low > high:
            raise SystemExit(f"{where}: no step left")
        yield number, low, high, earlier, line
    if len(blocks) != 1:
        raise SystemExit(f"{name}: block not closed")


def numbered_lines(text, step, name, cc):
    """The lines of one file in one step, tags removed, each with
    where it comes from: (number in the master, first step, last
    step, a seam, the line); cc is the comment character (";" or
    "#"). The register of the book (tools/chain_register.py)
    reads them."""
    out, cut_since = [], False
    for number, low, high, seam, line in tagged(text, name, cc):
        if low <= step <= high:
            # a blank line after a blank one, with lines cut
            # between them, goes too (no gaps where they were)
            if not (line.strip() == "" and cut_since and out and
                    out[-1][4].strip() == ""):
                out.append((number, low, high, seam, line))
            if line.strip():
                cut_since = False
            elif out and out[-1][4] is line:
                cut_since = False
        else:
            cut_since = True
    if cut_since:
        while out and out[-1][4].strip() == "":
            out.pop()
    return out


def step_lines(text, step, name, cc):
    """The lines of one file in one step, tags removed."""
    return [t[4] for t in numbered_lines(text, step, name, cc)]


def included(lines):
    return [m.group(1) for line in lines
            for m in [re.match(r'\s+include\s+"([a-z0-9_]+\.asm)"',
                               line)] if m]


def cut(src, dst, step, cc):
    """One file of the master into a step; a file with no line
    in the step is not written (music.py before the sound)."""
    lines = step_lines(src.read_text(encoding="utf-8"), step,
                       src.name, cc)
    if not any(line.strip() for line in lines):
        return []
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text("\n".join(lines) + "\n", encoding="utf-8",
                   newline="\n")
    return lines


def generate(step, out_root):
    target = out_root / STEPS[step]
    if target.exists():
        shutil.rmtree(target)
    src = ROOT / "game/src"
    files, todo, nlines = [], ["scalecrown.asm"], 0
    while todo:
        name = todo.pop(0)
        if name in files or not (src / name).exists():
            continue                    # (generated: from assets)
        lines = cut(src / name, target / "game/src" / name, step, ";")
        files.append(name)
        nlines += len(lines)
        todo += included(lines)
    for p in sorted((ROOT / "game/assets").glob("*.py")):
        cut(p, target / "game/assets" / p.name, step, "#")
    for p in sorted((ROOT / "game/assets").iterdir()):
        if p.is_file() and p.suffix != ".py":
            shutil.copy2(p, target / "game/assets" / p.name)
    cut(ROOT / "tools/build.py", target / "tools/build.py", step, "#")
    readme = ROOT / "chain/readme" / f"{step:02d}.md"
    if readme.exists():
        shutil.copy2(readme, target / "README.md")
    return target, files, nlines


def assemble(target):
    r = subprocess.run([sys.executable, "tools/build.py"],
                       cwd=target, capture_output=True, text=True)
    if r.returncode:
        raise SystemExit(f"{target.name}: build failed\n"
                         f"{r.stdout[-3000:]}{r.stderr[-3000:]}")
    return json.loads((target / "game/build/manifest.json")
                      .read_text())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--assemble", action="store_true")
    ap.add_argument("--out", default=str(ROOT / "chain"))
    ap.add_argument("steps", nargs="*", type=int)
    a = ap.parse_args()
    out_root = Path(a.out)
    out_root.mkdir(parents=True, exist_ok=True)
    report = {}
    jpath = out_root / "chain.json"
    if jpath.exists():
        report = json.loads(jpath.read_text())
    for step in a.steps or sorted(STEPS):
        target, files, nlines = generate(step, out_root)
        info = dict(name=STEPS[step], files=files, lines=nlines)
        msg = f"{target.name}: {len(files)} files, {nlines} lines"
        if not a.assemble:
            # the step is made again without its build: keep the
            # fingerprints of chain.json, which --assemble checks
            for key in ("cartridges", "equal_to_1.0"):
                if key in report.get(str(step), {}):
                    info[key] = report[str(step)][key]
            msg += " (not built: run with --assemble)"
        if a.assemble:
            man = assemble(target)
            info["cartridges"] = man["cartridges"]
            shas = {k: v["sha256"] for k, v in
                    man["cartridges"].items()}
            msg += " " + " ".join(f"{k[11:]} {v[:16]}"
                                  for k, v in shas.items())
            if step == LAST:
                want = approved()
                same = shas == want
                info["equal_to_1.0"] = same
                msg += " = 1.0" if same else " NOT THE 1.0"
                if not same:
                    report[str(step)] = info
                    jpath.write_text(json.dumps(report, indent=1))
                    print(msg)
                    raise SystemExit("the last step is not the 1.0")
        report[str(step)] = info
        print(msg, flush=True)
    jpath.write_text(json.dumps(report, indent=1))


if __name__ == "__main__":
    main()
