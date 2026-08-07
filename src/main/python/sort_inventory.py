#!/usr/bin/env python3
"""
sort_inventory.py — Sort each character's inventory in a Darklands save file.

Sort order within the sortable zone:
  1. Arrows / quarrels          (ammo)
  2. Javelins / thrown weapons
  3. Equipped items             (alpha by name, then quality desc)
  4. Alchemy ingredients        (alpha, quality desc)
  5. Potions                    (alpha, quality desc)
  6. Armor & shields            (alpha, quality desc)
  7. Weapons                    (alpha, quality desc)
  8. Misc                       (alpha, quality desc)

Divider rule: the first zero-cost nonmetal-armor item (clothing) acts as a
section marker. Items that appear BEFORE it in the current inventory are left
in place; everything from the divider onwards is sorted.

Usage:
    python sort_inventory.py <save_file> --lst <darklands_dir> [--dry-run] [--backup]

Example:
    python sort_inventory.py "C:/Games/Darklands/SAVES/DKSAVE0.SAV" --lst "C:/Games/Darklands"
"""
import sys
import struct
import shutil
import argparse
from pathlib import Path

from read_lst import read_lst, GRP_EQUIPPED

# ── Save-file layout ─────────────────────────────────────────────────────────

# Offset of first character record in the save file (derived from format_sav.py)
CHARS_START = 393
CHAR_SIZE   = 554   # bytes per character record

# Offsets *within* a character record (from dksaveXX.sav.xml)
OFF_FULL_NAME          = 0x25
OFF_EQUIP_MISSILE_TYPE = 0x22
OFF_EQUIP_VITAL_TYPE   = 0x4b
OFF_EQUIP_LEG_TYPE     = 0x4c
OFF_EQUIP_VITAL_Q      = 0x4f
OFF_EQUIP_LEG_Q        = 0x50
OFF_EQUIP_WEAPON_TYPE  = 0x51
OFF_EQUIP_WEAPON_Q     = 0x58
OFF_EQUIP_MISSILE_Q    = 0x5a
OFF_EQUIP_SHIELD_Q     = 0x5b
OFF_EQUIP_SHIELD_TYPE  = 0x5c
OFF_NUM_ITEMS          = 0x7e
OFF_ITEMS              = 0xaa   # 64 × 6-byte item records

ITEM_SIZE = 6
MAX_ITEMS = 64

# Offset of num_characters in the save-file header
OFF_NUM_CHARS = 241


# ── Item record helpers ───────────────────────────────────────────────────────

def _read_item(buf, offset):
    code, itype, quality, quantity, weight = struct.unpack_from('<HBBBB', buf, offset)
    return dict(code=code, itype=itype, quality=quality,
                quantity=quantity, weight=weight)


def _write_item(buf, offset, item):
    struct.pack_into('<HBBBB', buf, offset,
                    item['code'], item['itype'], item['quality'],
                    item['quantity'], item['weight'])


# ── Character helpers ─────────────────────────────────────────────────────────

def _char_name(buf, base):
    raw = buf[base + OFF_FULL_NAME: base + OFF_FULL_NAME + 25]
    end = raw.find(0)
    return raw[:end].decode('ascii', errors='replace') if end != -1 else raw.decode('ascii', errors='replace')


def _equipped_pairs(buf, base):
    """Return the set of (itype, quality) pairs for all equipped slots."""
    slots = (
        (OFF_EQUIP_WEAPON_TYPE,  OFF_EQUIP_WEAPON_Q),
        (OFF_EQUIP_VITAL_TYPE,   OFF_EQUIP_VITAL_Q),
        (OFF_EQUIP_LEG_TYPE,     OFF_EQUIP_LEG_Q),
        (OFF_EQUIP_SHIELD_TYPE,  OFF_EQUIP_SHIELD_Q),
        (OFF_EQUIP_MISSILE_TYPE, OFF_EQUIP_MISSILE_Q),
    )
    pairs = set()
    for t_off, q_off in slots:
        t = buf[base + t_off]
        q = buf[base + q_off]
        if t != 0 or q != 0:
            pairs.add((t, q))
    return pairs


