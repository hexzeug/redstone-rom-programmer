import argparse
import sys
from yaml import load, Loader

def parse_args():
    parser = argparse.ArgumentParser(description="Redstone ROM Programmer: Convert .hex to .schem")
    parser.add_argument("--layout", default="rom.yml", help="YAML file containing the ROM layout [defaults to rom.yml]")
    return parser.parse_args()

def open_file(rom_layout_file):
    try:
        file = open(rom_layout_file)
    except FileNotFoundError:
        print(f"Error: {rom_layout_file} does not exist.", file=sys.stderr)
    except PermissionError:
        print(f"Error: {rom_layout_file} is not readable", file=sys.stderr)
    except OSError as e:
        print(f"Error: Failed opening {rom_layout_file}, {e}", file=sys.stderr)
    else:
        return file
    raise SystemExit(1)

def main() -> int:
    args = parse_args()
    print(load(open_file(args.layout), Loader=Loader))
    return 0