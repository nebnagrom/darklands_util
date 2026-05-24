#!/usr/bin/env python3
"""
alchemy_profit.py — ranks alchemical formulae by expected profit per party member.

Reads a DKSAVE*.SAV file and DARKLAND.LST to determine which formulae each
character knows, then ranks each known formula using:

    success_rate = min(0.99, max(0, (100 − (magic_number − total)) / 100))
    expected_profit = success_rate × potion_value − comp_value

where total = alchemy_skill + intelligence + philosopher_stone_quality.

Usage:
    python alchemy_profit.py [save_file] [game_dir] [csv_file]

Defaults (relative to this script):
    save_file  DARKLAND/SAVES/DKSAVE0.SAV
    game_dir   DARKLAND                      (contains DARKLAND.LST)
    csv_file   src/main/resources/darklands_alchemy.csv
"""

import sys
import os
import csv
from struct import unpack

# ── Save file offsets (from dksaveXX.sav.xml) ──────────────────────────────────
PSTONE_OFF        = 0x92   # word: philosopher's stone quality
PARTY_INDICES_OFF = 0xF3   # 5 words: indices of active party members (0xffff = empty)
NUM_CHARS_OFF     = 0xF1   # word: total number of characters defined
CHARS_OFF         = 0x189  # start of character array
CHAR_SIZE         = 554    # 0x22A bytes per character

# Per-character relative offsets
CHR_NAME_OFF   = 0x25  # 25-byte null-terminated full name
CHR_ATTRS_OFF  = 0x5D  # 7-byte attribute_set: end str agl per INT chr df
CHR_SKILLS_OFF = 0x6B  # 19-byte skill_set: wEdg wImp wFll wPol wThr wBow wMsl ALCH ...
CHR_FORMS_OFF  = 0x94  # 22-byte formulae_known (one byte per formula type, bits for q25/q35/q45)

INT_ATTR_IDX   = 4   # intelligence = attr[4]  (end=0 str=1 agl=2 per=3 int=4 chr=5 df=6)
ALCH_SKILL_IDX = 7   # alchemy = skill[7]

# DARKLAND.LST item record is 46 bytes:
# name(20) + short_name(10) + type(2) + flags(5) + weight(1) + quality(1) +
# rarity(1) + unknown1(2) + unknown2(2) + value(2)
LST_ITEM_SIZE = 46

# formulae_known byte bits for each quality tier.
# 66 LST formula entries = 22 types × 3 qualities; formulae_known[type_i] covers
# LST indices [type_i*3, type_i*3+1, type_i*3+2] for q25, q35, q45.
Q_TIERS = [(25, 0x01, 0), (35, 0x02, 1), (45, 0x04, 2)]

# The 22 formula types in DARKLAND.LST order (verified against reader_lst.py output).
# Multiple alchemists share the same abbreviation across types at the same quality tier
# (e.g. "aR" = al-Razi for both Noxious Aroma q25 AND Fleadust q25), so CSV matching
# must key on formula base name, not alchemist prefix.
FORMULA_TYPES = [
    "Noxious Aroma",    # 0
    "Eyeburn",          # 1
    "Black Cloud",      # 2
    "Fleadust",         # 3
    "Eater Water",      # 4
    "Breath of Death",  # 5
    "Sunburst",         # 6
    "Thunderbolt",      # 7
    "Arabian Fire",     # 8
    "Stone-Tar",        # 9
    "Deadly Blade",     # 10
    "Strongedge",       # 11
    "Greatpower",       # 12
    "Trueflight",       # 13
    "Hardarmor",        # 14
    "Transformation",   # 15  (also yields +240pf florin per success)
    "Truesight",        # 16
    "New-wind",         # 17
    "Ironarm",          # 18
    "Quickmove",        # 19
    "Essence of Grace", # 20
    "Firewall",         # 21
]

TRANSFORMATION_BONUS_PF = 240  # 1 florin per successful Transformation brew


# ── DARKLAND.LST parsing ───────────────────────────────────────────────────────

def _read_cstring(data, pos):
    end = pos
    while end < len(data) and data[end] != 0:
        end += 1
    return data[pos:end].decode('ascii', errors='replace'), end + 1


def load_formula_table(game_dir):
    """
    Returns a list of 66 dicts {name, short_name, prefix} in LST order.
    prefix = first word of short_name (e.g. "aR", "Sol", "MS") — matches CSV.
    """
    path = os.path.join(game_dir, 'DARKLAND.LST')
    with open(path, 'rb') as fh:
        data = fh.read()

    item_cnt, saint_cnt, form_cnt = data[0], data[1], data[2]
    pos = 3
    pos += item_cnt * LST_ITEM_SIZE

    for _ in range(saint_cnt):    # skip saint full names
        _, pos = _read_cstring(data, pos)
    for _ in range(saint_cnt):    # skip saint short names
        _, pos = _read_cstring(data, pos)

    full_names = []
    for _ in range(form_cnt):
        name, pos = _read_cstring(data, pos)
        full_names.append(name)

    short_names = []
    for _ in range(form_cnt):
        sname, pos = _read_cstring(data, pos)
        short_names.append(sname)

    table = []
    for full, short in zip(full_names, short_names):
        prefix = short.split()[0] if short.split() else short
        table.append({'name': full, 'short_name': short, 'prefix': prefix})
    return table


# ── Alchemy CSV parsing ────────────────────────────────────────────────────────

