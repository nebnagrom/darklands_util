# darklands_util

A collection of Python utilities and a Kotlin parser for the 1992 DOS RPG *Darklands* by MicroProse. The tools read the game's proprietary binary save files and data files for analysis, save management, and in-game decision support.

---

## Python Utilities

All scripts require Python 3 and no third-party packages. Game files must be in a `DARKLAND/` directory (or passed explicitly). Scripts in `src/main/python/` import each other, so run them from that directory.

### `alchemy_profit.py` — Alchemy profit ranker
**Run from project root.**

Reads your current save file and `DARKLAND.LST` to find which alchemical formulae each party member knows, then ranks them by expected profit per attempt using each character's alchemy skill + intelligence + philosopher's stone quality.

```
python alchemy_profit.py [save_file] [game_dir] [csv_file]

  save_file   DKSAVE*.SAV  (default: DARKLAND/SAVES/DKSAVE0.SAV)
  game_dir    Darklands install dir containing DARKLAND.LST  (default: DARKLAND/)
  csv_file    alchemy data CSV  (default: src/main/resources/darklands_alchemy.csv)
```

Output: one table per alchemist showing each known formula sorted by expected pf/attempt, with success%, raw profit, and risk rating. Formulae that are currently impossible to brew are listed separately.

---

### `src/main/python/organise_saves.py` — Sort save slots by in-game date

Renames all `DKSAVE*.SAV` files in a directory so slot 0 is the oldest save and the highest slot is the newest, sorted by in-game calendar date.

```
python organise_saves.py <saves_dir> [--dry-run]

  saves_dir   Path to DARKLAND/SAVES/
  --dry-run   Preview the proposed order without renaming anything
```

---

### `src/main/python/list_quests.py` — List pending quests

Parses a save file and prints all pending quests: what item to fetch or deliver, from/to which location, who commissioned it, and the deadline. Non-city locations are annotated with compass directions relative to the nearest cities.

```
python list_quests.py [save_file] --lst <darklands_dir>

  save_file       DKSAVE*.SAV (omit to use the most recently modified save in ./SAVES/)
  --lst DIR       Darklands install directory containing DARKLAND.LST
```

---

### `src/main/python/sort_inventory.py` — Sort character inventories

Rewrites character inventory order within a save file. Items are grouped and sorted by type (ammo → javelins → equipped → ingredients → potions → armor → weapons → misc), then alphabetically by name and quality descending within each group. A clothing item acts as a divider; items before it are left untouched.

```
python sort_inventory.py <save_file> --lst <darklands_dir> [--dry-run] [--backup]

  save_file       DKSAVE*.SAV to modify
  --lst DIR       Darklands install directory containing DARKLAND.LST
  --dry-run       Show proposed order without writing to disk
  --backup        Write a .bak copy of the save before modifying
```

---

### `src/main/python/highest_save_number.py` — Find highest run number in save labels

Scans all save slots, reads the in-game save labels, extracts embedded numbers (e.g. "run234b" → 234), and reports the maximum. Useful for tracking a playthrough counter across many saves. Highlights the winning save in the output.

```
python highest_save_number.py [saves_dir]

  saves_dir   Darklands install dir or SAVES/ subdir  (default: current directory)
```

---

### Library modules (not standalone)

- `src/main/python/format_sav.py` — save file parser; reads header fields (date, location, label) used by the other scripts
- `src/main/python/read_lst.py` — parses `DARKLAND.LST` item definitions; provides item names, flags, and sort groups to `sort_inventory.py` and `list_quests.py`

---

---

## Folder Structure

