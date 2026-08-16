#!/usr/bin/env python3
"""
dump_web_data.py — Dump DARKLAND.LST item defs, formula table, and the alchemy
CSV as JSON, for embedding as static data in the zero-backend web/ pages.

Usage:
    python dump_web_data.py <darklands_dir> <alchemy_csv> <out_dir>
"""
import sys
import json
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..'))

from read_lst import read_lst
from alchemy_profit import load_formula_table, load_alchemy_csv, FORMULA_TYPES


def main():
    darklands_dir = sys.argv[1]
    csv_path = sys.argv[2]
    out_dir = sys.argv[3]

    items = read_lst(darklands_dir)
    item_defs = [
        {
            'code': d.code,
            'name': d.name,
            'shortName': d.short_name,
            'value': d.value,
            'isNonmetalArmor': d.is_nonmetal_armor,
            'isMetalArmor': d.is_metal_armor,
            'isShield': d.is_shield,
            'isArrow': d.is_arrow,
            'isQuarrel': d.is_quarrel,
            'isThrown': d.is_thrown,
            'isPotion': d.is_potion,
            'isThrowPotion': d.is_throw_potion,
            'isComponent': d.is_component,
            'isEdged': d.is_edged,
            'isImpact': d.is_impact,
            'isPolearm': d.is_polearm,
            'isFlail': d.is_flail,
            'isBow': d.is_bow,
            'isMissileWeapon': d.is_missile_weapon,
        }
        for d in items
    ]

    formula_table = load_formula_table(darklands_dir)

    potions = load_alchemy_csv(csv_path)
    potions_list = [
        {'key_prefix': k[0], 'key_quality': k[1], **v}
        for k, v in potions.items()
    ]

    os.makedirs(out_dir, exist_ok=True)

    with open(os.path.join(out_dir, 'lst_items.json'), 'w', encoding='utf-8') as f:
        json.dump(item_defs, f, ensure_ascii=False)

    with open(os.path.join(out_dir, 'lst_formulas.json'), 'w', encoding='utf-8') as f:
        json.dump({'formulaTypes': FORMULA_TYPES, 'formulaTable': formula_table}, f, ensure_ascii=False)

    with open(os.path.join(out_dir, 'alchemy_potions.json'), 'w', encoding='utf-8') as f:
        json.dump(potions_list, f, ensure_ascii=False)

    print(f'items: {len(item_defs)}  formulas: {len(formula_table)}  potions: {len(potions_list)}')


if __name__ == '__main__':
    main()
