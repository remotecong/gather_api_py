""" module to actual print the territory data """
import sys
from addresses import get_gather_address, get_street
from mongo import get_all_docs_for
from names import pretty_print_name

def key_residence(res):
    """ mapper for sorting residences """
    return res["address"]

def ppp(name, address, phone, notes):
    """ handles printing records """
    if phone == "No Number Found":
        call_note = "-"
    elif phone == "Do Not Call":
        call_note = "DNC"
    else:
        call_note = ""
    print("{}\t{}\t{}\t{}\t{}\t{}".format(name, address, phone, call_note, call_note, notes))

def get_territory_docs(territory_id):
    """ collects all docs for territory """
    territory = {}
    for doc in get_all_docs_for(territory_id):
        street = get_street(doc["address"])
        if street not in territory:
            territory[street] = []
        territory[street].append(doc)
    return territory.items()

def phone_number_sort(num):
    """ prep phone numbers for sorting tulsa numbers first """
    if num.startswith("918-"):
        return 0
    return 1

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
                continue

            # sometimes name is saved as null if thatsthem has no results
            # and owner doesn't live there
            name = pretty_print_name(res.get("name", "Current Resident") or "Current Resident")

            # DO NOT CALL!
            if dnc:
                ppp(name, printable_addr, "Do Not Call", "DNC")
                continue

            phone_numbers = res["phoneNumbers"] if "phoneNumbers" in res else []
            # first two numbers, any more we don't track (unless some disconnected)
            uniq_phones = list({p["number"] for p in phone_numbers})
            uniq_phones.sort(key=phone_number_sort)
            phones = uniq_phones[0:2]

            if len(phones) == 0:
                phones.append("No Number Found")
            for i, p in enumerate(phones):
                ppp(
                    name if i == 0 else "▲",
                    printable_addr if i == 0 else "▲",
                    p,
                    "" if i == 0 else "⃠"
                )
            #ppp(name, printable_addr, phones)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise ValueError("you need to include a territory id")
    print_territory(sys.argv[1])
