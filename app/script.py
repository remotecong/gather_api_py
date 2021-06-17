""" thats them parser """
import re
import requests
from bs4 import BeautifulSoup
import pydash


""" translate address to thatsthem url """
def get_url(address):
    q = re.sub(r'\s#\d+', '', address)
    q = re.sub(r'\.', '', q)
    q = re.sub(',? ', '-', q)
    return 'https://thatsthem.com/address/' + q


def get_phone_numbers(address):
    url = get_url(address)
    with requests.Session() as s:
        r = s.get(
            url,
            headers={
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:74.0) Gecko/20100101 Firefox/74.0',
            }
        )
        return parse_html(r.text)


def parse_html(html):
    soup = BeautifulSoup(html, 'html.parser')
    rows = soup.select('.ThatsThem-people-record.row')
    return [parse_row(r) for r in rows]


def parse_row(row):
    return {
        'name': row.find('h2').text.strip(),
        'numbers': [get_phone_number(p) for p in row.find_all(itemprop='telephone')],
    }


def get_phone_number(elem):
    return elem.text.strip()


if __name__ == '__main__':
    import sys
    for line in sys.stdin:
        name, address = line.split("\t")
        if re.search("^[^,],.*", name):
            last_name = name.split(",")[0].lower()
        else:
            last_name = re.sub(" or cr$", "", name, flags=re.I).split(" ")[-1].strip().lower()
        if address:
            details = get_phone_numbers(address)
            if details and len(details):
                phones = []
                for detail in details:
                    if last_name in detail['name'].lower():
                        phones = phones + detail['numbers']
                if 0 < len(phones):
                    print(", ".join(phones[0:2]))
                else:
                    print("No Number Found")
            else:
                print("no results at all")
        else:
            print("no address")
