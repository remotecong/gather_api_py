""" script to prefetch all assessor datas! """
import sys
import signal
import logging
import pandas as pd
from mongo import add_address, doc_already_exists
from owner_parsers.tulsa import fetch_owner_data_from_permalink
from geo_json import find_acct_num

counter = 0

def keyboardInterruptHandler(signal, frame):
    """ gracefully shutdown? """
    print_counter()
    exit(0)

def print_counter():
    """ print counter out """
    print("Added {} locations!".format(counter))

signal.signal(signal.SIGINT, keyboardInterruptHandler)

if __name__ == "__main__":
    logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))
    # for each row in sample.xlsx
    # if not find_one({"coords": [row[lat], row[lng]]}):
        # if get_acct_num:
            # if get_owner_data:
                # save doc with owner_data
            # else:
                # save doc with num
        # else:
            # print something bad happened!
    DATA = pd.read_excel("sample.xlsx")

    ROW_COUNT = DATA.shape[0]
    if ROW_COUNT > 0:
        print("{} Locations found".format(ROW_COUNT))
        for r in range(ROW_COUNT):
            coords = [DATA.at[r, "Latitude"], DATA.at[r, "Longitude"]]
            doc = {
                "address": DATA.at[r, "Address"],
                "doNotCall": DATA.at[r, "Status"] == "Do not call",
                "coords": coords,
            }
            if not doc_already_exists({"coords": coords}):
                acct_num = find_acct_num(coords)
                if acct_num:
                    doc["assessorAccountNumber"] = acct_num
                    url = "https://www.assessor.tulsacounty.org/assessor-property.php" + \
                        "?account={}&go=1".format(acct_num)
                    try:
                        owner_data = fetch_owner_data_from_permalink(url)
                        if owner_data:
                            doc["ownerName"] = owner_data.get("owner_name")
                            doc["ownerLivesThere"] = owner_data.get("lives_there")
                            house_num = owner_data.get("assessor_house_number")
                            if house_num and doc["address"].find(house_num) != 0:
                                doc["houseNumConflict"] = house_num
                    except Exception as e:
                        print("### Bad dates ###\n{}\n{}\n".format(doc, e))
                add_address(DATA.at[r, "Territory number"], doc)
                print("+++ {}".format(doc))
                counter = counter + 1
        print_counter()
