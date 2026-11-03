"""vcs_sim.py - a small Atari 2600 simulator for the tests.

It is not an emulator of the picture: it runs the 6507 (py65,
cycle counts of the 6502), the RIOT timer, the joystick port
and F8 bank switching, and it keeps the TIA writes with the
cycle at which each one happens. That is enough to stop the
program at a label in every frame, give it the joystick, the
fire button and the switches (swchb, bit 0 RESET: 0 down),
read its RAM, count the lines of every frame and the cycles of a
routine, and know which instructions ran. The picture comes
from Stella; the two are compared on the same program.

Rules that matter for the 2600 and are modelled here:
- the 6507 sees 13 address lines: everything is mirrored;
- a write to WSYNC stops the processor until the end of the
  line (76 cycles a line);
- a frame starts when VSYNC is switched on;
- TIM1T/TIM8T/TIM64T/T1024T: INTIM drops by one on the cycle
  after the write and then once per interval; after zero it
  wraps to $FF and counts every cycle;
- F8: an access to $1FF8 selects bank 0, $1FF9 bank 1;
- F4: an access to $1FF4 ... $1FFB selects bank 0 ... 7;
- Superchip (SC): 128 bytes of RAM in the cartridge, written
  at $1000-$107F and read at $1080-$10FF in every bank. A read
  of the write side is a bug on a real cartridge (it writes
  whatever is on the bus): the simulator keeps a list of them.
  As Stella does, a cartridge is taken as SC when in every
  bank the first 128 bytes repeat in the next 128.
"""
import random

from py65.devices.mpu6502 import MPU

LINE = 76                       # processor cycles in a line
_SIZE = {"imp": 1, "acc": 1, "abs": 3, "abx": 3, "aby": 3,
         "ind": 3}
LENGTH = [_SIZE.get(mode, 2) for _, mode in MPU.disassemble]
INTERVALS = (1, 8, 64, 1024)


class Bus:
    """The address decoding of the 2600, seen by py65."""

    def __init__(self, vcs):
        self.vcs = vcs

    def __getitem__(self, addr):
        return self.vcs.read(addr)

    def __setitem__(self, addr, value):
        self.vcs.write(addr, value)


