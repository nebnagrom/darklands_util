"""
Read DARKLAND.LST item definitions.
Adapted from reader_lst.py in https://github.com/vvendigo/Darklands.
Self-contained — no external dependencies.
"""
import os
import struct


def _sread(data, start, maxlen):
    end = start
    limit = start + maxlen
    while end < limit and data[end] != 0:
        end += 1
    return data[start:end].decode('ascii', errors='replace')


def _word(data, pos):
    return struct.unpack_from('<H', data, pos)[0]


_FLAG_ROWS = [
    ('is_edged', 'is_impact', 'is_polearm', 'is_flail', 'is_thrown', 'is_bow', 'is_metal_armor', 'is_shield'),
    ('is_unknown1', 'is_unknown2', 'is_component', 'is_potion', 'is_relic', 'is_horse', 'is_quest_1', 'is_const0_1'),
    ('is_lockpicks', 'is_light', 'is_arrow', 'is_const0_2', 'is_quarrel', 'is_ball', 'is_const0_3', 'is_quest_2'),
    ('is_throw_potion', 'is_const0_4', 'is_nonmetal_armor', 'is_missile_weapon', 'is_unknown3', 'is_music', 'is_const0_6', 'is_const0_7'),
    ('is_unknown4', 'is_unknown5', 'is_const0_8', 'is_const0_9', 'is_const0_10', 'is_const0_11', 'is_const0_12', 'is_unknown6'),
]

# Sort-group constants (lower = closer to top of inventory)
GRP_AMMO       = 0
GRP_THROWN     = 1
GRP_EQUIPPED   = 2
GRP_INGREDIENT = 3
GRP_POTION     = 4
GRP_ARMOR      = 5
GRP_WEAPON     = 6
GRP_MISC       = 7


class ItemDef:
    __slots__ = (
        ['code', 'name', 'short_name', 'lst_type', 'value', 'weight', 'quality', 'rarity']
        + [f for row in _FLAG_ROWS for f in row]
    )

    def sort_group(self):
        if self.is_arrow or self.is_quarrel:
            return GRP_AMMO
        if self.is_thrown:
            return GRP_THROWN
        if self.is_potion or self.is_throw_potion:
            return GRP_POTION
        if self.is_component:
            return GRP_INGREDIENT
        if (self.is_edged or self.is_impact or self.is_polearm
                or self.is_flail or self.is_bow or self.is_missile_weapon):
            return GRP_WEAPON
        if self.is_metal_armor or self.is_nonmetal_armor or self.is_shield:
            return GRP_ARMOR
        return GRP_MISC

    def is_clothing_divider(self):
        """Zero-cost nonmetal-armor item — used as an inventory section marker."""
        return self.is_nonmetal_armor and self.value == 0

    def __repr__(self):
        return f'<ItemDef {self.code} {self.name!r}>'


def read_lst(darklands_dir):
    """Return list of ItemDef objects indexed by LST code."""
    path = os.path.join(darklands_dir, 'DARKLAND.LST')
    data = open(path, 'rb').read()

    item_count = data[0]
    pos = 3  # skip item_count, saint_count, form_count bytes

    items = []
    for i in range(item_count):
        d = ItemDef()
        d.code = i
        d.name       = _sread(data, pos, 20);  pos += 20
        d.short_name = _sread(data, pos, 10);  pos += 10
        d.lst_type   = _word(data, pos);        pos += 2
        for row in _FLAG_ROWS:
            bits = data[pos]; pos += 1
            for b, fname in enumerate(row):
                setattr(d, fname, bool(bits & (1 << b)))
        d.weight  = data[pos]; pos += 1
        d.quality = data[pos]; pos += 1
        d.rarity  = data[pos]; pos += 1
        pos += 4  # unknown1, unknown2 (non-zero only for relics)
        d.value = _word(data, pos); pos += 2
        items.append(d)

    return items
