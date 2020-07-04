""" actually does the lookups """
import re
import sys
from mongo import (
    get_ungathered_address_for,
    add_owner_data,
    change_address_and_add_owner_data,
    get_addresses_without_thatsthem_data,
    get_docs_without_phone_num_but_ttd,
    add_phone_data
)
from addresses import get_gather_address, get_verbose_address
from geocode import find_location_by_bad_address
from owner_info import get_owner_data
from owner_parsers.tulsa import fetch_owner_data_from_permalink
from thatsthem import get_phone_numbers, ThatsThemNoMatchException


class ThatsThemNoDataException(Exception):
    """ custom error for thatsthem errors """

def phone_number_sort(rec):
    """ prep phone numbers for sorting tulsa numbers first """
    if rec["number"].startswith("918-"):
        return 0
    return 1

def compile_final_doc(doc, thatsthem_data, ignore_no_data=False):
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
    if thats_them_match_count == 0 and ("skip_no_match" not in doc or not doc["skip_no_match"]):
        assessor_acct_num = doc.get("assessorAccountNumber", None)
        if assessor_acct_num:
            url = "https://www.assessor.tulsacounty.org/assessor-property.php" + \
                "?account={}&go=1".format(assessor_acct_num)
            print(url)
        print("### I thought the last name was {}".format(first_piece_of_name))
        print("### (technically I thought it was {})".format(last_name))
        print("### because the full name is {}\n".format(name))
        for thatsthem in thatsthem_data:
            print("* {}".format(thatsthem["name"]))
        print("\n### but I can't find a match in ThatsThem so do you want to")
        print("(f)ix name, (m)ove on, (c)onfirm no match, or (q)uit?")
        action = input("f/m/c/q: ")
        if action == "q":
            raise Exception("Goodbye!")
        if action == "f":
            shallow_doc = {
                "_id": doc["_id"],
                "ownerLivesThere": True,
                "overrideLastName": input("New Last Name: "),
                "originalName": name
            }
            return compile_final_doc(shallow_doc, thatsthem_data)
        return {
            "name": name,
            "phoneNumbers": phone_numbers,
            "thatsThemData": thatsthem_data,
            "skip_no_match": action.strip().lower() == "c"
        }
    phone_numbers.sort(key=phone_number_sort)
    if has_override_name:
        return {
            "name": doc["originalName"],
            "phoneNumbers": phone_numbers,
            "thatsThemData": thatsthem_data,
            "overrideLastName": doc["overrideLastName"],
        }
    return {
        "name": name,
        "phoneNumbers": phone_numbers,
        "thatsThemData": thatsthem_data,
    }

def get_assessor_data(territory_id):
    """ load assessor data for territory """
    docs = get_ungathered_address_for(territory_id)
    for doc in docs:
        get_assessor_data_for_doc(doc)

def get_assessor_data_for_doc(doc, override_address=None, tries=1):
    """ single assessor lookup """
    try:
        acct_num = doc.get("assessorAccountNumber", None)
        if acct_num:
            url = "https://www.assessor.tulsacounty.org/assessor-property.php" + \
                "?account={}&go=1".format(acct_num)
            print("\nAssessor Lookup with Permalink: {} --- ".format(url))
            assessor_data = fetch_owner_data_from_permalink(url)
        else:
            gather_address = get_gather_address(override_address or doc["address"])
            print("\nAssessor Lookup: {} --- ".format(gather_address))
            assessor_data = get_owner_data(gather_address)

        if override_address:
            print("\nAddress changed! Be sure to update TerritoryHelper")
            print("Search for: {}".format(doc["address"]))
            print("Change  to: {}".format(override_address))
            change_address_and_add_owner_data(doc, override_address, assessor_data)
        else:
            add_owner_data(doc, assessor_data)
        return assessor_data
    except TypeError as e:
        if tries > 2:
            print("\nThis address cannot be found!\n{}".format(doc["address"]))
            print(doc["address"])
            print(gather_address)
            print("\nWould you like to:\n(c)ontinue or (q)uit?")
            if input("c/q: ") == "q":
                raise Exception("Goodbye!")
        if tries > 1:
            print("No match on Assessor for -- {}".format(doc["address"]))
            print("(Searched for: {})".format(gather_address))
            if input("Assessor couldn't find address, change address? (y/n)") == "y":
                print("old address: {}".format(doc["address"]))
                new_address = input("new address: ").strip()
                get_assessor_data_for_doc(doc, new_address, tries+1)
            else:
                print("ERROR ==> {}".format(e))
        else:
            print("Assessor couldn't find {}".format(gather_address))
            print("So I'm going to try to get a new address from Google based on this house's GPS.")
            new_address = find_location_by_bad_address(doc["address"].split(",")[0])
            get_assessor_data_for_doc(doc, new_address, tries+1)
    except Exception as exc:
        print("#### DEBUG ASSESSOR EXCEPTION ####\n{}\n".format(exc))

def get_thatsthem_data(doc, override_address=None):
    """ put together thatsthem data """
    try:
        gather_address = override_address or get_gather_address(doc["address"])
        thatsthem_data = get_phone_numbers(gather_address)
        add_phone_data(doc, compile_final_doc(doc, thatsthem_data))

    except ThatsThemNoMatchException:
        if not override_address:
            verbose_address = get_verbose_address(doc["address"])
            return get_thatsthem_data(doc, verbose_address)

        print("\nThatsThem couldn't find a match for this address.")
        print("Would you like to try to search a slightly different address?")
        print("Official Address: {}".format(doc["address"]))
        print("Address Searched for on ThatsThem: {}\n".format(get_gather_address(doc["address"])))
        action = input("(n)ew address, (c)ontinue, or (q)uit: ")
        print("")
        if action == "n":
            new_addr = input("Enter address to use for ThatsThem: ")
            return get_thatsthem_data(doc, new_addr)
        if action == "q":
            raise Exception("Goodbye!")

        # give back empty result set
        add_phone_data(doc, compile_final_doc(doc, [], ignore_no_data=True))

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

def fetch_all_missing_thatsthem_data(territory_id):
    """ get fresh data from thatsthem for all docs in territory """
    for doc in get_addresses_without_thatsthem_data(territory_id):
        if "ownerLivesThere" in doc:
            get_thatsthem_data(doc)
        else:
            print(">>> No Assessor data found for {}".format(doc["address"]))
            print("Do you want to try getting Assessor data again then retry ThatsThem?")
            if input("y/n: ") == "y":
                assessor_data = get_assessor_data_for_doc(doc)
                get_thatsthem_data(doc.update(assessor_data), doc["address"])


if __name__ == "__main__":
    if len(sys.argv) > 1:
        TERRITORY_ID = sys.argv[1]
        get_assessor_data(TERRITORY_ID)
        finalize_pending_thatsthem_matches(TERRITORY_ID)
        fetch_all_missing_thatsthem_data(TERRITORY_ID)
    print("<> <> done <> <>")
