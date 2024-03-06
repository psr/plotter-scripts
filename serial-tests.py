#!/usr/bin/env python3

import termios
import os
import io
import unicodedata
import curses.ascii

serial = open('/dev/ttyUSB0', 'r+b', buffering=0)
assert serial.isatty()
# Set non-blocking
assert os.get_blocking(serial.fileno()), "Serial device was already non-blocking"
os.set_blocking(serial.fileno(), False)
(iflag, oflag, cflag, lflag, ispeed, ospeed, cc) = termios.tcgetattr(serial)

def print_flags(flags, constants, masks={}):
    for flag in constants:
        mask = getattr(termios, flag, 0)
        if not (values := masks.get(flag)):
            print(f"{flag:>10}: {mask & flags != 0}")
            continue
        for value in values:
            if getattr(termios, value) == flags & mask:
                print(f"{flag:>10}: {value}")
    print()

iflag_constants = [
    "IGNBRK",
    "BRKINT",
    "IGNPAR",
    "PARMRK",
    "INPCK",
    "ISTRIP",
    "INLCR",
    "IGNCR",
    "ICRNL",
    "IUCLC",
    "IXON",
    "IXANY",
    "IXOFF",
    "IMAXBEL",
    "IUTF8",
]

print("Input flags")
print_flags(iflag, iflag_constants)


oflag_constants = [
    "OPOST",
    "OLCUC",
    "ONLCR",
    "OCRNL",
    "ONOCR",
    "ONLRET",
    "OFILL",
    "OFDEL",
    "NLDLY",  # The following are masks for multi-bit patterns
    "CRDLY",
    "TABDLY",
    "BSDLY",
    "VTDLY",
    "FFDLY",
]


oflag_masks = {
    "NLDLY": ["NL0", "NL1"],
    "CRDLY": ["CR0", "CR1", "CR2", "CR3"],
    "TABDLY": ["TAB0", "TAB1", "TAB2", "XTABS"],
    "BSDLY": ["BS0", "BS1"],
    "VTDLY": ["VT0", "VT1"],
    "FFDLY": ["FF0", "FF1"],
}


print("Output flags")
print_flags(oflag, oflag_constants, oflag_masks)

cflag_constants = [
    # "CBAUD",  # Storage for Baud rate I think
    # "CBAUDEX",
    "CSIZE",
    "CSTOPB",
    "CREAD",
    "PARENB",
    "PARODD",
    "HUPCL",
    "CLOCAL",
    "LOBLK",
    # "CIBAUD",  # Storage for output baud rate
    "CMSPAR",
    "CRTSCTS",
]

print("Control flags")
print_flags(cflag, cflag_constants)


lflag_constants = [
    "ISIG",
    "ICANON",
    "XCASE", 
    "ECHO",
    "ECHOE",
    "ECHOK",
    "ECHONL",
    "ECHOCTL",
    "ECHOPRT",
    "ECHOKE",
    "DEFECHO",
    "FLUSHO",
    "NOFLSH",
    "TOSTOP",
    "PENDIN",
    "IEXTEN",
]


print("Local flags")
print_flags(lflag, lflag_constants)

baud_rates = [
    0,
    50,
    75,
    110,
    134,
    150,
    200,
    300,
    600,
    1200,
    1800,
    2400,
    4800,
    9600,
    19200,
    38400,
    57600,
    115200,
    230400,
]

def print_baudrate(speed):
    print(f"{baud_rates[speed]:,} baud")

print("Input speed: ", end='')
print_baudrate(ispeed)

print("Output speed: ", end='')
print_baudrate(ospeed)
print()

special_character_names = [
    "VDISCARD",
    # "VDSUSP",  # Not in POSIX, AND not supported on Linux. Why it is in the man page I do not know.
    "VEOF",
    "VEOL",
    "VEOL2",
    "VERASE",
    "VINTR",
    "VKILL",
    "VLNEXT",
    "VMIN",
    "VQUIT",
    "VREPRINT",
    "VSTART",
    # "VSTATUS",  # Same
    "VSTOP",
    "VSUSP",
    "VSWTCH",
    "VTIME",
    "VWERASE",
]

special_character_indexes = {n: i for i, n in sorted((getattr(termios, n), n) for n in special_character_names)}

def char_name(c):
    try:
        return unicodedata.name(c)
    except ValueError:
        pass
    try:
        return curses.ascii.controlnames[ord(s)]
    except IndexError:
        if ord(s) == curses.ascii.DEL:
            return "DEL"
        raise

print("Special Characters")
for name, i in special_character_indexes.items():
    if name in {"VMIN", "VTIME"}:
        continue
    char = cc[i]
    s = char.decode('ascii')
    print(f"{name:>10}: {curses.ascii.unctrl(s):>3} {char_name(s)}")
print()
for name in ["VMIN", "VTIME"]:
    index = getattr(termios, name)
    value = cc[index]
    # For some reason the Python termios module interprets these differently
    # depending on whether canonical mode is on (I think).
    # Try to ignore that.
    if isinstance(value, bytes):
        assert len(value) == 1
        value = value[0]
    print(f"{name:>10}: {value:>3}")

