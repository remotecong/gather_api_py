""" address manipulation """
import re
import sys

import usaddress

DIRECTIONS = {
    "N": "North",
    "S": "South",
    "E": "East",
    "W": "West",
}

STREET_TYPE = {
    "Ave": "Avenue",
    "Blvd": "Boulevard",
    "Cir": "Circle",
    "Ct": "Court",
    "Dr": "Drive",
    "Hwy": "Highway",
    "Ln": "Lane",
    "Pl": "Place",
    "Rd": "Road",
    "St": "Street",
    "Wy": "Way",
}

def get_verbose_address(address):
    """ expand abbreviations from address pieces """
    pieces = usaddress.tag(address)[0]
    out = ""
    for key, piece in pieces.items():
        if key == "AddressNumber":
            out += piece
        elif key == "StreetNamePreDirectional":
            out += " {}".format(DIRECTIONS[piece])
        elif key in ["StreetName", "StateName"]:
            out += " {}".format(piece)
        elif key == "StreetNamePostType":
            out += " {}".format(STREET_TYPE[piece] or piece)
        elif key == "StreetNamePostDirectional":
            out += " {}".format(DIRECTIONS[piece])
        elif key == "PlaceName":
            out += ", {},".format(piece)
    return out

def get_street(address):
    """ get normalized street name string """
    pieces = usaddress.tag(address)[0]
    printed_pieces = []
    for key, piece in pieces.items():
        if key in ["StreetNamePostDirectional", "StreetNamePreDirectional"]:
            printed_pieces.append(piece[0])
        elif key == "StreetNamePostType":
            printed_pieces.append(piece[0:3])
        elif key == "StreetName":
            street = re.sub(r' North$', " N", piece)
            street = re.sub(r' South$', " S", piece)
            street = re.sub(r' East$', " E", piece)
            street = re.sub(r' West$', " W", piece)
            printed_pieces.append(street)
    return " ".join(printed_pieces)


def get_gather_address(address):
    """ get gather address from address """
    addr_pieces = usaddress.tag(address)[0]
    return "{} {} {} {}, {}, {}".format(
        addr_pieces["AddressNumber"],
        addr_pieces["StreetNamePreDirectional"],
        addr_pieces["StreetName"],
        addr_pieces["StreetNamePostType"],
        addr_pieces["PlaceName"],
        addr_pieces["StateName"]
        )

if __name__ == "__main__":
    if len(sys.argv) > 1:
        #print(get_verbose_address(sys.argv[1]))
        print(get_street(sys.argv[1]))
    else:
        TESTS = {
            "9505 E 117th Pl S, Bixby, OK": "9505 East 117th Place South, Bixby, OK",
            "123 W Main St, Bixby, OK": "123 West Main Street, Bixby, OK",
            "123 N Main St E, Bixby, OK": "123 North Main Street East, Bixby, OK",
        }
        for test, expected in TESTS.items():
            print("\n{}\n{}\n{}\n--------------------------------------------".format(
                test, get_verbose_address(test), expected
            ))
