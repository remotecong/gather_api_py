""" check disconnected numbers """
import os

from requests_futures.sessions import FuturesSession

def get_disconnected_manifest_url():
    """ find url for disconnected sheet """
    return os.getenv("DISCONNECTEDS_URL")


def fetch_all():
    """ loads all disconnected numbers """
    url = get_disconnected_manifest_url()
    with FuturesSession() as sess:
        tsv = sess.get(url)
        return [num.strip() for num in tsv.result().text.split("\n")]

cached_numbers = []

def is_disconnected(number):
    """ checks if number has been reported as disconnected """
    global cached_numbers
    if not cached_numbers:
        cached_numbers = fetch_all()
    return number in cached_numbers
