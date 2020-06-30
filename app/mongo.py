""" database entrypoint """
from datetime import datetime
from pymongo import MongoClient
import usaddress

CLIENT = MongoClient(port=27017)
DB = CLIENT.address_test
ADDR = DB.address_test

if not DB.fly_not_test:
    DB.create_collection("fly_not_test")

def add_address(territory_id, address):
    """ add address to collection it ain't already there """
    doc = {"territoryId": territory_id, "address": address}
    if not ADDR.find_one(doc):
        addr_pieces = usaddress.tag(address)[0]
        doc["street"] = " ".join((
            addr_pieces["StreetNamePreDirectional"],
            addr_pieces["StreetName"],
            addr_pieces["StreetNamePostType"]
        ))
        ADDR.insert(doc)

def get_ungathered_address_for(territory_id):
    """ find all addresses without gather details """
    return ADDR.find({"territoryId": territory_id, "ownerName": None})

def get_addresses_without_thatsthem_data(territory_id):
    """ find all address without thatsthem data """
    return ADDR.find({"territoryId": territory_id, "thatsThemData": None})

def get_docs_without_phone_num_but_ttd(territory_id):
    """ find all docs with thatsthem data but no phones """
    return ADDR.find({
        "territoryId": territory_id,
        "$and": [
            {"phoneNumbers": {"$exists": True}},
            {"phoneNumbers": {"$size": 0}}
        ]
    })

def add_owner_data(doc, owner_data):
    """ patch in owner_data """
    ADDR.update_one(doc, {
        "$set": {
            "lastUpdate": datetime.now(),
            "ownerName": owner_data["owner_name"],
            "ownerLivesThere": owner_data["lives_there"]
        }
        })

def get_gather_address(address):
    """ get gather address from address """
    addr_pieces = usaddress.tag(address)[0]
    return "{} {} {} {}, {}, {}".format(
        addr_pieces["AddressNumber"],
        addr_pieces["StreetNamePreDirectional"],
        addr_pieces["StreetName"],
        addr_pieces["StreetNamePostType"],
        addr_pieces["PlaceName"],
        addr_pieces["StateName"]
        )

def add_phone_data(doc, updates):
    """ patch in owner_data """
    updates["lastUpdate"] = datetime.now()
    ADDR.update_one(doc, {
        "$set": updates
        })

def get_all_docs_for(territory_id):
    """ get all docs for a given territory """
    return ADDR.find({"territoryId": territory_id})