def _sort_key(item, defs, equipped):
    defn = defs[item['code']] if item['code'] < len(defs) else None
    name = defn.name.lower() if defn else ''

    if defn is None:
        from read_lst import GRP_MISC
        group = GRP_MISC
    elif (item['itype'], item['quality']) in equipped:
        group = GRP_EQUIPPED
    else:
        group = defn.sort_group()

    return (group, name, -item['quality'])


# ── Per-character sort ────────────────────────────────────────────────────────

def sort_character(buf, char_idx, defs, dry_run=False):
    base      = CHARS_START + char_idx * CHAR_SIZE
    num_items = struct.unpack_from('<H', buf, base + OFF_NUM_ITEMS)[0]
    if num_items == 0:
        return None

    items_base = base + OFF_ITEMS
    items = [_read_item(buf, items_base + i * ITEM_SIZE) for i in range(num_items)]

    # Find the clothing divider (first zero-cost nonmetal-armor)
    divider = next(
        (i for i, it in enumerate(items)
         if it['code'] < len(defs) and defs[it['code']].is_clothing_divider()),
        None
    )

    fixed    = items[:divider] if divider is not None else []
    sortable = items[divider:] if divider is not None else items

    if not sortable:
        return fixed, [], []

    equipped = _equipped_pairs(buf, base)
    sorted_items = sorted(sortable, key=lambda it: _sort_key(it, defs, equipped))

    if not dry_run:
        for i, item in enumerate(fixed + sorted_items):
            _write_item(buf, items_base + i * ITEM_SIZE, item)

    return fixed, sortable, sorted_items


# ── Main ──────────────────────────────────────────────────────────────────────

def _item_label(item, defs):
    defn = defs[item['code']] if item['code'] < len(defs) else None
    name = defn.name if defn else f'#code{item["code"]}'
    return f'{name:<26}  q={item["quality"]:3d}  x{item["quantity"]}'


def main():
    ap = argparse.ArgumentParser(
        description='Sort Darklands character inventories by type, name, and quality.'
    )
    ap.add_argument('save_file',
                    help='Path to a DKSAVE*.SAV file')
    ap.add_argument('--lst', metavar='DIR', required=True,
                    help='Darklands install directory containing DARKLAND.LST')
    ap.add_argument('--dry-run', action='store_true',
                    help='Show proposed order without writing anything')
    ap.add_argument('--backup', action='store_true',
                    help='Save a .bak copy before modifying')
    args = ap.parse_args()

    save_path = Path(args.save_file)
    if not save_path.exists():
        sys.exit(f'Save file not found: {save_path}')

    defs = read_lst(args.lst)
    buf  = bytearray(save_path.read_bytes())

    num_chars = struct.unpack_from('<H', buf, OFF_NUM_CHARS)[0]
    print(f'{save_path.name}  —  {num_chars} character(s)\n')

    for c in range(num_chars):
        base      = CHARS_START + c * CHAR_SIZE
        num_items = struct.unpack_from('<H', buf, base + OFF_NUM_ITEMS)[0]
        name      = _char_name(buf, base)
        print(f'  [{c}] {name}  ({num_items} items)')

        result = sort_character(buf, c, defs, dry_run=args.dry_run)
        if result is None:
            print('      (empty)\n')
            continue

        fixed, sortable, sorted_items = result
        if fixed:
            print(f'      {len(fixed)} item(s) before divider — not moved:')
            for it in fixed:
                print(f'        {_item_label(it, defs)}')
        if sortable:
            print(f'      {len(sortable)} item(s) sorted:')
            for it in sorted_items:
                print(f'        {_item_label(it, defs)}')
        print()

    if args.dry_run:
        print('(dry run — no changes written)')
        return

    if args.backup:
        bak = save_path.with_suffix('.bak')
        shutil.copy2(save_path, bak)
        print(f'Backup → {bak.name}')

    save_path.write_bytes(buf)
    print(f'Saved  → {save_path.name}')


if __name__ == '__main__':
    main()
