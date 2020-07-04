""" find last name from assessor data """
import re

def get_last_name(raw_name):
    """ try best guess of last name """
    lname = re.sub(r'( the| ttee| revocable| rev| trustee| trust| Living| \d+)', "", raw_name)
    lname = lname.split(',')[0].strip()

    if " " in lname:
        return re.match(r'^[^\s]+\s', lname)[0].strip()
    return lname


if __name__ == "__main__":
    print(get_last_name("DOE, JOHN S"))
