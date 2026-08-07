#!/usr/bin/env python3
"""
highest_save_number.py — Find the highest number embedded in Darklands save labels.

Scans all DKSAVE*.SAV files in a directory, reads each save's in-game label,
extracts every run of digits (e.g. "run234b" yields 234), and reports the max.

Usage:
    python highest_save_number.py [saves_dir]

Accepts either the Darklands install directory or its SAVES subdirectory.
"""
import re
import sys
from pathlib import Path

from format_sav import read_file

SAVE_RE = re.compile(r'^DKSAVE\d+\.SAV$', re.IGNORECASE)
NUM_RE  = re.compile(r'\d+')


def _resolve_saves_dir(path):
    """Return the directory that actually contains DKSAVE*.SAV files.

    Accepts the install root (DARKLAND/) or the saves subdir (DARKLAND/SAVES/).
    """
    p = Path(path)
    if any(p.glob('DKSAVE*.SAV')):
        return p
    sub = p / 'SAVES'
    if sub.is_dir() and any(sub.glob('DKSAVE*.SAV')):
        return sub
    return p  # fall through; let the caller surface a useful error


def main():
    root = sys.argv[1] if len(sys.argv) > 1 else '.'
    saves_dir = _resolve_saves_dir(root)
    if not saves_dir.is_dir():
        sys.exit(f'Not a directory: {saves_dir}')

    rows = []
    for path in sorted(saves_dir.iterdir()):
        if not SAVE_RE.match(path.name):
            continue
        try:
            save = read_file(path)
            nums = [int(m) for m in NUM_RE.findall(save.save_game_label)]
            rows.append((path.name, save.save_game_label, save.curr_coords, nums))
        except Exception as exc:
            print(f'Warning: skipping {path.name}: {exc}', file=sys.stderr)

    if not rows:
        sys.exit('No DKSAVE*.SAV files found.')

    all_nums = [n for _, _, _, nums in rows for n in nums]
    highest = max(all_nums) if all_nums else None

    BOLD = '\033[1m'
    GREEN = '\033[32m'
    RESET = '\033[0m'

    print(f'{"File":<14}  {"Label":<26}  {"Coords":<14}  Numbers')
    print('-' * 72)
    for filename, label, coords, nums in rows:
        nums_str = ', '.join(str(n) for n in nums) or '-'
        coords_str = f'({coords[0]},{coords[1]})'
        if highest is not None and highest in nums:
            print(f'{GREEN}{BOLD}{filename:<14}  {label:<26}  {coords_str:<14}  {nums_str}{RESET}')
        else:
            print(f'{filename:<14}  {label:<26}  {coords_str:<14}  {nums_str}')

    print()
    if highest is not None:
        print(f'Highest: {GREEN}{BOLD}{highest}{RESET}')
    else:
        print('No numbers found in any save label.')


if __name__ == '__main__':
    main()