def load_alchemy_csv(csv_path):
    """
    Returns a dict keyed by (short_prefix_lower, quality_int).
    prefix = first word of the CSV name column (e.g. "aR", "Sol", "Mam").
    """
    potions = {}
    with open(csv_path, newline='', encoding='utf-8') as fh:
        for row in csv.DictReader(fh):
            raw = row['name'].strip()
            parts = raw.split(' ', 1)
            if len(parts) < 2:
                continue
            base_name = parts[1].strip()
            quality   = int(row['quality'])
            potions[(base_name.lower(), quality)] = {
                'display': raw,
                'quality': quality,
                'magic':   int(row['magic number']),
                'pval':    int(row['potion value']),
                'cval':    int(row['comp value']),
                'risk':    row['risk'].strip(),
            }
    return potions


# ── Save file parsing ──────────────────────────────────────────────────────────

def parse_characters(data):
    party_indices = set(
        unpack('<H', data[PARTY_INDICES_OFF + i*2: PARTY_INDICES_OFF + i*2 + 2])[0]
        for i in range(5)
    ) - {0xFFFF}

    num  = unpack('<H', data[NUM_CHARS_OFF:NUM_CHARS_OFF + 2])[0]
    chars = []
    for i in range(num):
        if i not in party_indices:
            continue
        base = CHARS_OFF + i * CHAR_SIZE

        name_raw = data[base + CHR_NAME_OFF: base + CHR_NAME_OFF + 25]
        null_at  = name_raw.find(0)
        name     = (name_raw[:null_at] if null_at >= 0 else name_raw).decode('ascii', errors='replace')

        chars.append({
            'name':          name.strip() or f'Character {i}',
            'intelligence':  data[base + CHR_ATTRS_OFF  + INT_ATTR_IDX],
            'alchemy':       data[base + CHR_SKILLS_OFF + ALCH_SKILL_IDX],
            'forms_raw':     bytes(data[base + CHR_FORMS_OFF: base + CHR_FORMS_OFF + 22]),
        })
    return chars


# ── Profit calculation ─────────────────────────────────────────────────────────

def expected_profit(total, magic, pval, cval):
    sr = min(0.99, max(0.0, (100 - (magic - total)) / 100))
    return sr, sr * pval - cval


# ── Reporting ─────────────────────────────────────────────────────────────────

RULE = '─' * 74

def report_character(char, pstone, formula_table, potions):
    alch  = char['alchemy']
    intel = char['intelligence']
    total = alch + intel + pstone

    print(RULE)
    print(f"  {char['name']}   Alch={alch}  Int={intel}  PSt={pstone}  total={total}")
    print(RULE)

    brewable, impossible, unmatched = [], [], []

    for type_i, fbyte in enumerate(char['forms_raw']):
        if type_i * 3 + 2 >= len(formula_table):
            break
        for quality, bit, q_offset in Q_TIERS:
            if not (fbyte & bit):
                continue
            lst_idx  = type_i * 3 + q_offset
            entry    = formula_table[lst_idx]
            key      = (FORMULA_TYPES[type_i].lower(), quality)
            if key not in potions:
                unmatched.append(f"{entry['name']} (q{quality})")
                continue
            p        = potions[key]
            pval_eff = p['pval'] + (TRANSFORMATION_BONUS_PF if type_i == 15 else 0)
            sr, ep   = expected_profit(total, p['magic'], pval_eff, p['cval'])
            bucket = brewable if sr > 0 else impossible
            bucket.append((ep, sr, p, pval_eff))

    if not brewable and not impossible and not unmatched:
        print("  (no formulae known)")
        print()
        return

    brewable.sort(key=lambda x: -x[0])
    impossible.sort(key=lambda x: x[2]['magic'])

    print(f"  {'Potion':<34} {'Q':>3}  {'Mag#':>4}  {'Succ%':>5}  {'Raw':>7}  {'Exp/att':>8}  Risk")
    print()

    for ep, sr, p, pval_eff in brewable:
        raw = pval_eff - p['cval']
        print(f"  {p['display']:<34} {p['quality']:>3}  {p['magic']:>4}  "
              f"{sr*100:>4.0f}%  {raw:>+7}pf  {ep:>+8.0f}pf  {p['risk']}")

    if impossible:
        print(f"\n  ── IMPOSSIBLE (need total ≥ {impossible[0][2]['magic']}) ──")
        for _, _, p, pval_eff in impossible:
            raw = pval_eff - p['cval']
            print(f"  {p['display']:<34} {p['quality']:>3}  {p['magic']:>4}  "
                  f"  ---   {raw:>+7}pf              {p['risk']}")

    if unmatched:
        print(f"\n  [warning] in save but not in CSV: {', '.join(unmatched)}")

    print()


def main():
    here     = os.path.dirname(os.path.abspath(__file__))
    sav_path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(here, 'DARKLAND', 'SAVES', 'DKSAVE0.SAV')
    game_dir = sys.argv[2] if len(sys.argv) > 2 else os.path.join(here, 'DARKLAND')
    csv_path = sys.argv[3] if len(sys.argv) > 3 else os.path.join(here, 'src', 'main', 'resources', 'darklands_alchemy.csv')

    with open(sav_path, 'rb') as fh:
        data = fh.read()

    pstone        = unpack('<H', data[PSTONE_OFF: PSTONE_OFF + 2])[0]
    formula_table = load_formula_table(game_dir)
    potions       = load_alchemy_csv(csv_path)
    characters    = parse_characters(data)

    print(f"Save:  {os.path.basename(sav_path)}")
    print(f"Stone: {pstone}   Formulae in LST: {len(formula_table)}   Types: {len(formula_table)//3}")
    print()

    shown = 0
    for char in characters:
        if char['alchemy'] == 0:
            continue
        report_character(char, pstone, formula_table, potions)
        shown += 1

    if shown == 0:
        print("No characters with alchemy skill found.")


if __name__ == '__main__':
    main()
