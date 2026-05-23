#!/usr/bin/env python3
"""
organise_saves.py — Sort Darklands save slots by in-game date.

Usage:
    python organise_saves.py <saves_dir> [--dry-run]

Reads all DKSAVE*.SAV files in the given directory, sorts them by
in-game date ascending, and renames them so slot 0 is the oldest
save and the highest slot is the newest.

A two-pass rename (via temp names) avoids collisions when slots swap.
"""
import sys
import re
import argparse
from pathlib import Path

from format_sav import read_file

SAVE_RE = re.compile(r'^DKSAVE\d+\.SAV$', re.IGNORECASE)


def find_saves(saves_dir):
    saves = []
    for entry in Path(saves_dir).iterdir():
        if not SAVE_RE.match(entry.name):
            continue
        try:
            saves.append(read_file(entry))
        except Exception as exc:
            print(f'  Warning: skipping {entry.name}: {exc}', file=sys.stderr)
    return saves


def organise(saves_dir, dry_run=False):
    saves = find_saves(saves_dir)
    if not saves:
        sys.exit('No DKSAVE*.SAV files found in the given directory.')

    saves.sort(key=lambda s: s.curr_date)

    root = Path(saves_dir)
    print(f'Found {len(saves)} save(s), ordered by in-game date:\n')
    for i, save in enumerate(saves):
        new_name = f'DKSAVE{i}.SAV'
        arrow = '(unchanged)' if Path(save.path).name.upper() == new_name.upper() else f'-> {new_name}'
        print(f'  {i}: {save.curr_date:%Y-%m-%d}  {save.save_game_label:<24}  {Path(save.path).name}  {arrow}')

    if dry_run:
        print('\n(dry run — no files changed)')
        return

    print()
    # Pass 1: rename everything to temp names to avoid slot-swap collisions
    tmp_paths = []
    for i, save in enumerate(saves):
        tmp = root / f'_DKTMP{i}.SAV'
        Path(save.path).rename(tmp)
        tmp_paths.append(tmp)

    # Pass 2: rename temps to final slot names
    for i, tmp in enumerate(tmp_paths):
        final = root / f'DKSAVE{i}.SAV'
        tmp.rename(final)
        print(f'  Renamed -> {final.name}')

    print(f'\nDone. {len(saves)} file(s) reorganised.')


def main():
    parser = argparse.ArgumentParser(
        description='Sort Darklands save slots by in-game date (oldest = slot 0).'
    )
    parser.add_argument('saves_dir', help='Path to the Darklands SAVES directory')
    parser.add_argument('--dry-run', action='store_true',
                        help='Print the proposed order without renaming anything')
    args = parser.parse_args()
    organise(args.saves_dir, dry_run=args.dry_run)


if __name__ == '__main__':
    main()
