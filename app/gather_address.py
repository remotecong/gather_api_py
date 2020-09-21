""" actually does the lookups """
import re
import sys
import signal

from mongo import (
    add_owner_data,
    add_phone_data,
    change_address_and_add_owner_data,
    get_addresses_without_thatsthem_data,
    get_docs_without_phone_num_but_ttd,
    get_ungathered_address_for,
)
from addresses import get_gather_address, get_verbose_address
from geocode import find_location_by_bad_address
from locations_convert import load_territory_with_logs
from owner_info import get_owner_data
from owner_parsers.tulsa import fetch_owner_data_from_permalink
from thatsthem import get_phone_numbers, ThatsThemNoMatchException
from geo_json import find_acct_num


class ThatsThemNoDataException(Exception):
    """ custom error for thatsthem errors """

class AddressHouseNumberConflictException(Exception):
    """ custom error to pre-resolve address conflicts """

def phone_number_sort(rec):
    """ prep phone numbers for sorting tulsa numbers first """
    if rec["number"].startswith("918-"):
        return 0

    return 1


def compile_final_doc(doc, thatsthem_data, ignore_no_data=False, autopilot=False):
    """ connects existing doc with address to gather data """
    # name for record
    name = None
    # last name for matching
    last_name = None

    first_piece_of_name = None
    thats_them_match_count = 0
    has_override_name = "overrideLastName" in doc

    if has_override_name:
        # just use this value for all names
        name = doc["overrideLastName"]
        first_piece_of_name = name
        last_name = name

    elif doc["ownerLivesThere"]:
        name = doc["ownerName"]
        first_piece_of_name = name.split(",")[0].strip()
        last_name = re.sub(
            r' (TRUST|FAMILY|FAMILY TRUST|FAMILY REV TRUST|' +
            r'2020 TRUST|REV TRU?S?T?|FAMILY REVOCABLE TRUST|' +
            r'REV TRUST C/O.*|REVOCABLE TRUST DATED.*|' +
            r'LIVING TRUST|FAMILY TRUST C/O.*)?$',
            '',
            first_piece_of_name,
            flags=re.IGNORECASE
        )
        #   allow matches for names including hyphens
        last_name = re.sub(r'-', '-?', last_name)
        last_name = re.sub(r' ', ' ?', last_name)
        last_name = re.sub(r'\'', '\'?', last_name)
        last_name = re.sub(r'^MC([A-Z]+)', r'MC ?\1', last_name)

    elif len(thatsthem_data) > 0:
        name = thatsthem_data[0]["name"]
        last_name = name.split(" ")[-1]

    elif not ignore_no_data:
        raise ThatsThemNoDataException("no owner at {}".format(doc["address"]))

    # filter all thatsthem data for last_name
    lname_re = re.compile("{}( jn?r| sn?r| ii| iii)?$".format(last_name), re.IGNORECASE)
    phone_numbers = []

    for thatsthem in thatsthem_data:
        if lname_re.search(thatsthem["name"]):
            thats_them_match_count += 1
            phone_numbers = phone_numbers + thatsthem["numbers"]

    if not autopilot and thats_them_match_count == 0 and ("skip_no_match" not in doc or not doc["skip_no_match"]):
        assessor_acct_num = doc.get("assessorAccountNumber", None)

        if assessor_acct_num:
            url = "https://www.assessor.tulsacounty.org/assessor-property.php" + \
                "?account={}&go=1".format(assessor_acct_num)
            print(url)
        print("### I thought the last name was {}".format(first_piece_of_name))
        print("### because the full name is {}\n".format(name))

        for thatsthem in thatsthem_data:
            print("* {}".format(thatsthem["name"]))

        print("\n### but I can't find a match in ThatsThem so do you want to")
        print("(f)ix, (m)ove on temporarily, (r)enter lives there, (c)onfirm no match, or (q)uit?")
        action = input("f/m/c/r/q: ")

        if action == "q":
            raise Exception("Goodbye!")

        if action == "f":
            shallow_doc = {
                "_id": doc["_id"],
                "ownerLivesThere": True,
                "ownerName": doc["ownerName"],
                "overrideLastName": input("New Last Name: "),
                "originalName": name,
                "adjustedAddress": doc.get("adjustedAddress", None),
            }
            return compile_final_doc(shallow_doc, thatsthem_data)

        if action == "r":
            doc["ownerLivesThere"] = False
            result_data = compile_final_doc(doc, thatsthem_data)
            result_data.update({
                "ownerLivesThere": False,
                "adjustedAddress": doc.get("adjustedAddress", None),
            })
            return result_data

        return {
            "name": name,
            "phoneNumbers": phone_numbers,
            "thatsThemData": thatsthem_data,
            "adjustedAddress": doc.get("adjustedAddress", None),
            "skip_no_match": action.strip().lower() == "c"
        }

    phone_numbers.sort(key=phone_number_sort)

    if has_override_name:
        return {
            "name": doc["originalName"],
            "phoneNumbers": phone_numbers,
            "thatsThemData": thatsthem_data,
            "overrideLastName": doc["overrideLastName"],
            "adjustedAddress": doc.get("adjustedAddress", None),
        }

    return {
        "name": name,
        "phoneNumbers": phone_numbers,
        "thatsThemData": thatsthem_data,
        "adjustedAddress": doc.get("adjustedAddress", None),
    }


