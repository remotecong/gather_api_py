""" module to actual print the territory data """
import sys
from mongo import get_all_docs_for, get_gather_address

def key_residence(res):
    """ mapper for sorting residences """
    return res["address"]

if len(sys.argv) != 2:
    raise ValueError("you need to include a territory id")

TERR = sys.argv[1]
print("finding addresses for {}".format(TERR))

territory = {}

for doc in get_all_docs_for(TERR):
    if "street" in doc:
        street = doc["street"]
        if street not in territory:
            territory[street] = []
        territory[street].append(doc)
    else:
        raise ValueError("no street?")

for street, residences in territory.items():
    print("\n\n=========================================================\n{}".format(street))
    residences.sort(key=key_residence)
    for r in residences:
        printable_addr = get_gather_address(r["address"])
        if "ownerLivesThere" in r:
            if "phoneNumbers" in r:
                #   first two numbers, any more we don't track (unless some disconnected)
                phones = list({p["number"] for p in r["phoneNumbers"]})[0:2]
                phones = ", ".join(phones) if len(phones) > 0 else "No Number Found"
                print("{}\t{}\t{}".format(r["name"], printable_addr, phones))
            elif r["ownerLivesThere"]:
                print("{}\t{}\t{}".format(r["ownerName"], printable_addr, "No Number Found"))
            else:
                print("Current Resident\t{}\tNo Number Found".format(printable_addr))
        else:
            print("Unknown\t{}\tN/A".format(printable_addr))
