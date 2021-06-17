""" scrape thatsthem """
import re
from bs4 import BeautifulSoup
import pydash
from requests_futures.sessions import FuturesSession


def get_url(address):
    """ parse address into url """
    q = re.sub(r'\s#\d+', '', address)
    q = re.sub(r'\.', '', q)
    q = re.sub(',? ', '-', q)
    return 'https://thatsthem.com/address/' + q


def get_phone_numbers(address):
    """ scrape thatsthem """
    url = get_url(address)
    with FuturesSession() as s:
        r = s.get(
            url,
            headers={
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:74.0) Gecko/20100101 Firefox/74.0',
            }
        )
        print("--- {} ---".format(address))
        return parse_html(r.result().text)

class ThatsThemPhpException(Exception):
    """ when we hit php fatal error """

class ThatsThemNoMatchException(Exception):
    """ when we don't have any address matches """

class ThatsThemRateLimitException(Exception):
    """ rate limit hit """

def parse_html(html):
    """ parse response into usable data """
    soup = BeautifulSoup(html, 'html.parser')
    rows = soup.select('.ThatsThem-people-record.row')

    # check for rate limits
    if re.search(r'(exceeded the maximum number of queries|<h1>403 Forbidden</h1>)', html):
        raise ThatsThemRateLimitException
    if re.search(r'<b>Fatal error</b>', html):
        raise ThatsThemPhpException
    if re.search(r'We did not find any results for your query', html):
        # this is a valid response, but we may need to debug if address is malformed
        # if it happens repeatedly
        raise ThatsThemNoMatchException

    return list(parse_rows(rows))

def parse_rows(rows):
    """ convert data """
    for row in rows:
        name = row.find('h2').text.strip()
        for elem in row.find_all(itemprop="telephone"):
            yield get_phone_number(name, elem)


def get_phone_number(name, elem):
    """ individual data conversion """
    return {
        "name": name,
        'number': elem.text.strip(),
        'is_mobile': pydash.get(elem, 'parent.data-title') == 'Mobile',
    }


if __name__ == '__main__':
    with open('tt.html', 'r') as f:
        print(parse_html(f.read()))