def get_assessor_data(territory_id, autopilot=False):
    """ load assessor data for territory """
    docs = get_ungathered_address_for(territory_id)
    for doc in docs:
        get_assessor_data_for_doc(doc, None, 1, autopilot)


def print_assessor_permalink(doc):
    """ prints link if account number is set """
    acct = doc.get("assessorAccountNumber", None)
    if acct:
        print("https://www.assessor.tulsacounty.org/assessor-property.php" + \
            "?account={}&go=1".format(acct))


def get_assessor_data_for_doc(doc, override_address=None, tries=1, autopilot=False):
    """ single assessor lookup """
    try:
        acct_num = doc.get("assessorAccountNumber", None)
        # try geojson for assessor first!
        if not acct_num and tries == 1 and "coords" in doc:
            acct_num = find_acct_num(doc["coords"])
        gather_address = get_gather_address(override_address or doc["address"])

        if acct_num:
            url = "https://www.assessor.tulsacounty.org/assessor-property.php" + \
                "?account={}&go=1".format(acct_num)
            print("\nAssessor Lookup with Permalink: {} --- ".format(url))
            assessor_data = fetch_owner_data_from_permalink(url)
        else:
            print("\nAssessor Lookup: {} --- ".format(gather_address))
            assessor_data = get_owner_data(gather_address)

        if override_address:
            print("")
            print("[==] Address changed! Be sure to update TerritoryHelper")
            print("[==] Search for: {}".format(doc["address"]))
            print("[==] Change  to: {}".format(override_address))
            change_address_and_add_owner_data(doc, override_address, assessor_data)

        else:
            add_owner_data(doc, assessor_data)

        return assessor_data

    except TypeError as e:
        # if autopilot, just move on to the next one.
        if not autopilot and tries > 2:
            print("\nThis address cannot be found!\n{}".format(doc["address"]))
            print(gather_address)
            print("\nWould you like to:\n(c)ontinue to next house, (s)et assessor ID, or (q)uit?")
            next_step = input("c/s/q: ")

            if next_step == "q":
                raise Exception("Goodbye!")

            if next_step == "s":
                assessor_id = input("Paste in assessor ID: ")
                doc["assessorAccountNumber"] = assessor_id
                return get_assessor_data_for_doc(doc, None, tries+1)

        if not autopilot and tries > 1:
            print("No match on Assessor for -- {}".format(doc["address"]))
            print("(Searched for: {})".format(gather_address))
            print("Assessor couldn't find address\n(c)hange address, (s)et assessor id, (n)ext")
            customize_address = input("c/s/n: ")

            if customize_address == "c":
                print("old address: {}".format(doc["address"]))
                new_address = input("new address: ").strip()
                get_assessor_data_for_doc(doc, new_address, tries+1)

            elif customize_address.strip() == "s":
                assessor_id = input("Paste in assessor ID: ")
                doc["assessorAccountNumber"] = assessor_id
                get_assessor_data_for_doc(doc, None, tries+1)

            elif customize_address.strip() != "n":
                print("ERROR ==> {}".format(e))

        elif tries == 1:
            print("Assessor couldn't find {}".format(gather_address))
            print("So I'm going to try to get a new address from Google based on this house's GPS.")
            new_address = find_location_by_bad_address(doc["address"].split(",")[0])
            get_assessor_data_for_doc(doc, new_address, tries+1, autopilot)

        else:
            print("Assessor couldn't find {}\nMoving on now...".format(gather_address))

    except Exception as exc:
        print("#### DEBUG ASSESSOR EXCEPTION ####\n{}\n{}\n".format(doc, exc))


