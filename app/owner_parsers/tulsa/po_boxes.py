import re

UPS_BOXES = ("11063-D S MEMORIAL", "6528 E 101ST ST STE D")

def is_po_box(address):
    a = address.upper()

    if re.search('PO BOX', a):
        return True

    for box in UPS_BOXES:
        if box in a:
            return True

    return False


if __name__ == '__main__':
    print(is_po_box('11063-d s meMorial ave, Tulsa, OK'))
