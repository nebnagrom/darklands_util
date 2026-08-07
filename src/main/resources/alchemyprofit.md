# Darklands Alchemy Profit Analysis

Bootstrap document for a dynamic alchemy profit calculator utility.

---

## Data Sources

- **`darklands_alchemy.csv`** — structured potion data (columns: `name, quality, magic number, risk, ingredients, potion value, comp value, further info`)
- **`darklands_cluebook.md`** — source of truth for all mechanics; alchemy section starts at the `# Alchemy` heading

---

## The Success Formula

From the cluebook:

```
success_chance = Philosopher's Stone value + Intelligence + Alchemy skill − Magic number
```

- If `total >= magic number`: success is capped at **99%** (virtually automatic)
- If `total < magic number`: `success% = 100 − (magic number − total)`
- If that result is ≤ 0: the formula is **impossible** to brew

**Batch penalty:** Making 4+ potions per person per day reduces the effective "k" constant (normally 100), lowering success rates. Best practice is ≤ 3 potions per alchemist per day.

---

## Expected Profit Formula

Raw profit (if you always succeeded) = `potion value − comp value`

But failures still consume ingredients, so the correct figure is **expected profit per attempt**:

```
expected_profit = (success_rate × potion_value) − comp_value
```

- On success: net = `potion_value − comp_value`
- On failure: net = `−comp_value`
- Combined: `success_rate × potion_value − comp_value`

This is the correct ranking metric — not raw profit.

---

## Example Calculation (Alch 30, Int 40, Pstone 6)

Total = 6 + 40 + 30 = **76**

| Potion | Magic# | Success% | Raw Profit | Exp. Profit/attempt |
|--------|--------|----------|------------|---------------------|
| RL Firewall (q45) | 127 | 49% | 562pf | **177pf** |
| BE Sunburst (q45) | 110 | 66% | 339pf | **170pf** |
| Av Essence of Grace (q45) | 98 | 78% | 240pf | **158pf** |
| MS Black Cloud (q45) | 112 | 64% | 289pf | **153pf** |
| Mam Firewall (q35) | 122 | 54% | 407pf | **126pf** |
| JR New-wind (q45) | 107 | 69% | 269pf | **124pf** |
| MS Essence of Grace (q35) | 90 | 86% | 156pf | **114pf** |
| RL Sunburst (q35) | 99 | 77% | 205pf | **113pf** |
| MS New-wind (q35) | 99 | 77% | 199pf | **112pf** |
| Af Sunburst (q25) | 91 | 85% | 122pf | **76pf** |

**Impossible with these stats** (magic number > 176): all Transformation variants (195–210), all Breath of Death variants (189–199).

**Money losers despite high raw profit**: Arabian Fire (6–16% success), Eater Water, Hardarmor, most Thunderbolt tiers — ingredient costs outweigh expected return.

---

## What a Dynamic Utility Needs

### Inputs (character stats)
- `alchemy_skill` (integer)
- `intelligence` (integer)
- `pstone_value` (integer) — philosopher's stone quality; typically 0 (none) to ~35 (best obtainable)

### Data to read
- Parse **`darklands_alchemy.csv`** for all potion rows: name, quality, magic number, potion value, comp value, ingredients, risk

### Calculations per potion
1. `total = alchemy_skill + intelligence + pstone_value`
2. `success_rate = min(0.99, max(0, (100 - (magic_number - total)) / 100))`
3. `raw_profit = potion_value - comp_value`
4. `expected_profit = (success_rate * potion_value) - comp_value`
5. Flag as `IMPOSSIBLE` if `success_rate <= 0`

### Output / ranking
- Sort by `expected_profit` descending
- Show: potion name, quality, magic#, success%, raw profit, expected profit
- Suppress or clearly mark impossible potions
- Optionally filter by `risk` level (low / mod / high) — relevant if brewing in cities (failure risk triggers city reputation penalties)

### Useful extensions
- **Filter by known formulas**: the character only knows certain recipes; utility should accept a list and filter to those
- **Filter by available ingredients**: cross-reference a stock list against the `ingredients` column
- **Batch mode**: show total expected profit for a day's brewing (≤ 3 potions, same formula or mixed)
- **Breakeven stone quality**: for each formula, show the minimum pstone needed to reach a given success threshold (e.g. 70%, 90%, 99%)

---

## Notes on Data Fidelity

- `potion value` and `comp value` in the CSV are averages for a size-5 city; actual in-game prices vary by city size and a random factor
- Component costs can vary "sometimes considerably" per the cluebook — the comp value is a guide, not a guarantee
- The CSV is derived from the cluebook; if values conflict, the **cluebook PDF** is the source of truth
- Transformation potions (all tiers) also yield 1 florin (240pf) per success on top of sale value — factor this into their expected profit if they become brewable
