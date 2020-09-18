""" territory helper locations converter """
import sys
import pandas as pd

from mongo import add_address, doc_already_exists
from geo_json import find_acct_num


def get_new_docs(t_id):
    """ filter out and give back docs to be added """
    for doc in get_rows(t_id):
        coords = doc.get("coords")
        if not doc_already_exists({"coords": coords}):
            acct_num = find_acct_num(coords)
            if acct_num:
                doc["assessorAccountNumber"] = acct_num
            yield doc


def get_rows(t_id):
    """ loads up spreadsheet and yields rows """
    DATA = pd.read_excel("sample.xlsx")
    for r in range(DATA.shape[0]):
        if DATA.at[r, "Territory number"] == t_id:
            yield {
                "address": DATA.at[r, "Address"],
                "doNotCall": DATA.at[r, "Status"] == "Do not call",
                "coords": [DATA.at[r, "Latitude"], DATA.at[r, "Longitude"]],
                "territoryId": t_id,
            }


def load_territory(t_id):
    """ fetch all locations for a territory """
    added_count = 0
    for doc in get_new_docs(t_id):
        add_address(t_id, doc)
        added_count = added_count + 1
    return added_count


if __name__ == "__main__":
    TARGET_TERR = sys.argv[1]
    print("Loading Territory {}".format(TARGET_TERR))
    print("Added {} locations for {}.!".format(load_territory(TARGET_TERR), TARGET_TERR))
