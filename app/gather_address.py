""" actually does the lookups """
import re
import sys
from mongo import (get_ungathered_address_for,
                   get_gather_address,
                   add_owner_data,
                   get_addresses_without_thatsthem_data,
                   get_docs_without_phone_num_but_ttd,
                   add_phone_data)
from owner_info import get_owner_data
from thatsthem import get_phone_numbers

if len(sys.argv) != 2:
    raise ValueError("you need to include a territory id")

TERR = sys.argv[1]
print("finding addresses for {}".format(TERR))


class ThatsThemNoDataException(Exception):
    """ custom error for thatsthem errors """

def phone_number_sort(rec):
    """ prep phone numbers for sorting tulsa numbers first """
    if rec["number"].startswith("918-"):
        return 0
    return 1

def compile_final_doc(doc, thatsthem_data):
    # name for record
    name = None
    # last name for matching
    last_name = None
    first_piece_of_name = None
    thats_them_match_count = 0
    if doc["ownerLivesThere"]:
        name = doc["ownerName"]
        first_piece_of_name = name.split(",")[0].strip()
        #   allow matches for names including hyphens
        first_piece_of_name = re.sub(r'-', '-?', first_piece_of_name)
        last_name = re.sub(r' (TRUST|FAMILY|FAMILY TRUST|FAMILY REV TRUST|REV TRUST C/O.*)?$', '', first_piece_of_name, flags=re.IGNORECASE)
    elif len(thatsthem_data) > 0:
        name = thatsthem_data[0]["name"]
        last_name = name.split(" ")[-1]
    else:
        raise ThatsThemNoDataException("no owner at {}".format(gather_address))

    # filter all thatsthem data for last_name
    lname_re = re.compile("{}( jn?r| sn?r| ii| iii)?$".format(last_name), re.IGNORECASE)
    phone_numbers = []
    for thatsthem in thatsthem_data:
        if lname_re.search(thatsthem["name"]):
            thats_them_match_count += 1
            phone_numbers = phone_numbers + thatsthem["numbers"]
        else:
            print("{} !== {}".format(last_name, thatsthem["name"]))
    if thats_them_match_count == 0 and ("skip_no_match" not in doc or not doc["skip_no_match"]):
        print(doc["address"])
        print(" <== {} ==> {}".format(first_piece_of_name, name))
        print(lname_re)
        if input("move on? ") != "y":
            raise Exception("Sorry bud")
        return {
            "name": name,
            "phoneNumbers": phone_numbers,
            "thatsThemData": thatsthem_data,
            "skip_no_match": True
        }
    else:
        phone_numbers.sort(key=phone_number_sort)
    return {
        "name": name,
        "phoneNumbers": phone_numbers,
        "thatsThemData": thatsthem_data,
    }

DOCS = get_ungathered_address_for(TERR)
if DOCS:
    for doc in DOCS:
        print(doc)
        gather_address = get_gather_address(doc["address"])
        try:
            assessor_data = get_owner_data(gather_address)
            add_owner_data(doc, assessor_data)
        except Exception as e:
            print("ERROR ==> {}".format(e))

DOCS = get_docs_without_phone_num_but_ttd(TERR)
if DOCS:
    for doc in DOCS:
        add_phone_data(doc, compile_final_doc(doc, doc["thatsThemData"]))

DOCS = get_addresses_without_thatsthem_data(TERR)
if DOCS:
    for doc in DOCS:
        gather_address = get_gather_address(doc["address"])
        thatsthem_data = get_phone_numbers(gather_address)
        add_phone_data(doc, compile_final_doc(doc, thatsthem_data))

print("<> <> done <> <>")
