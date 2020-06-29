""" territory helper locations converter """
import pandas as pd
from mongo import add_address

DATA = pd.read_excel("sample.xlsx")

KEYS_WE_CARE_ABOUT = ("Territory number", "Address")

ROW_COUNT = DATA.shape[0]
if ROW_COUNT > 0:
    for r in range(ROW_COUNT):
        terr = DATA.at[r, "Territory number"]
        add_address(terr, DATA.at[r, "Address"])
