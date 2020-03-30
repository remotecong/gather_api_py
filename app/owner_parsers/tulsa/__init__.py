from requests_futures.sessions import FuturesSession
from .get_form_data import get_form_data
from .get_owner_data import get_owner_data

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
        return get_owner_data(r.result().text)



if __name__ == '__main__':
    import os
    print(fetch_owner_data(os.environ['TEST_ADDR']))
