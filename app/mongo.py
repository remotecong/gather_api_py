""" database entrypoint """
from datetime import datetime
import os
from os.path import join, dirname
import sys
from dotenv import load_dotenv
from pymongo import MongoClient

from addresses import get_street

DOT_ENV = join(dirname(dirname(__file__)), '.env')
load_dotenv(DOT_ENV)


CLIENT = MongoClient(os.getenv("MONGO_URI"))
DB = CLIENT.db
if not DB:
    print("NO DB!")
    sys.exit(1)

ADDR = DB.address

class CoordsMissingException(Exception):
    """ no coords? """

def add_address(territory_id, doc):
    """ add address to collection it ain't already there """
    if "coords" in doc:
        if not ADDR.find_one({"coords": doc["coords"]}):
            doc.update({"territoryId": territory_id})
            doc["street"] = get_street(doc["address"])
            ADDR.insert(doc)
    else:
        raise CoordsMissingException


def doc_already_exists(doc):
    """ check if doc exists """
    return ADDR.find_one(doc)


def change_address_and_add_owner_data(doc, address, owner_data):
    """ updates wrong address and adds assessor results """
    updates = {
        "assessorAccountNumber": owner_data.get("account_number", None),
        "lastUpdate": datetime.now(),
        "ownerName": owner_data["owner_name"],
        "ownerLivesThere": owner_data["lives_there"],
        "address": address,
        "street": get_street(address),
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
            {"thatsThemData": {"$exists": True, "$ne": []}},
        ]
    })


def delete_doc(doc):
    """ erase a doc permanently """
    ADDR.delete_one({"_id": doc["_id"]})


def find_docs_like(example):
    """ generic search method """
    if example:
        return ADDR.find(example, batch_size=10)
    return []


def get_docs_without_coords():
    """ TEMP function to fix up missing coords """
    return ADDR.find({
        "coords": None,
    }, batch_size=10)


def add_owner_data(doc, owner_data):
    """ patch in owner_data """
    updates = {
        "assessorAccountNumber": owner_data.get("account_number", None),
        "lastUpdate": datetime.now(),
        "ownerName": owner_data["owner_name"],
        "ownerLivesThere": owner_data["lives_there"]
    }
    house_num = owner_data.get("assessor_house_number", None)
    if house_num and "address" in doc and doc["address"].find(house_num) != 0:
        updates["houseNumConflict"] = house_num
    ADDR.update_one(doc, {"$set": updates})

def add_assessor_id(doc, assessor_id):
    """ patch in assessor ID """
    ADDR.update_one(doc, {
        "$set": {
            "assessorAccountNumber": assessor_id,
            "lastUpdate": datetime.now(),
        },
    })

def add_phone_data(doc, updates):
    """ patch in owner_data """
    updates["lastUpdate"] = datetime.now()
    ADDR.update_one({"_id": doc["_id"]}, {
        "$set": updates
        })


def get_all_printable_docs_for(territory_id):
    """ get all docs for a given territory """
    return ADDR.find({"territoryId": territory_id, "ownerLivesThere": {"$exists": True}})


def get_all_docs_for(territory_id):
    """ get all docs for a given territory """
    return ADDR.find({"territoryId": territory_id})


def get_all_docs():
    """ get every doc """
    return ADDR.find({
        "thatsThemData": None,
        "assessorAccountNumber": None,
    }, batch_size=10)

def find_bad_address():
    """ temp method for broken addresses """
    return ADDR.find({
        "territoryId": "25A",
        "street": "101st Pl",
    })
