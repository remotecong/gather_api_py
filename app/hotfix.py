""" fix a few bad addresses """
import re
from mongo import find_bad_address, add_phone_data

for doc in find_bad_address():
    print(doc["address"])
    new_address = re.sub(r'^(\d+) ', r'\1 E ', doc["address"])
    add_phone_data(doc, {"address": new_address})

