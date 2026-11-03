"""Check the package of Scalecrown byte for byte.

Usage: python verify.py [--dasm PATH] [--keep] [NAME ...]

1. Every file listed in SHA256SUMS.txt is present and unchanged. A text
   file that differs only by its line ends (Windows writes CR LF) counts
   as unchanged. A file you have edited for an experiment is named
   here: that is expected.
2. Every program of the package is built again in a temporary folder,
   by its own tools/build.py, with the dasm given (chapter 1): the data
   from game/assets, then the two cartridges, NTSC and PAL.
       game                       the complete game, Scalecrown 1.0,
                                  from the master source
       chain/NN-name              the nine steps of the book
       variants/NN-name/ID-name   the 27 experiments of the chapters
   The data written again must be the data in the package
   (game/assets/generated), and each cartridge must be the one in the
   folder's game/build, byte for byte, with the fingerprint listed in
   chain/chain.json, variants/variants.json or releases/.
3. Each experiment is its step with the change the chapter prints: its
   sources (the files of SHA256SUMS.txt in its game/src, game/assets
   and tools) are those of the step, with the lines of
   variants/variants.json changed, and nothing else.
4. releases/scalecrown-1.0-ntsc.bin and scalecrown-1.0-pal.bin are the
   cartridges of game and of chain/09-the-hunt.

NAME limits the checks to the folders whose path contains it, for
example `chain/03` or `5b`. Only the folders of the package are built:
your own copies, such as chain/01-my-room, are not. Nothing in the
package is changed; the temporary folder is deleted at the end unless
--keep is given.

Needs Python 3.10 or later, standard library only, and dasm on the
PATH or given with --dasm. The cartridges of the package were made with
dasm 2.20.14.1; another version may give other bytes. Exit status 0
when everything matches, 1 when something does not.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent
TVS = ("ntsc", "pal")
SKIP = shutil.ignore_patterns("build", "generated", "evidence",
                              "__pycache__", "*.pyc", "*.log")
TEXT = {".asm", ".py", ".md", ".json", ".txt", ".lst", ".sym", ".csv"}
TEXT_NAMES = {"LICENSE", ".gitattributes", ".gitignore"}


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def lf(data):
    return data.replace(b"\r\n", b"\n")


def listed():
    """The files of SHA256SUMS.txt: {name: SHA-256}."""
    out = {}
    for line in (ROOT / "SHA256SUMS.txt").read_text(
            encoding="utf-8").splitlines():
        if line.strip():
            digest, name = line.split(maxsplit=1)
            out[name.lstrip("*")] = digest
    return out


def check_sums():
    """Files of SHA256SUMS.txt that are missing or changed. A text file
    counts as unchanged with LF or with CR LF line ends."""
    problems, names = [], listed()
    for name, digest in names.items():
        path = ROOT / name
        if not path.is_file():
            problems.append(f"missing: {name}")
            continue
        data = path.read_bytes()
        if sha256(data) == digest:
            continue
        text = path.suffix in TEXT or path.name in TEXT_NAMES
        forms = (lf(data), lf(data).replace(b"\n", b"\r\n"))
        if not (text and any(sha256(f) == digest for f in forms)):
            problems.append(f"changed: {name}")
    return len(names), problems


def programs():
    """(name, base, {tv: expected SHA-256}) of every program; base is
    the folder that holds its game/ and tools/build.py."""
    found = [("game", ROOT, {
        tv: sha256((ROOT / f"releases/scalecrown-1.0-{tv}.bin")
                   .read_bytes()) for tv in TVS})]
    chain = json.loads((ROOT / "chain/chain.json").read_text(
        encoding="utf-8"))
    for step in sorted(chain, key=int):
        info = chain[step]
        carts = info.get("cartridges", {})
        found.append((f"chain/{info['name']}", ROOT / "chain" / info["name"],
                      {tv: carts.get(f"scalecrown_{tv}", {}).get("sha256")
                       for tv in TVS}))
    for vid, v in variants().items():
        found.append((v["folder"], ROOT / v["folder"],
                      {tv: v["cartridges"][f"scalecrown_{tv}"]["sha256"]
                       for tv in TVS}))
    return found


def variants():
    return json.loads((ROOT / "variants/variants.json").read_text(
        encoding="utf-8"))


def run(command, folder):
    result = subprocess.run(command, cwd=folder, capture_output=True,
                            text=True)
    return result.returncode, (result.stdout + result.stderr).strip()


def build(name, base, work, dasm):
    """Build one program in `work`: (cartridges by tv, problems)."""
    if name == "game":
        # the master source: tools/build.py of the root builds game/
        shutil.copytree(base / "game", work / "game", ignore=SKIP)
        (work / "tools").mkdir()
        shutil.copy2(base / "tools/build.py", work / "tools/build.py")
    else:
        shutil.copytree(base, work, ignore=SKIP)
    status, output = run([sys.executable, "tools/build.py", "--dasm",
                          dasm], work)
    if status:
        # what the build said, without Python's traceback
        said = [line.strip() for line in output.splitlines()
                if line.strip() and not line.startswith(" ")
                and not line.startswith(("Traceback", "subprocess."))]
        where = [line.strip() for line in output.splitlines()
                 if line.strip().startswith('File "')
                 and "subprocess.py" not in line]
        return None, ["the build failed: " + " / ".join(
            where[-1:] + said[-4:])]
    problems = same_data(base / "game/assets/generated",
                         work / "game/assets/generated")
    made = {}
    for tv in TVS:
        made[tv] = (work / f"game/build/scalecrown_{tv}.bin").read_bytes()
    return made, problems


def same_data(expected, found):
    """The files of generated/ written again must be those shipped: the
    files of SHA256SUMS.txt in the package's generated/ (a file of your
    own there, such as a .DS_Store, is not one)."""
    prefix = expected.relative_to(ROOT).as_posix() + "/"
    shipped = {n[len(prefix):] for n in listed() if n.startswith(prefix)}
    written = {p.name for p in found.iterdir()} if found.is_dir() else set()
    problems = []
    for name in sorted(shipped | written):
        a, b = expected / name, found / name
        if name not in shipped:
            problems.append(f"generated/{name} is new")
        elif not a.is_file():
            problems.append(f"generated/{name} is missing in the package "
                            "(run tools/make_chain.py --assemble)")
        elif name not in written:
            problems.append(f"generated/{name} was not written")
        elif lf(a.read_bytes()) != lf(b.read_bytes()):
            problems.append(f"generated/{name} differs")
    return problems


def compare(made, shipped):
    """None if the two cartridges are the same, or where they differ:
    the place in the file, and the address the 6507 uses for it (bank n
    at $1000 + $2000 x n, as the book writes it)."""
    if made == shipped:
        return None
    for offset, (x, y) in enumerate(zip(made, shipped)):
        if x != y:
            bank = offset // 4096
            address = 0x1000 + 0x2000 * bank + offset % 4096
            return (f"${offset:04X} in the file differs (bank {bank}, "
                    f"${address:04X} for the 6507): ${x:02X}, in the "
                    f"package ${y:02X}")
    return f"{len(made)} bytes, in the package {len(shipped)}"


def sources(folder, names):
    """The files of a step or an experiment that its build reads: those
    of SHA256SUMS.txt in its game/src, game/assets (not generated) and
    tools; a file of your own there, such as a .DS_Store, is not one."""
    prefix = folder.relative_to(ROOT).as_posix() + "/"
    out = {}
    for name in names:
        if not name.startswith(prefix):
            continue
        rel = name[len(prefix):]
        if rel.startswith(("game/src/", "game/assets/", "tools/")) and \
                not rel.startswith("game/assets/generated/"):
            path = ROOT / name
            out[rel] = lf(path.read_bytes()).decode("utf-8") \
                if path.is_file() else None
    return out


def changed_step(v, names):
    """The step's sources with the experiment's lines changed, as
    tools/make_variants.py changes them."""
    files = sources(ROOT / "chain" / v["step_folder"], names)
    for change in v["change"]:
        lines = files[change["file"]].split("\n")
        hits = [i for i, line in enumerate(lines)
                if line.rstrip() == change["line"]]
        if len(hits) != 1:
            raise ValueError(f"{change['file']}: the line is there "
                             f"{len(hits)} times (or the step has "
                             "changed)")
        if change["becomes"]:
            lines[hits[0]] = change["becomes"]
        else:
            del lines[hits[0]]
        files[change["file"]] = "\n".join(lines)
    return files


def check_experiments(selected):
    problems, count, names = 0, 0, listed()
    for vid, v in variants().items():
        if v["folder"] not in selected:
            continue
        count += 1
        try:
            same = changed_step(v, names) == sources(ROOT / v["folder"],
                                                     names)
        except (KeyError, ValueError, AttributeError) as error:
            same, why = False, str(error)
        else:
            why = ("its sources are not the step's with the change (or "
                   "the step has changed)")
        if not same:
            print(f"  {v['folder']}: {why}")
            problems += 1
    return count, problems


def main():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("names", nargs="*")
    parser.add_argument("--dasm", default=None,
                        help="dasm, if it is not on the PATH")
    parser.add_argument("--keep", action="store_true",
                        help="keep the temporary folder")
    args = parser.parse_args()
    found = shutil.which(args.dasm or "dasm")
    if not found:
        sys.exit(f"{args.dasm or 'dasm'} is not found: add its folder to "
                 "the PATH or give its full path with --dasm.")
    dasm = str(Path(found).resolve())   # the builds run elsewhere
    wanted = [n.replace("\\", "/").strip("/") for n in args.names]
    status, version = run([dasm], ROOT)
    print(f"Python {sys.version.split()[0]}; "
          f"{version.splitlines()[0] if version else dasm}")
    failures = 0

    count, problems = check_sums()
    print(f"\nSHA256SUMS.txt: {count} files, "
          f"{'all unchanged' if not problems else f'{len(problems)} not'}")
    for line in problems:
        print("  " + line)
    failures += len(problems)

    selected = [p for p in programs()
                if not wanted or any(n in p[0] for n in wanted)]
    if not selected:
        print(f"\nNo program of the package matches {' '.join(wanted)}")
        print("\nResult: FAIL")
        return 1
    print(f"\nPrograms built again and compared: {len(selected)}, "
          "two cartridges each")
    scratch = Path(tempfile.mkdtemp(prefix="scalecrown-verify-"))
    width = max([len(p[0]) for p in selected] + [4])
    same = 0
    try:
        for number, (name, base, expected) in enumerate(selected):
            made, problems = build(name, base, scratch / f"{number:02d}",
                                   dasm)
            if made is not None:
                for tv in TVS:
                    shipped = base / f"game/build/scalecrown_{tv}.bin"
                    if not shipped.is_file():
                        problems.append(f"no {shipped.relative_to(ROOT)}")
                        continue
                    difference = compare(made[tv], shipped.read_bytes())
                    if difference:
                        problems.append(f"{tv}: {difference}")
                    if not expected[tv]:
                        problems.append(f"{tv}: no fingerprint in "
                                        "chain/chain.json (run "
                                        "tools/make_chain.py --assemble)")
                    elif sha256(made[tv]) != expected[tv]:
                        problems.append(f"{tv}: not the fingerprint "
                                        f"listed ({expected[tv][:16]})")
            if made is not None and not problems:
                same += 1
                print(f"  {name:{width}}  NTSC {sha256(made['ntsc'])[:16]}"
                      f"  PAL {sha256(made['pal'])[:16]}  same")
            else:
                print(f"  {name:{width}}  DIFFERENT")
                for line in problems:
                    print("      " + line)
                failures += 1
    finally:
        if args.keep:
            print(f"\nThe builds are in {scratch}")
        else:
            shutil.rmtree(scratch, ignore_errors=True)
    print(f"  {same} of {len(selected)} identical to the package")

    total, wrong = check_experiments({p[0] for p in selected})
    print(f"\nExperiments that are their step with the chapter's change: "
          f"{total - wrong} of {total}")
    failures += wrong

    releases = {tv: (ROOT / f"releases/scalecrown-1.0-{tv}.bin")
                .read_bytes() for tv in TVS}
    last = {tv: (ROOT / f"chain/09-the-hunt/game/build/scalecrown_{tv}.bin")
            .read_bytes() for tv in TVS}
    game = {tv: (ROOT / f"game/build/scalecrown_{tv}.bin").read_bytes()
            for tv in TVS}
    one = releases == last == game
    said = "the cartridges of game and of step 09" if one else \
        "NOT the cartridges of game and of step 09"
    print(f"\nreleases/: {said}")
    failures += not one

    print("\nResult:", "PASS" if not failures else f"FAIL ({failures})")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
