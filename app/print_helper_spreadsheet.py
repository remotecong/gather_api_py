""" module to actual print the territory data """
import sys

from addresses import get_gather_address, get_street
from mongo import get_all_docs_for
from names import pretty_print_name

def key_residence(res):
    """ mapper for sorting residences """
    return res["address"]


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

    all_residences = get_territory_docs(territory_id)

    if len(all_residences) < 1:
        raise ValueError("no residences found for {}".format(territory_id))

    print("Territory {}".format(territory_id))

    for street, residences in all_residences:
        print("\n\n=========================================================\n{}\n".format(street))
        residences.sort(key=key_residence)

        for res in residences:
            printable_addr = get_gather_address(res["address"])
            dnc = "DO NOT CALL!" if "doNotCall" in res and res["doNotCall"] else ""
            url = "https://www.assessor.tulsacounty.org/assessor-property.php?account={}&go=1".format(res.get("assessorAccountNumber")) if res.get("assessorAccountNumber") else "Not found on assessor"
            conflict_message = ""

            if res.get("houseNumConflict"):
                map_link = "http://www.google.com/maps/place/{}".format(",".join(res.get("coords")))
                conflict_message = "Assessor's address doesn't match, please verify " + \
                "address and adjust as necessary!\n{}".format(map_link)
                printable_addr = "*" + printable_addr

            print("{}\t{}\t{}\t{}".format(printable_addr, url, conflict_message, dnc))


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise ValueError("you need to include a territory id")
    print_territory(sys.argv[1])

