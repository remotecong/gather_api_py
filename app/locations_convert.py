""" territory helper locations converter """
import sys
import pandas as pd
from mongo import add_address

DATA = pd.read_excel("sample.xlsx")

TARGET_TERR = sys.argv[1]

ROW_COUNT = DATA.shape[0]
if ROW_COUNT > 0:
    print("Loading Territory {}\n{} Locations found.".format(TARGET_TERR, ROW_COUNT))
    for r in range(ROW_COUNT):
        terr = DATA.at[r, "Territory number"]
        if not TARGET_TERR or terr == TARGET_TERR:
            doc = {
                "address": DATA.at[r, "Address"],
                "doNotCall": DATA.at[r, "Status"] == "Do not call",
            }
            add_address(terr, doc)
