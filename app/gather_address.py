""" actually does the lookups """
import sys
from mongo import get_ungathered_address_for, get_gather_address, add_owner_data, get_addresses_without_thatsthem_data
from owner_info import get_owner_data
from thatsthem import get_phone_numbers

if len(sys.argv) != 2:
    raise ValueError("you need to include a territory id")

TERR = sys.argv[1]
print("finding addresses for {}".format(TERR))

docs = get_ungathered_address_for(TERR)
if docs:
    for doc in docs:
        print(doc)
        gather_address = get_gather_address(doc["address"])
        try:
            assessor_data = get_owner_data(gather_address)
            add_owner_data(doc, assessor_data)
            print("<=> {} --> {}".format(gather_address, assessor_data))
        except Exception as e:
            print("FAIL {}".format(e))

docs = get_addresses_without_thatsthem_data(TERR)
if docs:
    for doc in docs:
        gather_address = get_gather_address(doc["address"])
        thatsthem_data = get_phone_numbers()

print("<> <> done <> <>")
