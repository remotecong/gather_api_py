""" get tulsa assessor data """
from bs4 import BeautifulSoup
from .get_last_name import get_last_name
from .po_boxes import is_po_box


def get_owner_data(html):
    """ parses owner data from assessor html """
    soup = BeautifulSoup(html, "html.parser")
    homestead = False
    doc = soup.select("#adjustments tbody tr td:first-child")

    for elem in doc:
        if elem.string == "Homestead":
            # go to <tr>, get last child, get first child's type
            last_cell_type = type(elem.parent.contents[-1].contents[0]).__name__
            # if homestead:true, there'll be an <img> else it's a str
            homestead = last_cell_type == "Tag"
            break

    # check mailing address and name
    mailing_address = None
    owner_name = None
    doc = soup.select("#general td")
    for elem in doc:
        if elem.string == "Owner mailing address":
            try:
                mailing_address = ", ".join([
                    elem.next_sibling.contents[0],
                    elem.next_sibling.contents[2]
                ]).strip()
            except:
                mailing_address = elem.next_sibling.get_text()
        elif elem.string == "Owner name":
            owner_name = elem.next_sibling.string.strip()

    # situs address to see if it's in mailing_address
    house_number = ''
    acct_num = None
    doc = soup.select("#quick td")

    for elem in doc:
        if elem.string == "Account #":
            acct_num = elem.next_sibling.contents[0]
        if elem.string == "Situs address":
            try:
                house_number = elem.next_sibling.contents[1].split()[0]
            except IndexError:
                pass
            break

    # does owner live there?
    if not house_number and mailing_address:
        house_number = mailing_address.split()[0]
    lives_there = house_number and ( \
            (house_number and house_number in mailing_address) or \
            (homestead and is_po_box(mailing_address)))

    # return results
    return {
        "account_number": acct_num,
        "homestead": homestead,
        "mailing_address": mailing_address,
        "owner_name": owner_name,
        "lives_there": lives_there,
        "last_name": get_last_name(owner_name),
        "assessor_house_number": house_number,
    }

if __name__ == "__main__":
    import json

    with open("assessor.html", "r") as f:
        d = get_owner_data(f.read())
        with open("data.json", "w") as j:
            json.dump(d, j)
            print(d)


