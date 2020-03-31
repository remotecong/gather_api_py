from .owner_info import get_owner_data
from .thatsthem import get_phone_numbers
from datetime import timedelta
import redis
import json

r = redis.Redis(host='redis')

def lookup(address):
    # try cache first
    cache = r.get(address)
    if cache:
        return json.loads(cache)

    d = get_owner_data(address)
    phones = get_phone_numbers(address)

    d['phones'] = []

    # for easier searching
    ln = d['last_name'].lower()

    for p in phones:
        n = p['name'].lower()
        if (d['lives_there'] and ln in n) or\
            (not d['lives_there'] and ln not in n):
            d['phones'].append(p)

    r.setex(address, timedelta(hours=1), value=json.dumps(d))

    return d
