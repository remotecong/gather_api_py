from .owner_info import get_owner_data
from .thatsthem import get_phone_numbers

def lookup(address):
    print(address)
    d = get_owner_data(address)
    d['phones'] = get_phone_numbers(address)
    return d
