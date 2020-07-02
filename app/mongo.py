""" database entrypoint """
from datetime import datetime
import os
from os.path import join, dirname
import sys
from dotenv import load_dotenv
from pymongo import MongoClient
import usaddress

DOT_ENV = join(dirname(dirname(__file__)), '.env')
load_dotenv(DOT_ENV)


CLIENT = MongoClient(os.getenv("MONGO_URI"))
DB = CLIENT.db
if not DB:
    print("NO DB!")
    sys.exit(1)

ADDR = DB.address

def add_address(territory_id, doc):
    """ add address to collection it ain't already there """
    doc.update({"territoryId": territory_id})
    if not ADDR.find_one(doc):
        addr_pieces = usaddress.tag(doc["address"])[0]
        doc["street"] = " ".join((
            addr_pieces["StreetNamePreDirectional"],
            addr_pieces["StreetName"],
            addr_pieces["StreetNamePostType"]
        ))
        ADDR.insert(doc)

def change_address_and_add_owner_data(doc, address, owner_data):
    """ updates wrong address and adds assessor results """
    addr_pieces = usaddress.tag(address)[0]
    updates = {
        "lastUpdate": datetime.now(),
        "ownerName": owner_data["owner_name"],
        "ownerLivesThere": owner_data["lives_there"],
        "address": address,
        "street": " ".join((
            addr_pieces["StreetNamePreDirectional"],
            addr_pieces["StreetName"],
            addr_pieces["StreetNamePostType"]
        ))
    }
    ADDR.update_one(doc, {"$set": updates})


def get_ungathered_address_for(territory_id):
    """ find all addresses without gather details """
    return ADDR.find({"territoryId": territory_id, "ownerName": None}, batch_size=10)

def get_addresses_without_thatsthem_data(territory_id):
    """ find all address without thatsthem data """
    return ADDR.find({"territoryId": territory_id, "thatsThemData": None})

def get_docs_without_phone_num_but_ttd(territory_id):
    """ find all docs with thatsthem data but no phones """
    return ADDR.find({
        "territoryId": territory_id,
        "$and": [
            {"phoneNumbers": {"$exists": True}},
            {"phoneNumbers": {"$size": 0}},
            {"skip_no_match": {"$exists": False}},
            {"overrideLastName": {"$exists": False}},
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
    ADDR.update_one({"_id": doc["_id"]}, {
        "$set": updates
        })

def get_all_docs_for(territory_id):
    """ get all docs for a given territory """
    return ADDR.find({"territoryId": territory_id})
