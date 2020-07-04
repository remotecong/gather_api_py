""" reverse geocode lat/lng for bad assessor addresses """
import os
from os.path import join, dirname
import re
import sys
from dotenv import load_dotenv
import pandas as pd
from requests_futures.sessions import FuturesSession

DOT_ENV = join(dirname(dirname(__file__)), '.env')
load_dotenv(DOT_ENV)

API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

def get_address(lat_lng):
    """ fetch results from google """
    url = "?".join((
        "https://maps.googleapis.com/maps/api/geocode/json",
        "key={}&latlng={}".format(API_KEY, lat_lng)
    ))
    print(lat_lng, file=sys.stderr)

    with FuturesSession() as s:
        r = s.get(
            url,
            headers={
                'User-Agent': " ".join((
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5)",
                    "AppleWebKit/537.36 (KHTML, like Gecko)",
                    "Chrome/83.0.4103.116 Safari/537.36"
                ))
            }
        )
        try:
            return print_replacement_address(r.result().json())
        except Exception as e:
            print("ERROR: {}".format(e), file=sys.stderr)
            print("latlng -----> {}".format(lat_lng), file=sys.stderr)
            print("url -----> {}".format(url), file=sys.stderr)
            print("json -----> {}".format(r.result().json()), file=sys.stderr)

def print_replacement_address(geocode_result):
    """ translate google geocode response into pasteable address """
    if "results" in geocode_result and len(geocode_result["results"]) > 0:
        addr_pieces = []
        for res in geocode_result["results"][0]["address_components"]:
            if "street_number" in res["types"] or \
                    "locality" in res["types"] or \
                    "administrative_area_level_1" in res["types"] or \
                    "postal_code" in res["types"]:
                addr_pieces.append(res["short_name"])

            elif "route" in res["types"]:
                cleaned = re.sub(r'^North ', 'N ', res["short_name"])
                cleaned = re.sub(r'^South ', 'S ', cleaned)
                cleaned = re.sub(r'^East ', 'E ', cleaned)
                cleaned = re.sub(r'^West ', 'W ', cleaned)
                addr_pieces.append(cleaned)
        #   google includes country before zip, but territory helper prefers it after
        addr_pieces.append("United States")
        number, street, city, state, postal_code, country = addr_pieces
        return "{} {}, {}, {} {}, {}".format(number, street, city, state, postal_code, country)
    return None

def find_location_by_bad_address(address):
    """ reverse spreadsheet search for bad address """
    data = pd.read_excel("sample.xlsx")
    rows = data.shape[0]
    for row in range(rows):
        if address in data.at[row, "Address"]:
            return get_address(
                ",".join([
                    str(data.at[row, "Latitude"]),
                    str(data.at[row, "Longitude"]),
                ])
            )
    return None

if __name__ == "__main__":
    if len(sys.argv) == 3:
        lat, lng = sys.argv[1:]
        print(get_address(",".join([lat,lng])))
    else:
        for line in sys.stdin:
            good_address = find_location_by_bad_address(line.strip())
            print(good_address)
