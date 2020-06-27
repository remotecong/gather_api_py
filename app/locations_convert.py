""" territory helper locations converter """
import pandas as pd
import usaddress

DATA = pd.read_excel("sample.xlsx")

KEYS_WE_CARE_ABOUT = ("Territory number", "Address")

ROW_COUNT = DATA.shape[0]
if ROW_COUNT > 0:
    for r in range(ROW_COUNT):
        addr = usaddress.tag(DATA.at[r, "Address"])[0]
        terr = DATA.at[r, "Territory number"]
        gatherable_addr = "{} {} {} {}, {}, {}".format(
            addr["AddressNumber"],
            addr["StreetNamePreDirectional"],
            addr["StreetName"],
            addr["StreetNamePostType"],
            addr["PlaceName"],
            addr["StateName"]
        )
        print("T{} --> {}".format(terr, gatherable_addr))
