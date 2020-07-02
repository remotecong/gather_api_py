""" module to actual print the territory data """
import sys
from mongo import get_all_docs_for, get_gather_address

def key_residence(res):
    """ mapper for sorting residences """
    return res["address"]

def ppp(name, address, phones, notes=None):
    """ handles printing records """
    if notes:
        print("{}\t{}\t{}\t{}".format(name, address, phones, notes))
    else:
        print("{}\t{}\t{}".format(name, address, phones))

class TerritoryMissingStreetException(Exception):
    """ exception thrown when street name missing """

def get_territory_docs(territory_id):
    """ collects all docs for territory """
    territory = {}
    for doc in get_all_docs_for(territory_id):
        if "street" in doc:
            street = doc["street"]
            if street not in territory:
                territory[street] = []
            territory[street].append(doc)
        else:
            raise TerritoryMissingStreetException
    return territory.items()

def print_territory(territory_id):
    """ print territory outright """
    print("=== Printing Territory {} ===".format(territory_id))

    for street, residences in get_territory_docs(territory_id):
        print("\n\n=========================================================\n{}\n".format(street))
        residences.sort(key=key_residence)
        for res in residences:
            printable_addr = get_gather_address(res["address"])
            dnc = "doNotCall" in res and res["doNotCall"]

            # assessor missed this one
            if "ownerLivesThere" not in res:
                ppp("Unknown", printable_addr, "Do Not Call" if dnc else "N/A", "DNC")
                return

            name = res["name"] if "name" in res else "Current Resident"

            # DO NOT CALL!
            if dnc:
                ppp(name, printable_addr, "Do Not Call", "DNC")

            phone_numbers = res["phoneNumbers"] if "phoneNumbers" in res else []
            # first two numbers, any more we don't track (unless some disconnected)
            phones = list({p["number"] for p in phone_numbers})[0:2]

            if len(phones) > 1:
                phones = "\"{}\"".format("\n".join(phones))
            elif len(phones) > 0:
                phones = "".join(phones)
            else:
                phones = "No Number Found"
            ppp(name, printable_addr, phones)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise ValueError("you need to include a territory id")
    print_territory(sys.argv[1])
