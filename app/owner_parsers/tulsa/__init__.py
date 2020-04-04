from requests_futures.sessions import FuturesSession
from .get_form_data import get_form_data
from .get_owner_data import get_owner_data
from bs4 import BeautifulSoup

def bs(html):
    return BeautifulSoup(html, 'html.parser')


def fetch_owner_data(address):
    # prep data first so we don't make request if we can't understand
    # the address
    data = get_form_data(address)

    with FuturesSession() as s:
        # updated browser
        s.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:74.0) Gecko/20100101 Firefox/74.0',
        })

        r = s.post('https://assessor.tulsacounty.org/assessor-property-view.php', data=data)

        soup = bs(r.result().text)
        # check if multiple results are returned for given address
        q = soup.select('#pickone tr[goto]')

        if q:
            r = s.get(f"https://assessor.tulsacounty.org/{q[0]['goto']}")
            soup = bs(r.result().text)

        return get_owner_data(soup)



if __name__ == '__main__':
    import os
    print(fetch_owner_data(os.environ['TEST_ADDR']))
