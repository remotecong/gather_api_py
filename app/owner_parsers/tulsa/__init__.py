""" tulsa assessor lookup """
import re

from requests_futures.sessions import FuturesSession

from .get_form_data import get_form_data
from .get_owner_data import get_owner_data


def fetch_owner_data(address):
    """ make assessor request and parse response """
    form_data = get_form_data(address)

    with FuturesSession() as ses:
        # updated browser
        ses.headers.update({
            "User-Agent": " ".join([
                "Mozilla/5.0 (Macintosh; Intel Mac OS X",
                "10.15; rv:77.0) Gecko/20100101 Firefox/77.0",
            ])
        })

        req = ses.post(
            "https://assessor.tulsacounty.org/assessor-property-view.php",
            data=form_data
        )

        html = req.result().text

        goto_link = get_goto_link(html)
        if goto_link:
            with open("temp.html", "w") as f:
                f.write(html)
            print("GOTO LINK: " + goto_link)
            req = ses.get("https://assessor.tulsacounty.org/" + goto_link)

        return get_owner_data(req.result().text)


def fetch_owner_data_from_permalink(url):
    """ save assessor permalinks and refetch data from hardcoded URLS """
    with FuturesSession() as ses:
        # updated browser
        ses.headers.update({
            "User-Agent": " ".join([
                "Mozilla/5.0 (Macintosh; Intel Mac OS X",
                "10.15; rv:77.0) Gecko/20100101 Firefox/77.0",
            ])
        })
        req = ses.get(url)
        return get_owner_data(req.result().text)


def get_goto_link(html):
    """ quick parse to find goto link for multi results """
    if re.search(r'Click on a line to see the details for that property', html):
        match = re.search(r'goto="([^"]+)"', html)
        return re.sub(r'amp;', '', match[1])
    return None


if __name__ == "__main__":
    with open("multiresult-assessor.html", "r") as f:
        test_goto_link = get_goto_link(f.read())
        print(test_goto_link)
