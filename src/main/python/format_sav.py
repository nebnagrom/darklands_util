"""
Darklands save file parser.
Adapted from https://github.com/vvendigo/Darklands (format_sav.py + utils.py).
Only the fields needed for save-slot management are parsed.
"""
from struct import unpack
from datetime import datetime


def _cstrim(raw):
    return str(raw[:raw.find(b'\x00')].decode('ascii'))


class Save:
    def __init__(self):
        self.path = None
        self.curr_location_name = ''
        self.save_game_label = ''
        self.curr_date = None
        self.curr_location = None
        self.curr_coords = None
        self.num_characters = 0

    def from_data(self, data):
        pos = 0
        self.curr_location_name = _cstrim(unpack('12s', data[pos:pos+12])[0]); pos += 12
        pos += 9
        self.save_game_label = _cstrim(unpack('23s', data[pos:pos+23])[0]); pos += 23
        pos += 18
        pos += 37   # not 55 per original notes
        pos += 1
        pos += 2    # city_contents_seed
        pos += 2
        y, m, d, h = unpack('HHHH', data[pos:pos+8]); pos += 8
        self.curr_date = datetime(y, m + 1, d, h)
        pos += 6    # party_money
        pos += 4
        pos += 2    # reputation
        self.curr_location = unpack('h', data[pos:pos+2])[0]; pos += 2
        self.curr_coords = unpack('HH', data[pos:pos+4]); pos += 4
        pos += 2    # curr_menu
        pos += 6
        pos += 2    # prev_menu
        pos += 2    # bank_notes
        pos += 4
        pos += 2    # philosopher_stone
        pos += 7
        pos += 5    # party_order_indices (5*byte, not string)
        pos += 1
        pos += 1    # party_leader_index
        pos += 3
        pos += 74
        pos += 2    # num_curr_characters
        self.num_characters = unpack('H', data[pos:pos+2])[0]

    def __repr__(self):
        return f'[{self.save_game_label}] {self.curr_date:%Y-%m-%d} @ {self.curr_location_name}'


def read_file(path):
    save = Save()
    save.path = path
    with open(path, 'rb') as f:
        save.from_data(f.read())
    return save
