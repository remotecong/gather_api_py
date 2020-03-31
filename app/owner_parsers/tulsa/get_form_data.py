import re

Streets = {
    'street': 'ST',
    'avenue': 'AV',
    'place': 'PL',
    'road rd': 'RD',
    'court ct': 'CT',
    'circle cr': 'CR',
    'drive': 'DR',
    'lane ln': 'LN',
    'park pr pk': 'PK',
    'boulevard blvd': 'BV',
    'expressway expwy': 'EX',
    'highway hwy': 'HY',
    'terrace tr': 'TE',
    'trail tl': 'TL',
    'way wy': 'WY',
}


class BadAddressException(Exception):
    pass


def get_form_data(address):
    try:
        # remove apt numbers and chop every after first comma
        clean_addr = re.sub(r'\s#\d+', '', address).split(',')[0].strip()
        # remove all periods
        clean_addr = re.sub(r'\.', '', clean_addr)
        # remove any directional suffixes
        clean_addr = re.sub(' [NEWS]$', '', clean_addr)

        matches = re.search(r'(\d+) ([NSEW]) ([\w\s]+) ([NSEW]\s)?([A-Za-z]+)( [NSEW])?$', clean_addr)

        # defaulting to street if we can't find a match
        streettype = 'ST'
        for options, val in Streets.items():
            if matches.group(5).lower() in options:
                streettype = val
                break

        return {
            'ln': '',
            'fn': '',
            'srchbox': 'on',
            'streetno': matches.group(1),
            'predirection': matches.group(2),
            'streetname': re.sub(' [NEWS]$', '', matches.group(3)),
            'streettype': streettype,
            'subaddr': 'Search+by+address',
            'subdivname': '',
            'subdivnum': '',
            'subdivlot': '',
            'subdivblk': '',
            'account': '',
            'parcel': '',
            'accepted': 'accepted',
        }
    except:
        raise BadAddressException('address parse failed. input: ' + address)


if __name__ == '__main__':
    import os
    print(get_form_data(os.environ['TEST_ADDR']))
