import requests
from bs4 import BeautifulSoup
from get_form_data import get_form_data

def bs(html):
    return BeautifulSoup(html, 'html.parser')


def fetch_owner_data(address):
    # prep data first so we don't make request if we can't understand
    # the address
    data = get_form_data(address)

    with requests.Session() as s:
        # updated browser
        s.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:74.0) Gecko/20100101 Firefox/74.0',
        })

        r = s.post('https://assessor.tulsacounty.org/assessor-property-view.php', data=data)
        return parse_owner_data(r.text)


def parse_owner_data(html):
    soup = bs(html)

    # check homstead
    homestead = False
    q = soup.select('#adjustments tbody tr td:first-child')
    for el in q:
        if el.string == 'Homestead':
            homestead = len(el.next_sibling.contents) > 0

    # check mailing address and name
    mailing_address = None
    owner_name = None
    q = soup.select('#general td')
    for el in q:
        if el.string == 'Owner mailing address':
            mailing_address = f"{el.next_sibling.contents[0]}, {el.next_sibling.contents[2]}"
        elif el.string == 'Owner name':
            owner_name = el.next_sibling.string

    # return results
    return { 'homestead': homestead, 'mailing_address': mailing_address, 'owner_name': owner_name }


if __name__ == '__main__':
    import os
    print(fetch_owner_data(os.environ['TEST_ADDR']))
