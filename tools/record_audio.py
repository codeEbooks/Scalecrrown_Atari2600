"""record_audio.py - what Stella plays, into a WAV (and an MP3).

    python3 tools/record_audio.py --stella PATH ROM OUT.wav
                                  [--seconds 24] [--hold F]

Stella runs at its normal speed (not in the debugger: there it
runs the frames as fast as it can and drops the sound) with the
"disk" audio driver of SDL, which writes the sound it would
play into a file: 32-bit floats, two channels, 44 100 a second.
--hold F starts with the fire button held (-holdjoy0 F: the
title starts a game at once), --hold S with SELECT held
(-holdselect: the first sound mode after MUSIC). The joystick
cannot be used: Stella is not driven by a script here.

The WAV is 16-bit mono, 44 100 Hz; with ffmpeg in the PATH an
MP3 is written next to it. For listening; the tests use it in
tests/audio_check.py. Tried on Linux, and with the Windows
Stella under wine.
"""
import argparse
import os
import shutil
import struct
import subprocess
import sys
import tempfile
import wave


def record(stella, rom, out, seconds=24.0, hold=""):
    work = tempfile.mkdtemp(prefix="stella_audio_")
    raw = os.path.join(work, "out.raw")
    for d in ("home", "base"):
        os.makedirs(os.path.join(work, d))
    cmd = [stella, "-userdir", os.path.join(work, "home"),
           "-basedir", os.path.join(work, "base"),
           "-audio.enabled", "1", "-audio.sample_rate", "44100",
           "-uimessages", "0"]
    if "F" in hold:
        cmd += ["-holdjoy0", "F"]
    if "S" in hold:
        cmd += ["-holdselect"]
    cmd.append(rom)
    env = dict(os.environ, SDL_AUDIODRIVER="disk",
               SDL_DISKAUDIOFILE=raw,
               XDG_RUNTIME_DIR=tempfile.mkdtemp())
    if sys.platform.startswith("linux") and not env.get("DISPLAY"):
        cmd = ["xvfb-run", "-a"] + cmd
    p = subprocess.Popen(cmd, env=env, stdout=subprocess.DEVNULL,
                         stderr=subprocess.DEVNULL,
                         start_new_session=True)
    try:
        p.wait(seconds)
    except subprocess.TimeoutExpired:
        if hasattr(os, "killpg"):
            os.killpg(p.pid, 15)    # Stella and xvfb-run
        else:
            p.terminate()           # Windows: Stella.exe
        p.wait(10)
    data = open(raw, "rb").read() if os.path.exists(raw) else b""
    n = len(data) // 8
    left = struct.unpack(f"<{2 * n}f", data[:8 * n])[0::2]
    with wave.open(out, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(44100)
        w.writeframes(b"".join(struct.pack(
            "<h", max(-32767, min(32767, int(x * 32767 * 3))))
            for x in left))
    shutil.rmtree(work, ignore_errors=True)
    if shutil.which("ffmpeg"):
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i",
                        out, "-b:a", "128k",
                        os.path.splitext(out)[0] + ".mp3"])
    return n / 44100.0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stella", required=True)
    ap.add_argument("--seconds", type=float, default=24.0)
    ap.add_argument("--hold", default="")
    ap.add_argument("rom")
    ap.add_argument("out")
    a = ap.parse_args()
    s = record(a.stella, a.rom, a.out, a.seconds, a.hold)
    print(a.out, f"{s:.1f} s")


if __name__ == "__main__":
    main()
