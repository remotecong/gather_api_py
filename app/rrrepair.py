""" actually does the lookups """
import re
from mongo import (
    get_ungathered_address_for,
    add_owner_data,
    change_address_and_add_owner_data,
    get_addresses_without_thatsthem_data,
    get_all_docs,
    add_phone_data
)
from addresses import get_gather_address, get_verbose_address
from geocode import find_location_by_bad_address
from owner_info import get_owner_data
from owner_parsers.tulsa import fetch_owner_data_from_permalink
from thatsthem import ThatsThemNoMatchException

class ThatsThemNoDataException(Exception):
    """ thatsthem has nothing for address """

def phone_number_sort(rec):
    """ prep phone numbers for sorting tulsa numbers first """
    if rec["number"].startswith("918-"):
        return 0
    return 1

def compile_final_doc(doc, thatsthem_data):
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
    else:
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
        print()
        if action == "q":
            raise Exception("Goodbye!")
        if action == "f":
            shallow_doc = {
                "_id": doc["_id"],
                "ownerLivesThere": True,
                "overrideLastName": input("New Last Name: ").strip(),
                "originalName": name
            }
            return compile_final_doc(shallow_doc, thatsthem_data)
        return {
            "name": doc.get("originalName", name),
            "phoneNumbers": phone_numbers,
            "thatsThemData": thatsthem_data,
            "skip_no_match": action.strip().lower() == "c"
        }
    phone_numbers.sort(key=phone_number_sort)
    return {
        "name": doc.get("originalName", name),
        "phoneNumbers": phone_numbers,
        "thatsThemData": thatsthem_data,
        "overrideLastName": doc.get("overrideLastName")
    }


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
                return get_assessor_data_for_doc(doc, new_address, tries+1)
            print("ERROR ==> {}".format(e))
        else:
            print("Assessor couldn't find {}".format(gather_address))
            print("So I'm going to try to get a new address from Google based on this house's GPS.")
            new_address = find_location_by_bad_address(doc["address"].split(",")[0])
            return get_assessor_data_for_doc(doc, new_address, tries+1)
    except Exception as exc:
        print("#### DEBUG ASSESSOR EXCEPTION ####\n{}\n".format(exc))


if __name__ == "__main__":
    for location in get_all_docs():
        print("## {}".format(location.get("_id")))

        owner = get_assessor_data_for_doc(location)
        continue

        location.update({
            "ownerName": owner["owner_name"],
            "ownerLivesThere": owner["lives_there"],
            "assessorAccountNumber": owner.get("account_number", None),
        })
        for key in ["skip_no_match", "overrideLastName", "phoneNumbers"]:
            location.pop(key, None)
        phone_updates = compile_final_doc(location, location["thatsThemData"])
        if phone_updates:
            add_phone_data(location, phone_updates)
    print("<> <> done <> <>")
