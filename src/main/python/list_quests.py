#!/usr/bin/env python3
"""
list_quests.py — List pending quests from a Darklands save file.

Ports the logic from DARKLAND/dlq_src/DlqDump.cpp (Michael Petzold, 2000).

Usage:
    python list_quests.py <save_file> --lst <darklands_dir>
    python list_quests.py --latest --lst <darklands_dir>

Example:
    python list_quests.py SAVES/DKSAVE0.SAV --lst "C:/Games/Darklands"
"""
import sys
import math
import struct
import argparse
from pathlib import Path

from read_lst import read_lst


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
    return p


def _resolve_lst_dir(path):
    """Return the directory containing DARKLAND.LST.

    Checks the given path first, then its parent — so running from SAVES/
    still finds the LST file one level up.
    """
    p = Path(path).resolve()  # resolve() needed so Path('.').parent works correctly
    if (p / 'DARKLAND.LST').exists():
        return p
    parent = p.parent
    if (parent / 'DARKLAND.LST').exists():
        return parent
    return p  # fall through; read_lst will raise a clear error

# ── Save-file layout ──────────────────────────────────────────────────────────

QUEST_SZ    = 48   # bytes per quest record (24 signed shorts)
LOC_SZ      = 58   # bytes per location record
LOC_NAME_SZ = 20   # name field within location record
CHAR_SZ     = 554  # bytes per character record
CHARS_START = 393  # offset of first character record

OFF_YEAR      = 104  # game date fields (each a little-endian short)
OFF_NUM_CHARS = 241  # number of characters (little-endian short)

MAX_LOC    = 420
CITY_COUNT = 92    # first 92 location indices are cities

# Employer type labels indexed by quest[13]
WHO = [
    "Merchant", "#1", "#2", "#3",
    "Foreign Trader", "Pharmacist", "Medici",
    "Hanseatic League", "Fugger", "Schulz", "Mayor",
    "#11",
]

NSEW = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]  # indexed 0-7


# ── String helpers ────────────────────────────────────────────────────────────

def _decode(raw):
    """Null-terminate and decode, mapping Darklands umlaut bytes to Unicode."""
    end = raw.find(0)
    if end != -1:
        raw = raw[:end]
    # Darklands uses 0x7b for ö and 0x7c for ü (neither CP437 nor latin-1)
    raw = bytes(0xf6 if b == 0x7b else (0xfc if b == 0x7c else b) for b in raw)
    return raw.decode('latin-1')


# ── Location helpers ──────────────────────────────────────────────────────────

def _loc_name(loc_buf, idx):
    if idx < 0 or idx >= len(loc_buf):
        return '<invalid index>'
    return _decode(loc_buf[idx][38:38 + LOC_NAME_SZ])


def _loc_coords(loc_buf, idx):
    x = struct.unpack_from('<h', loc_buf[idx], 4)[0]
    y = struct.unpack_from('<h', loc_buf[idx], 6)[0]
    return x, y


def _compass(site_x, site_y, city_x, city_y):
    dx = float(abs(site_x - city_x))
    dy = float(abs(site_y - city_y))
    if dx == 0.0:
        dx = 0.0001
    angle = math.atan2(dy, dx)
    if angle < math.pi / 8:
        return 2 if site_x > city_x else 6          # E or W
    elif angle < math.pi * 3 / 8:
        if site_x > city_x:
            return 1 if site_y < city_y else 3      # NE or SE
        else:
            return 5 if site_y > city_y else 7      # SW or NW
    else:
        return 0 if site_y < city_y else 4          # N or S


def _closest_city(loc_buf, idx, exclude):
    """Return (city_index, compass_dir) of the closest city to loc_buf[idx]."""
    sx, sy = _loc_coords(loc_buf, idx)
    best_dist = float('inf')
    best_i = -1
    best_cx, best_cy = 0, 0
    for i in range(min(CITY_COUNT, len(loc_buf))):
        if i == exclude:
            continue
        cx, cy = _loc_coords(loc_buf, i)
        d = math.hypot(cx - sx, cy - sy)
        if d < best_dist:
            best_dist = d
            best_i = i
            best_cx, best_cy = cx, cy
    return best_i, _compass(sx, sy, best_cx, best_cy)


# ── Quest parsing ─────────────────────────────────────────────────────────────

