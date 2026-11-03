"""stella_run.py - run a cartridge in Stella from its debugger.

The way found in the first trials of Stella, made into a
module for every milestone:

- Stella starts in its debugger with autoexec.script;
- for each frame the script sets the joystick (only when it
  changes), runs one frame and, through `exec`, dumps the RAM
  to <cart>_dbg_fNNNN.dump (a fixed name);
- at the frames asked for it also saves the picture;
- at the end it saves the access counters and closes Stella.

Waiting for Stella (0.9): as long as it writes a new frame at
least every STALL seconds, however long the whole run takes (a
slow computer, or Stella under wine, is not a stuck Stella).
Until the 0.8 the wait was 300 seconds in all: under wine the
route of the 0.9 takes longer, and the kill reached only the
wrapper, so the Stella that was killed went on writing frames
next to the one started again. Now a Stella that stops is
killed with its children (xvfb-run, wine), and started again,
on clean folders, only if it never wrote a frame.

Debugger numbers are hexadecimal unless written with #, and
joy0Right 0 means pressed (the wire is active low); so does
joy0Fire 0. The console switches are set with swchb (bit 0
RESET, bit 1 SELECT, 0 = down: 0b is no switch down, 0a is
RESET down, 09 SELECT; written with the 0, because a alone is
the accumulator). joystick(k) gives SWCHA for frame k, or
(SWCHA, fire, reset[, select]).

    run(stella, rom, frames, joystick=None, shots=(),
        startbank=None) -> dict(ram=[...], shots={...},
                                reads=set(...), seconds=...)
"""
import os
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import time

DIRS = (("Right", 0x80), ("Left", 0x40), ("Down", 0x20),
        ("Up", 0x10))
STALL = 120     # seconds without a new frame: Stella is stuck


def _start(cmd, env):
    """Stella in a process group of its own (POSIX: a session,
    with xvfb-run and wine; Windows: a group), to be killed
    whole."""
    extra = dict(start_new_session=True) if os.name == "posix" \
        else dict(creationflags=getattr(
            subprocess, "CREATE_NEW_PROCESS_GROUP", 0))
    return subprocess.Popen(cmd, env=env,
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL, **extra)


def _kill(p):
    try:
        if os.name == "posix":
            os.killpg(p.pid, signal.SIGKILL)
        else:
            subprocess.run(["taskkill", "/F", "/T", "/PID",
                            str(p.pid)], capture_output=True)
            p.kill()
    except OSError:
        pass
    try:
        p.wait(30)
    except subprocess.TimeoutExpired:
        pass


def _wait(p, home, cart, frames):
    """Wait while Stella writes frames; kill it if it writes none
    for STALL seconds. Returns the number of frames written. The
    seconds are counted in steps of at most 2: a computer that
    sleeps, or a run stopped while the other one records the
    sound, is not a Stella that stopped."""
    k, idle, t = 0, 0.0, time.time()
    while True:
        done = p.poll() is not None
        now = time.time()
        idle += min(now - t, 2.0)
        t = now
        while k < frames and os.path.exists(os.path.join(
                home, f"{cart}_dbg_f{k + 1:04d}.dump")):
            k += 1
            idle = 0.0
        if done:
            return k
        if idle > STALL:
            _kill(p)
            return k
        time.sleep(0.5)


def _inputs(joystick, k):
    """joystick(k) -> SWCHA, or (SWCHA, fire, reset[, select])."""
    v = joystick(k) if joystick else 0xFF
    if isinstance(v, tuple):
        return (tuple(v) + (False,))[:4]
    return v, False, False, False


def _script(work, frames, joystick, shots):
    # forward slashes: the debugger reads the path of exec as
    # one word, and Windows accepts them as well
    path = work.replace("\\", "/")
    with open(os.path.join(work, "step.script"), "w") as f:
        f.write("frame #1\ndump 80 ff 1\n")
    with open(os.path.join(work, "shot.script"), "w") as f:
        f.write("frame #1\ndump 80 ff 1\nsaveSnap\n")
    lines = ["frame #1"]                 # power-on to first VSYNC
    last = None
    for k in range(1, frames + 1):
        swcha, fire, reset, select = _inputs(joystick, k)
        swchb = 0x0B & ~(1 if reset else 0) & ~(2 if select else 0)
        state = tuple(0 if not swcha & bit else 1
                      for _, bit in DIRS) + (int(not fire), swchb)
        if state != last:
            for i, (name, _) in enumerate(DIRS):
                if last is None or last[i] != state[i]:
                    lines.append(f"joy0{name} {state[i]}")
            if last is None or last[4] != state[4]:
                lines.append(f"joy0Fire {state[4]}")
            if last is None or last[5] != state[5]:
                # SWCHB: bit 0 RESET, bit 1 SELECT (0 = down),
                # bit 3 colour; written 0b, 0a, 09, 08 (a alone
                # would be the accumulator)
                lines.append(f"swchb {state[5]:02x}")
            last = state
        name = "shot" if k in shots else "step"
        lines.append(f"exec {path}/{name}.script f{k:04d}")
    lines += ["saveAccess", "exitRom"]
    return "\n".join(lines) + "\n"


