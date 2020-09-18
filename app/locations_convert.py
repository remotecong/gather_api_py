""" territory helper locations converter """
import sys
import pandas as pd
from mongo import add_address, doc_already_exists
from geo_json import find_acct_num

DATA = pd.read_excel("sample.xlsx")

TARGET_TERR = sys.argv[1]

ROW_COUNT = DATA.shape[0]

def get_new_docs(all_docs):
    """ filter out and give back docs to be added """
    for doc in all_docs:
        coords = doc.get("coords")
        if not doc_already_exists({"coords": coords}):
            acct_num = find_acct_num(coords)
            if acct_num:
                doc["assessorAccountNumber"] = acct_num
            yield doc


if ROW_COUNT > 0:
    print("Loading Territory {}\n{} total Locations across all territories.".format(TARGET_TERR, ROW_COUNT))
    to_be_added = []
    for r in range(ROW_COUNT):
        terr = DATA.at[r, "Territory number"]
        if terr == TARGET_TERR:
            to_be_added.append({
                "address": DATA.at[r, "Address"],
                "doNotCall": DATA.at[r, "Status"] == "Do not call",
                "coords": [DATA.at[r, "Latitude"], DATA.at[r, "Longitude"]],
            })
    print("Found {} locations from spreadsheet for {}. Going to add them to database (if needed.)".format(len(to_be_added), TARGET_TERR))
    added_count = 0
    for doc in get_new_docs(to_be_added):
        add_address(terr, doc)
        added_count = added_count + 1
    print("Added {} locations".format(added_count))
