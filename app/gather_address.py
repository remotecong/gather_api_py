""" actually does the lookups """
import re
import sys
from mongo import (get_ungathered_address_for,
                   get_gather_address,
                   add_owner_data,
                   change_address_and_add_owner_data,
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
        raise ThatsThemNoDataException("no owner at {}".format(gather_address))

    # filter all thatsthem data for last_name
    lname_re = re.compile("{}( jn?r| sn?r| ii| iii)?$".format(last_name), re.IGNORECASE)
    phone_numbers = []
    for thatsthem in thatsthem_data:
        if lname_re.search(thatsthem["name"]):
            thats_them_match_count += 1
            phone_numbers = phone_numbers + thatsthem["numbers"]
    if thats_them_match_count == 0 and ("skip_no_match" not in doc or not doc["skip_no_match"]):
        print("### I thought the last name was {}".format(first_piece_of_name))
        print("### (technically I thought it was {})".format(last_name))
        print("### because the full name is {}\n".format(name))
        for thatsthem in thatsthem_data:
            print("and {} doesn't match {}".format(first_piece_of_name, thatsthem["name"]))
        print("""\n### but I can't find a match in ThatsThem
              so do you want to
              (f)ix name, (m)ove on, or (c)onfirm no match?""")
        action = input("(f/m/c): ")
        if action == "f":
            """
                make shallow doc copy
                just take _id
                add ownerLivesThere: True
                add ownerName: input("New Last Name: ")
                then just return self(shallow_copy_doc, thatsthem_data)
            """
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

DOCS = get_ungathered_address_for(TERR)
if DOCS:
    for doc in DOCS:
        gather_address = get_gather_address(doc["address"])
        try:
            assessor_data = get_owner_data(gather_address)
            add_owner_data(doc, assessor_data)
        except Exception as e:
            print("=== {}".format(doc["address"]))
            if input("Assessor couldn't find address, change address? (y/n)") == "y":
                print("old address: {}".format(doc["address"]))
                new_address = input("new address: ")
                gather_address = get_gather_address(new_address)
                assessor_data = get_owner_data(gather_address)
                change_address_and_add_owner_data(doc, new_address, assessor_data)
            else:
                print("ERROR ==> {}".format(e))

DOCS = get_docs_without_phone_num_but_ttd(TERR)
if DOCS:
    for doc in DOCS:
        add_phone_data(doc, compile_final_doc(doc, doc["thatsThemData"]))

DOCS = get_addresses_without_thatsthem_data(TERR)
if DOCS:
    for doc in DOCS:
        if "ownerLivesThere" in doc:
            try:
                gather_address = get_gather_address(doc["address"])
                thatsthem_data = get_phone_numbers(gather_address)
                add_phone_data(doc, compile_final_doc(doc, thatsthem_data))
            except ThatsThemNoDataException as no_data:
                add_phone_data(doc, {
                    "thatsThemData": thatsthem_data,
                    "phoneNumbers": [],
                    "name": "Current Resident",
                    "skip_no_match": True,
                    })
        else:
            print(">>> No Assessor data found for {}".format(doc["address"]))

print("<> <> done <> <>")