def get_thatsthem_data(doc, override_address=None, autopilot=False):
    """ put together thatsthem data """
    try:
        if not override_address and \
           not autopilot and \
           not doc.get("adjustedAddress", None) and \
           doc.get("houseNumConflict", None):
            raise AddressHouseNumberConflictException

        is_street = re.search(r"[0-9]+ [NEWS] [0-9]+", doc["address"])
        if override_address:
            gather_address = override_address

        elif is_street:
            gather_address = get_gather_address(doc["address"])

        else:
            gather_address = get_verbose_address(doc["address"])

        thatsthem_data = get_phone_numbers(gather_address)
        add_phone_data(doc, compile_final_doc(doc, thatsthem_data, False, autopilot))

    except ThatsThemNoMatchException:
        if not override_address:
            override_address = get_verbose_address(doc["address"]) if is_street \
                else get_gather_address(doc["address"])
            return get_thatsthem_data(doc, override_address, autopilot)

        if not autopilot:
            print("\nThatsThem couldn't find a match for this address.")
            print("Would you like to try to search a slightly different address?")
            print("Official Address: {}".format(doc["address"]))
            print_assessor_permalink(doc)
            print("Address Searched for on ThatsThem: {}\n".format(get_gather_address(doc["address"])))
            action = input("(n)ew address, (c)ontinue, or (q)uit: ")
            print("")

            if action == "n":
                new_addr = input("Enter address to use for ThatsThem: ")
                return get_thatsthem_data(doc, new_addr, autopilot)

            if action == "q":
                raise Exception("Goodbye!")

            # give back empty result set
        add_phone_data(doc, compile_final_doc(doc, [], True, autopilot))

    except AddressHouseNumberConflictException:
        print("A house number conflict has been detected!")
        print_assessor_permalink(doc)
        print("On record: {}".format(doc.get("address")))
        print("Would you like to review and correct now?")

        if input("y/n: ") == "y":
            new_address = input("Change to: ")
            doc.update({"adjustedAddress": new_address})
            return get_thatsthem_data(doc)

    except ThatsThemNoDataException:
        add_phone_data(doc, {
            "thatsThemData": thatsthem_data,
            "phoneNumbers": [],
            "name": "Current Resident",
            "skip_no_match": True,
            })
    return None


def finalize_pending_thatsthem_matches(territory_id):
    """ get all docs with thatsthem data and make sure it's got the best data """
    for doc in get_docs_without_phone_num_but_ttd(territory_id):
        add_phone_data(doc, compile_final_doc(doc, doc["thatsThemData"]))


def fetch_all_missing_thatsthem_data(territory_id, autopilot):
    """ get fresh data from thatsthem for all docs in territory """
    for doc in get_addresses_without_thatsthem_data(territory_id):
        if "ownerLivesThere" in doc:
            get_thatsthem_data(doc, None, autopilot)
        else:
            print(">>> No Assessor data found for {}".format(doc["address"]))
            print("Do you want to try getting Assessor data again then retry ThatsThem?")
            if input("y/n: ") == "y":
                assessor_data = get_assessor_data_for_doc(doc, None, 1, autopilot)
                get_thatsthem_data(doc.update(assessor_data), doc["address"], autopilot)


def pickup_territory_work(t_id, autopilot=False):
    """ running gather from script or as module """
    load_locations_if_needed(t_id)
    get_assessor_data(t_id, autopilot)
    if not autopilot:
        finalize_pending_thatsthem_matches(t_id)
    fetch_all_missing_thatsthem_data(t_id, autopilot)


def load_locations_if_needed(t_id):
    """ checks if we have loaded locations for this territory recently """
    try:
        with open("territory_in_progress", "r+") as last:
            if last.read() != t_id:
                load_locations_for(t_id)
    except FileNotFoundError:
        load_locations_for(t_id)


def load_locations_for(t_id):
    """ loads locations for territory and logs it as last territory """
    with open("territory_in_progress", "w") as record:
        record.write(t_id)
    load_territory_with_logs(t_id)


def outatime():
    """ if you did an autopilot """
    print("Goodbye!")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        TERRITORY_ID = sys.argv[1]
        AUTOPILOT = len(sys.argv) > 2 and \
            sys.argv[2].strip() in ["--autopilot", "autopilot", "a", "-a"]
        print("<> <> pulling up territory {} {} <> <>".format(TERRITORY_ID, "(with autopilot)" if AUTOPILOT else ""))
        pickup_territory_work(TERRITORY_ID, AUTOPILOT)

        if AUTOPILOT:
            signal.signal(signal.SIGALRM, outatime)
            signal.alarm(3)
            print("Would you like to go through the thatsthems that need verification?")
            if input("y/n: ") == "y":
                signal.alarm(0)
                finalize_pending_thatsthem_matches(TERRITORY_ID)

        print("<> <> done <> <>")

    else:
        print("## ## no territory id entered! ## ##")
        print("try again (e.g. python app/gather_address.py 25C1)")
