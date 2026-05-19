# Darklands Utility — Working Resources

This folder holds the working reference material for a utility project supporting **Darklands** (MicroProse, 1992). It is a collection of source documents and images extracted or compiled from the original game's documentation, used as the data backbone for the utility.

The user is processing these documents via Cowork.

## Primary documents

- `darklands_cluebook.pdf` — The official cluebook. Explains the underlying rules and exposes the **raw game mechanics** (formulas, tables, numeric values, probabilities). This is the authoritative source for mechanical detail.
- `darklands_manual.pdf` — The original game manual. Covers the same rules and systems but written for players; it describes how things work **without** giving the raw mechanical numbers. Use this for context, flavour, and narrative-level explanation; use the cluebook for hard numbers.

## Extracted data (CSV)

These CSVs are structured extracts taken from the cluebook, intended to be machine-readable.

- `darklands_alchemy.csv` — Alchemy potion data extracted from the cluebook. Columns: `name, quality, magic number, risk, ingredients, potion value, comp value, further info`. Each potion has three quality tiers (25 / 35 / 45) named after the alchemist who discovered that quality level.
- `saint_details.csv` — Saint data extracted from the cluebook. Columns: `Name, Virtue, Divine Favour, base success, status effects, detail text, special effects`. The `special effects` column uses pipe-separated tags (e.g. `heal|prevent-fight`) for programmatic filtering.

## Other contents

The folder also contains supporting images and other reference assets used alongside the documents above.

## Notes for working in this folder

- When a question is about exact mechanics, formulas, or numbers, prefer the **cluebook** over the manual.
- The CSVs are derived data — if there is ever a conflict, the cluebook PDF is the source of truth.
- The two main PDFs are large (cluebook ~39 pages, manual ~562 pages). Read them in page ranges rather than all at once.
