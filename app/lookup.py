""" lookup aggregator """
import json
import redis
from .owner_info import get_owner_data
from .thatsthem import get_phone_numbers

R = redis.Redis(host='redis')

def get_first_non_owner_name(owner_lname, phones):
    """ determine last name for matching phones """
    for phone in phones:
        if owner_lname not in phone["name"]:
            return phone["name"]



def lookup(address):
    """ looks up address """

    cache = R.get(address)
    if cache:
        pass
        #return json.loads(cache)

    d = get_owner_data(address)
    phones = get_phone_numbers(address)
    result = {
        "livesThere": d["lives_there"],
        "lastName": d["last_name"],
        "ownerName": d["owner_name"],
        "mailingAddress": d["mailing_address"],
        "phones": []
    }

    # for easier searching
    last = d["last_name"].lower()
    if not d["lives_there"]:
        renter = get_first_non_owner_name(d["last_name"].lower(), phones)
        last = renter.split()[-1].lower()

    for p in phones:
        if last in p["name"].lower():
            result["phones"].append({"number": p["number"], "isMobile": p["is_mobile"]})



    R.set(address, json.dumps(result))
    # mailingAddress: from assessor
    # ownerName: raw
    # lastName: guessed last name
    # livesThere: boolean
    # thatsThemUrl: url
    # phones:
    #   name: if not livesthere
    #   number: phone
    #   isMobile: boolean
    return result
