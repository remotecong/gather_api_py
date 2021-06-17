"""
abstract handler for looking up addresses
"""
from owner_parsers.tulsa import fetch_owner_data

def get_owner_data(address):
    """ look up data from assessor """
    return fetch_owner_data(address)
