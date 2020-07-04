""" checks for po box addresses """
import re

UPS_BOXES = ("11063-D S MEMORIAL", "6528 E 101ST ST STE D")

POBOX_RE = re.compile(r'PO BOX', flags=re.IGNORECASE)

def is_po_box(address):
    """ is this address a po box or known UPS box """
    if POBOX_RE.search(address):
        return True
    for box in UPS_BOXES:
        if box in address:
            return True
    return False


if __name__ == '__main__':
    print(is_po_box('11063-d s meMorial ave, Tulsa, OK'))