```
darklands_util/
├── DARKLAND/                         # Original DOS game files (binary)
│   ├── DARKLAND.EXE                  # Main game executable
│   ├── DARKLAND.LST   (14 KB)        # Master list: items, saints, formulae
│   ├── DARKLAND.SNT   (48 KB)        # Saint descriptions (binary, ~168 bytes/saint)
│   ├── DARKLAND.CTY   (57 KB)        # City data
│   ├── DARKLAND.MAP  (148 KB)        # World map data
│   ├── DARKLAND.ENM   (16 KB)        # Enemy data
│   ├── DARKLAND.ALC    (7 KB)        # Alchemy / formulae data
│   ├── DARKLAND.LOC   (24 KB)        # Location data
│   ├── DARKLAND.FAM    (1 KB)        # Family data
│   ├── DARKLAND.MSG                  # In-game messages
│   ├── DARKLAND.DSC                  # Descriptions
│   ├── *.CAT                         # Catalogue index files (A00C, C00C, E00C, F01C, F60C, M00C, IMAPS, EDITOR, EINFO)
│   ├── *.IMG / *.PAN / *.DGT         # Graphics / cutscene images
│   ├── *.DLC / *.DLB / *.DB / *.DC  # Audio files
│   ├── LEVEL0-6.ENM                  # Per-level enemy definitions
│   ├── dlq_src/                      # Source for a quest-related tool
│   ├── SAVES/                        # Save game files
│   ├── PICS/                         # Picture assets
│   ├── LCASTLE/                      # Castle-related assets
│   ├── MSGFILES/                     # Message files
│   └── *.EXE                         # Editors and utilities (DKED, DKQUE, EDITOR, etc.)
│
├── src/
│   ├── main/
│   │   ├── kotlin/bm/darkland/
│   │   │   ├── Main.kt               # Entry point; currently calls GeneralListParser
│   │   │   ├── model/
│   │   │   │   ├── Attribute.kt      # 7 character attributes (Endurance, Strength, etc.)
│   │   │   │   ├── Skill.kt          # 19 skills (weapon + non-weapon)
│   │   │   │   ├── Saint.kt          # Saint data class (id, fullName, shortName, description)
│   │   │   │   ├── DarklandList.kt   # Top-level list from DARKLAND.LST (saints + references)
│   │   │   │   ├── Catalogue.kt      # Parsed .CAT file container
│   │   │   │   └── CatalogueEntry.kt # Single entry within a catalogue file
│   │   │   ├── parser/
│   │   │   │   ├── Definitions.kt    # Path constants (e.g. DARKLAND.SNT filename)
│   │   │   │   ├── GeneralListParser.kt  # Parses DARKLAND.LST — reads saint names (incomplete)
│   │   │   │   ├── CatalogueParser.kt    # Parses .CAT files — reads entry metadata (working)
│   │   │   │   └── SaintParser.kt        # Parses DARKLAND.SNT — reads header only (stub)
│   │   │   ├── data/
│   │   │   │   └── SaintData.kt      # Hardcoded saint prayer effects (~140 saints) sourced from community
│   │   │   └── writer/
│   │   │       └── SaintJsonWriter.kt  # Writes List<Saint> to saints.json via Jackson
│   │   └── resources/
│   │       ├── darklands_manual.pdf  (55 MB)  # Original game manual
│   │       ├── darklands_cluebook.pdf (4 MB)  # Cluebook
│   │       ├── darklands_map.pdf      (5 MB)  # World map
│   │       ├── dksaints.swf         (626 KB)  # Flash app with saints data/UI
│   │       ├── dkmap.swf            (426 KB)  # Flash app with map data/UI
│   │       └── SaintClueText.txt     (16 KB)  # OCR'd saint prayer effects (raw, error-prone)
│   └── test/
│       └── kotlin/bm/darkland/parser/
│           └── GeneralListParserKtTest.kt  # Unit tests for null-delimited string extraction
│
└── pom.xml                           # Maven build (Kotlin 1.4.31, Jackson 2.12.1, JUnit Jupiter 5.7.1)
```

---

## Key Game File Formats

### `DARKLAND.LST`
Master list file. Binary layout:
- Byte 0: number of item slots
- Byte 1: number of saints
- Byte 2: number of formulae
- Bytes 3+: item definitions (46 bytes each), followed by null-delimited saint long names, then null-delimited saint short names

### `DARKLAND.SNT`
Binary saint description file. Each saint record is approximately 168 bytes. The internal structure is not yet fully decoded.

### `*.CAT` catalogue files
Index files for game assets. Layout:
- Byte 0: number of entries
- Each entry (24 bytes): filename (12 bytes), timestamp (2 bytes), length (2 bytes), offset (2 bytes)

---

## Implementation Status

| Component | Status |
|---|---|
| Attribute + Skill models | Complete |
| `CatalogueParser` | Working — reads `.CAT` entry metadata |
| `GeneralListParser` | Partial — reads headers, saint name extraction incomplete |
| `SaintParser` | Stub — reads file header only |
| `SaintJsonWriter` | Written but not wired into main flow |
| `SaintData` hardcoded fallback | Complete (~140 saints from community data) |
| Item / formulae parsing | Not started |
| SWF parsing | Not started |

---

## Reference Material

- [Darklands Companion](https://github.com/illusium77/darklandscompanion) — community project, source of the saint prayer data in `SaintData.kt`
- Original game manual and cluebook are in `src/main/resources/`