def read_dump(path):
    ram = bytearray()
    for line in open(path):
        if ":" in line:
            for tok in line.split(":", 1)[1].split():
                if tok != "-":
                    ram.append(int(tok, 16))
    return bytes(ram)


def read_access(path):
    """saveAccess CSV: the ROM offsets read, bank by bank."""
    out, bank = set(), None
    for line in open(path):
        if line.startswith("Bank"):
            words = line.replace("/", " ").split()
            bank = int(words[1]) if words[-1] == "reads:" else None
            continue
        if bank is None or line[:1] not in "0123456789abcdef":
            continue
        cells = [c.strip() for c in line.split(",") if c.strip()]
        for addr, count in zip(cells[0::2], cells[1::2]):
            if int(count):
                out.add((bank, int(addr, 16) & 0x0FFF))
    return out


def version(stella):
    """From -help (Linux); on Windows Stella prints nothing, so
    the name of its folder (Stella-7.0c) is the version."""
    try:
        r = subprocess.run([stella, "-help"], capture_output=True,
                           text=True, timeout=30)
        for ln in r.stdout.splitlines():
            if "Stella version" in ln:
                return ln.strip()
    except (OSError, subprocess.TimeoutExpired):
        pass
    folder = os.path.basename(os.path.dirname(os.path.abspath(
        stella)))
    return f"folder {folder}" if folder.lower().startswith(
        "stella") else "?"


def run(stella, rom, frames, joystick=None, shots=(),
        startbank=None, keep=None):
    work = tempfile.mkdtemp(prefix="stella_")
    home = os.path.join(work, "home")
    base = os.path.join(work, "base")
    snaps = os.path.join(work, "snaps")
    for d in (home, base, snaps):
        os.makedirs(d)
    with open(os.path.join(base, "autoexec.script"), "w") as f:
        f.write(_script(work, frames, joystick, shots))
    cmd = [stella, "-basedir", base, "-userdir", home,
           "-snapsavedir", snaps, "-debug", "-uimessages", "0",
           "-exitlauncher", "0", "-sound", "0"]
    if startbank is not None:
        cmd += ["-startbank", str(startbank)]
    cmd.append(rom)
    env = dict(os.environ)
    if sys.platform.startswith("linux"):
        env["XDG_RUNTIME_DIR"] = tempfile.mkdtemp()
        if not env.get("DISPLAY"):
            cmd = ["xvfb-run", "-a"] + cmd
    cart = os.path.splitext(os.path.basename(rom))[0]
    t0 = time.time()
    for attempt in range(3):            # xvfb-run can fail to
        p = _start(cmd, env)            # start: try again
        if _wait(p, home, cart, frames):
            break                       # it ran (to the end or not)
        for d in (home, snaps):         # never started: again, on
            for f in os.listdir(d):     # clean folders
                fp = os.path.join(d, f)
                if os.path.isfile(fp):
                    os.remove(fp)
    ram = []
    for k in range(1, frames + 1):
        path = os.path.join(home, f"{cart}_dbg_f{k:04d}.dump")
        ram.append(read_dump(path) if os.path.exists(path)
                   else None)
    pics = {}
    for f in sorted(os.listdir(snaps)):
        if f.endswith(".png"):
            k = int(re.match(r"\d+", f.split("_dbg_f")[1]).group())
            pics[k] = os.path.join(snaps, f)
    if keep:
        os.makedirs(keep, exist_ok=True)
        for k, p in list(pics.items()):
            dst = os.path.join(keep, f"{cart}_f{k:04d}.png")
            shutil.copy(p, dst)
            pics[k] = dst
    csv = [f for f in os.listdir(home) if f.endswith(".csv")]
    reads = read_access(os.path.join(home, csv[0])) if csv \
        else set()
    return dict(ram=ram, shots=pics, reads=reads,
                seconds=round(time.time() - t0, 1),
                version=version(stella), work=work)
