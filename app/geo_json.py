#!/usr/bin/env python
import sys
import json

from shapely.geometry import Point
from shapely.geometry.polygon import Polygon

from geocode import find_coords_by_bad_address
from mongo import add_phone_data, delete_doc, get_docs_without_coords

def geo_jsons():
    """ paths """
    return [
        "8314.geojson",
        "8315.geojson",
        "8316.geojson",
        "8317.geojson",
        "8318.geojson",
        "8320.geojson",
        "8321.geojson",
        "8322.geojson",
        "8323.geojson",
        "8324.geojson",
        "8325.geojson",
        "8326.geojson",
        "8327.geojson",
        "8328.geojson",
        "8329.geojson",
        "8333.geojson",
        "8334.geojson",
        "8335.geojson",
        "8336.geojson",
        "8419.geojson",
        "8430.geojson",
        "8431.geojson",
    ]

def get_geojson(path):
    """ load up geojson """
    with open(path, "r") as fh:
        geo = json.loads(fh.read())
        return geo.get("features", [])
    return []

def get_polys(features):
    """ polygon getter generator """
    for feat in features:
        coords = feat.get("geometry", {}).get("coordinates", None)
        if coords and len(coords) == 1:
            yield (Polygon(coords[0]), feat.get("properties", {}).get("ACCOUNTNO", ""))

def get_all_geos():
    """ try and load all geos """
    for path in geo_jsons():
        for feat in get_geojson(path):
            yield feat

def find_acct_num(coords):
    """ find acct_num from geojsons """
    point = Point(coords[1], coords[0])
    for poly, acct_num in get_polys(get_all_geos()):
        if poly.contains(point):
            return acct_num
    return None

if __name__ == "__main__":
    lines = []
    for doc in get_docs_without_coords():
        if not find_coords_by_bad_address(doc["address"]):
            if "assessorAccountNumber" not in doc and "ownerName" not in doc and "phoneNumbers" not in doc:
                delete_doc(doc)
            else:
                lines.append("{} `{}` `{}` {}".format(doc["territoryId"], doc["_id"], doc["address"], doc.get("assessorAccountNumber", "??")))
    for l in sorted(lines):
        print(l)