class VCS:
    def __init__(self, rom, start_bank=1, ram_seed=None):
        if len(rom) not in (4096, 8192, 32768):
            raise ValueError("4K, 8K (F8) or 32K (F4) only")
        self.rom = bytes(rom)
        self.banks = len(rom) // 4096
        self.bank = start_bank if self.banks > 1 else 0
        self.hot = {2: 0xFF8, 8: 0xFF4}.get(self.banks)
        self.sc = self.banks > 1 and all(
            self.rom[b * 4096:b * 4096 + 128] ==
            self.rom[b * 4096 + 128:b * 4096 + 256]
            for b in range(self.banks))
        rnd = random.Random(ram_seed)
        self.ram = bytearray(
            rnd.randrange(256) if ram_seed is not None else 0
            for _ in range(128))
        self.sc_ram = bytearray(
            rnd.randrange(256) if ram_seed is not None else 0
            for _ in range(128))
        self.sc_bad_reads = []      # (cycle, address)
        self.swcha = 0xFF           # joysticks: 0 = pressed
        self.swchb = 0x0B           # switches: none pressed
        self.fire0 = False
        self.tia_log = []           # (cycle, register, value)
        self.vsync_on = False
        self.frame_starts = []      # cycle of each VSYNC on
        self.vsync_cycles = []      # length of each VSYNC
        self.timer_write = None     # (cycle, value, interval)
        self.wsync = False
        self.executed = set()       # (bank, address)
        self.rom_reads = set()      # (bank, offset), any read
        self.breaks = {}            # address -> callback
        # pc=None: py65 then takes the start from the reset
        # vector at $FFFC (with its default pc=0 it would run
        # a BRK at $0000 and arrive through $FFFE instead)
        self.mpu = MPU(memory=Bus(self), pc=None)
        self.access_cycle = 0
        self.mpu.reset()            # reads the reset vector

    # -- time ----------------------------------------------
    @property
    def cycle(self):
        return self.mpu.processorCycles

    def position(self, cycle=None):
        """(frame, line, cycle in line) from the last VSYNC."""
        c = self.cycle if cycle is None else cycle
        starts = [s for s in self.frame_starts if s <= c]
        if not starts:
            return (0, c // LINE, c % LINE)
        base = (starts[-1] // LINE) * LINE
        return (len(starts), (c - base) // LINE, (c - base) % LINE)

    # -- the bus -------------------------------------------
    def _cart(self, a):
        off = a & 0x0FFF
        if self.hot is not None and \
                self.hot <= off < self.hot + self.banks:
            self.bank = off - self.hot
        return off

    def read(self, addr):
        a = addr & 0x1FFF
        if a & 0x1000:
            off = self._cart(a)
            if self.sc and off < 0x100:
                if off < 0x80:
                    self.sc_bad_reads.append((self.cycle, a))
                    return 0
                return self.sc_ram[off - 0x80]
            self.rom_reads.add((self.bank, off))
            return self.rom[self.bank * 4096 + off]
        if not a & 0x80:                       # TIA read side
            r = a & 0x0F
            if r == 0x0C:                      # INPT4
                return 0x00 if self.fire0 else 0x80
            return 0x00
        if not a & 0x200:                      # RAM
            return self.ram[a & 0x7F]
        if a & 0x04:                           # timer
            return self.intim() if not a & 1 else 0
        if (a & 3) == 0:
            return self.swcha
        if (a & 3) == 2:
            return self.swchb                  # SWCHB
        return 0x00

    def write(self, addr, value):
        a = addr & 0x1FFF
        t = self.access_cycle
        if a & 0x1000:
            off = self._cart(a)
            if self.sc and off < 0x80:
                self.sc_ram[off] = value
            return
        if not a & 0x80:                       # TIA write side
            r = a & 0x3F
            self.tia_log.append((t, r, value))
            if r == 0x00:                      # VSYNC
                on = bool(value & 2)
                if on and not self.vsync_on:
                    self.frame_starts.append(t)
                if not on and self.vsync_on:
                    self.vsync_cycles.append(t - self.frame_starts[-1])
                self.vsync_on = on
            elif r == 0x02:                    # WSYNC
                self.wsync = True
            return
        if not a & 0x200:
            self.ram[a & 0x7F] = value
            return
        if (a & 0x14) == 0x14:                 # timer
            self.timer_write = (t, value, INTERVALS[a & 3])

    def intim(self):
        if self.timer_write is None:
            return 0
        t0, n, iv = self.timer_write
        d = self.access_cycle - t0
        if d <= 0:
            return n
        k = (d - 1) // iv
        if k <= n - 1:
            return n - 1 - k
        wrap = 1 + n * iv                      # first $FF
        return (0xFF - (d - wrap)) & 0xFF

    # -- running -------------------------------------------
    def step(self):
        mpu = self.mpu
        pc = mpu.pc
        cb = self.breaks.get(pc)
        if cb:
            cb(self)
        op = self.read(pc)
        self.executed.add((self.bank, pc & 0x1FFF))
        # the bytes of the instruction, all fetched by the 6507
        # (py65 skips the operand of a branch not taken)
        for i in range(1, LENGTH[op]):
            self.rom_reads.add((self.bank, (pc + i) & 0x0FFF))
        start = mpu.processorCycles
        # every access is put on the last cycle of the
        # instruction: right for loads, stores and BIT,
        # which are what the 2600 code uses on TIA and RIOT
        self.access_cycle = start + mpu.cycletime[op] - 1
        mpu.step()
        if self.wsync:
            self.wsync = False
            r = mpu.processorCycles % LINE
            if r:
                mpu.processorCycles += LINE - r

    def run_frames(self, n, limit=200000):
        """Run until n more frames have started."""
        target = len(self.frame_starts) + n
        stop = self.cycle + n * limit
        while len(self.frame_starts) < target:
            self.step()
            if self.cycle > stop:
                raise RuntimeError("no VSYNC: the frame never ends")

    def lines_per_frame(self):
        s = [c // LINE for c in self.frame_starts]
        return [b - a for a, b in zip(s, s[1:])]


def read_symbols(path):
    """Labels of a dasm -s file: name -> address."""
    out = {}
    for line in open(path):
        parts = line.split()
        if len(parts) >= 2 and not line.startswith("---"):
            try:
                out[parts[0]] = int(parts[1], 16)
            except ValueError:
                pass
    return out
