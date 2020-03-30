import requests
import re
from bs4 import BeautifulSoup


def get_url(address):
    q = re.sub(r'\s#\d+', '', address)
    q = re.sub(r'\.', '', q)
    q = re.sub(',? ', '-', q)
    return 'https://thatsthem.com/address/' + q


def get_phone_numbers(address):
    url = get_url(address)
    r = requests.get(
            url,
            headers={
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:74.0) Gecko/20100101 Firefox/74.0',
            }
        )
    return parse_html(r.text)


def parse_html(html):
    soup = BeautifulSoup(html, 'html.parser')
    rows = soup.select('.ThatsThem-people-record.row')
    return list(map(parse_row, rows))


def parse_row(row):
    return {
        'name': row.find('h2').text.strip(),
        'numbers': [get_phone_number(e) for e in row.find_all(itemprop='telephone')],
    }


def get_phone_number(elem):
    return {
        'number': elem.text.strip(),
        'is_mobile': elem.parent['data-title'] == 'Mobile',
    }


if __name__ == '__main__':
    with open('tt.html', 'r') as f:
        print(parse_html(f.read()))