def list_quests(save_path, darklands_dir):
    buf = bytearray(Path(save_path).read_bytes())
    item_defs = read_lst(darklands_dir)

    year  = struct.unpack_from('<H', buf, OFF_YEAR)[0]
    month = struct.unpack_from('<H', buf, OFF_YEAR + 2)[0] + 1
    day   = struct.unpack_from('<H', buf, OFF_YEAR + 4)[0]
    hour  = struct.unpack_from('<H', buf, OFF_YEAR + 6)[0]

    num_chars = struct.unpack_from('<H', buf, OFF_NUM_CHARS)[0]

    quest_num_off  = CHARS_START + num_chars * CHAR_SZ
    num_quests     = struct.unpack_from('<h', buf, quest_num_off)[0]
    first_quest_off = quest_num_off + 2

    loc_num_off = first_quest_off + num_quests * QUEST_SZ
    num_loc     = min(struct.unpack_from('<h', buf, loc_num_off)[0], MAX_LOC)
    loc_start   = loc_num_off + 2
    loc_buf     = [
        bytes(buf[loc_start + i * LOC_SZ: loc_start + (i + 1) * LOC_SZ])
        for i in range(num_loc)
    ]

    t1 = _decode(buf[0:21])
    t2 = _decode(buf[21:101])
    save_name = Path(save_path).name
    print(f"Quests for {save_name}: {t1} {t2} {year}/{month:02d}/{day:02d} hour {hour}")
    print()

    pending = 0
    for i in range(num_quests):
        q = list(struct.unpack_from('<24h', buf, first_quest_off + i * QUEST_SZ))

        start_d, start_m, start_y  = q[6], q[7], q[8]
        dl_d,    dl_m,    dl_y     = q[10], q[11], q[12]
        employer  = q[13]
        dest_idx  = q[14]
        repo_idx  = q[15]
        item_idx  = q[23]

        # Pending filter (from dumpit() in DlqDump.cpp)
        if employer < 0 or dl_y == start_y:
            continue
        # q17==8 + q21!=0 + q22==2 marks an active Raubritter quest;
        # q17==36 is a delivery-phase variant DlqDump didn't handle — show it too.
        if not (q[17] == 8 and q[21] != 0 and q[22] == 2) and q[17] != 36:
            if item_idx == 0:
                continue

        pending += 1
        who = WHO[employer] if 0 <= employer < len(WHO) else f'#{employer}'

        # --- Line 1 ---
        parts = [f"{pending:3d}: "]
        if item_idx != 0:
            iname = item_defs[item_idx].name if item_idx < len(item_defs) else f'#item{item_idx}'
            if dl_y == 1499:
                parts.append(f"Get {iname} from ")
            else:
                parts.append(f"Return {iname} to {who} at ")
        else:
            parts.append("Raubritter Quest - go to - ")

        parts.append(f"{_loc_name(loc_buf, dest_idx)} ")

        if dest_idx > 91:
            c1, dir1 = _closest_city(loc_buf, dest_idx, -1)
            c2, dir2 = _closest_city(loc_buf, dest_idx, c1)
            parts.append(f"({NSEW[dir1]} of {_loc_name(loc_buf, c1)}, "
                         f"{NSEW[dir2]} of {_loc_name(loc_buf, c2)}) ")

        if dl_y > 1498:
            parts.append(f"[from {start_y:4d}/{start_m + 1:02d}/{start_d:02d}]")
        else:
            parts.append(f"by {dl_y:4d}/{dl_m + 1:02d}/{dl_d:02d}")

        print(''.join(parts))

        # --- Line 2 (only for some quest types) ---
        repo_name = _loc_name(loc_buf, repo_idx)
        if item_idx != 0:
            if dl_y == 1499:
                print(f"     Deliver to {who} at {repo_name}")
        else:
            print(f"     Report to {who} at {repo_name}")

        print()

    if pending == 0:
        print("No pending quests found.")

    return pending


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(
        description='List pending quests from a Darklands save file.'
    )
    ap.add_argument('save_file', nargs='?',
                    help='Path to a DKSAVE*.SAV (omit to use most recent in ./SAVES/)')
    ap.add_argument('--lst', metavar='DIR', default='.',
                    help='Darklands install directory containing DARKLAND.LST (default: current dir)')
    args = ap.parse_args()

    if args.save_file:
        save_path = Path(args.save_file)
    else:
        saves_dir = _resolve_saves_dir('.')
        saves = sorted(saves_dir.glob('DKSAVE*.SAV'),
                       key=lambda p: p.stat().st_mtime, reverse=True)
        if not saves:
            sys.exit('No DKSAVE*.SAV found in . or ./SAVES/')
        save_path = saves[0]
        print(f'Using most recent save: {save_path.name}')

    if not save_path.exists():
        sys.exit(f'Save file not found: {save_path}')

    list_quests(save_path, _resolve_lst_dir(args.lst))


if __name__ == '__main__':
    main()
