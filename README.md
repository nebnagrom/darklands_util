# darklands_util

A Kotlin utility for parsing and extracting data from the 1992 DOS RPG *Darklands* by MicroProse. The primary goal is to read the game's proprietary binary files and export their contents into modern formats (JSON, etc.) for analysis and reference.

The initial focus is the Saints system — the game's prayer and blessing mechanic — but the project also touches catalogue files, item lists, and world data.

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
