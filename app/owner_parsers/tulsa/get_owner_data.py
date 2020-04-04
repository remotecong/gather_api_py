from .po_boxes import is_po_box
from .get_last_name import get_last_name


def get_owner_data(soup):
    # check homstead
    homestead = False
    q = soup.select('#adjustments tbody tr td:first-child')
    for el in q:
        if el.string == 'Homestead':
            homestead = len(el.next_sibling.contents) > 0
            break

    # check mailing address and name
    mailing_address = None
    owner_name = None
    q = soup.select('#general td')
    for el in q:
        if el.string == 'Owner mailing address':
            mailing_address = f"{el.next_sibling.contents[0]}, {el.next_sibling.contents[2]}"
        elif el.string == 'Owner name':
            owner_name = el.next_sibling.string

    # situs address to see if it's in mailing_address
    house_number = ''
    q = soup.select('#quick td')
    for el in q:
        if el.string == 'Situs address':
            house_number = el.next_sibling.contents[1].split()[0]
            break

    # does owner live there?
    lives_there = house_number in mailing_address or \
            (homestead and is_po_box(mailing_address))

    # return results
    return {
        'homestead': homestead,
        'mailing_address': mailing_address,
        'owner_name': owner_name,
        'lives_there': lives_there,
        'last_name': get_last_name(owner_name),
    }

if __name__ == '__main__':
    import json

    with open('assessor.html', 'r') as f:
        d = get_owner_data(f.read())
        with open('data.json', 'w') as j:
            json.dump(d, j)
            print(d)


