import argparse
import sys
from yaml import load, Loader

def parse_args():
    parser = argparse.ArgumentParser(description="Redstone ROM Programmer: Convert .hex to .schem")
    parser.add_argument("--layout", default="rom.yml", help="YAML file containing the ROM layout [defaults to rom.yml]")
    return parser.parse_args()

def open_file(filename):
    try:
        return open(filename)
    except FileNotFoundError:
        print(f"Error: {filename} does not exist.", file=sys.stderr)
    except PermissionError:
        print(f"Error: {filename} is not readable", file=sys.stderr)
    except OSError as e:
        print(f"Error: Failed opening {filename}, {e}", file=sys.stderr)
    raise SystemExit(1)

def parse_layout(rom_layout_file):
    with open_file(rom_layout_file) as f:
        try:
            layout = load(f, Loader=Loader)
        except Exception as e:
            print(f"Error: Failed to parse {rom_layout_file}, {e}", file=sys.stderr)
            raise SystemExit(1)
    layout.setdefault("base_address", 0)
    return layout

class RomLayout:
    DIRECTIONS = {"north": (0, -1), "south": (0, 1), "east": (1, 0), "west": (-1, 0)}
    OFFSETS = {(0, -1): "north", (0, 1): "south", (1, 0): "east", (-1, 0): "west"}

    def __init__(self, layout):
        self.base_address = layout["base_address"]
        self.bank_dir = self.DIRECTIONS[layout["bank"]["dir"]]
        self.bank_shift = layout["bank"]["shift"]
        self.bank_bitmask = layout["bank"]["bitmask"]
        self.bank_period = layout["bank"]["period"]
        self.shift_bit = layout["bank"]["shift_bit"]
        self.word_dir = self.DIRECTIONS[layout["word"]["dir"]]
        self.word_shift = layout["word"]["shift"]
        self.word_bitmask = layout["word"]["bitmask"]
        self.word_period = layout["word"]["period"]
        self.word_bytes = layout["word"]["bytes"]
        self.side_bit = layout["word"]["side_bit"]
        self.zero = layout["zero"]
        self.size = 2 ** (self.bank_bitmask.bit_count() + self.word_bitmask.bit_count() + 1)

    def _dir(self, value, dir):
        return (value * dir[0], value * dir[1])
    
    def _add(self, dir1, dir2):
        return (dir1[0] + dir2[0], dir1[1] + dir2[1])
    
    def word_at(self, address):
        if address < self.base_address:
            raise ValueError(f"Address {address} is below the base address {self.base_address}")
        offset = address - self.base_address
        if offset >= self.size:
            raise ValueError(f"Address {address} is out of bounds for the ROM size {self.size} at base address {self.base_address}")
        bank = (offset >> self.bank_shift) & self.bank_bitmask
        shift = (offset >> self.shift_bit) & 0x1
        side = (offset >> self.side_bit) & 0x1
        word = (offset >> self.word_shift) & self.word_bitmask
        bank_coord = bank * self.bank_period + side * 2
        word_coord = word * self.word_period - shift
        dir = self._dir(-2 * side + 1, self.bank_dir)
        coords1 = self._dir(bank_coord, self.bank_dir)
        coords2 = self._dir(word_coord, self.word_dir)
        return (self._add(coords1, coords2), self.OFFSETS[dir])

class RomProgrammer:
    def __init__(self, layout):
        self.layout = layout
    
    def write(self, address, value):
        try:
            coords, dir = self.layout.word_at(address)
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            raise SystemExit(1)
        print(f"Write {value} to {coords} facing {dir}")

def main() -> int:
    args = parse_args()
    layout = RomLayout(parse_layout(args.layout))
    programmer = RomProgrammer(layout)
    programmer.write(1023, 0xFF)
    return 0