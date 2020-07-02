""" module to clean up names """
import re

MULTI_SPACE_RE = re.compile(r' +')
AND_RE = re.compile(r' and ', flags=re.IGNORECASE)
NON_NAME_PIECES = re.compile(
    r'(Jr|Co Trustees.*Trust|Rev Trusts?|' +
    r'Ttee.*|Revocable Trust|Trust)',
    flags=re.IGNORECASE
)

def squish(name):
    """ normalize spaces """
    name = NON_NAME_PIECES.sub('', name)
    name = AND_RE.sub(' & ', name)
    name = MULTI_SPACE_RE.sub(" ", name)
    return name.title().strip()


LAST_FIRST_RE = re.compile(r'^([A-Z-]+), ([A-Z\']+) ?[A-Z]*$', flags=re.IGNORECASE)

def last_first(name):
    """ LASTNAME, FIRSTNAME """
    match = LAST_FIRST_RE.match(name)
    if match:
        lname = clean_last_name(match[1])
        return "{} {}".format(match[2], lname)
    return None


MR_MRS_LAST_FIRST_RE = re.compile(
    r'^([A-Z-]+), ([A-Z\']+) ?[A-Z]* & ([A-Z]+) ?[A-Z]*$',
    flags=re.IGNORECASE
)

def mr_mrs_last_first(name):
    """ LASTNAME, NAME1 (M) & NAME2 (M) """
    match = MR_MRS_LAST_FIRST_RE.match(name)
    if match:
        lname = clean_last_name(match[1])
        return "{} & {} {}".format(match[2], match[3], lname)
    return None

MR_MRS_L_F_M_F_M_L_RE = re.compile(
    r'^([A-Z-]+), ([A-Z\']+) ?[A-Z]* & ([A-Z\']+) [A-Z] ([A-Z-]+)$',
    flags=re.IGNORECASE
)
def mr_mrs_last_first_last(name):
    """ LASTNAME, FIRST M & FIRST M LASTNAME """
    match = MR_MRS_L_F_M_F_M_L_RE.match(name)
    if match:
        lname1 = clean_last_name(match[1])
        lname2 = clean_last_name(match[4])
        return "{} {} & {} {}".format(match[2], lname1, match[3], lname2)
    return None


MAC_ATTACK_RE = re.compile(r'^(MA?C)([A-Z])(.*)', flags=re.IGNORECASE)

def clean_last_name(lname):
    """ special case handler for last names """
    match = MAC_ATTACK_RE.match(lname)
    if match:
        return match[1].title() + match[2].upper() + match[3]
    return lname


def pretty_print_name(name):
    """ try to clean up names """
    name = squish(name)
    return mr_mrs_last_first(name) or \
        mr_mrs_last_first_last(name) or \
        last_first(name) or \
        name

if __name__ == "__main__":
    TEST_NAMES = {
        "VAZQUEZ, WILMER": "Wilmer Vazquez",
        "SEGOVIA, JUAN MANUEL": "Juan Segovia",
        "ROBINSON, CHRISTOPHER CHARLES & CYNTHIA NUNES": "Christopher & Cynthia Robinson",
        "SMITH, JESSICA T AND DEBRA A": "Jessica & Debra Smith",
        "SOLOMON, SAMANTHA A & BRUCE O JR": "Samantha & Bruce Solomon",
        "OLZAWSKI, ELAINE A REVOCABLE TRUST": "Elaine Olzawski",
        "AL-TAMEEMI, KHALID": "Khalid Al-Tameemi",
        "GUSANU, MATILDA F AND DAMILOLA V SIAKA-STEVEN": "Matilda Gusanu & Damilola Siaka-Steven",
        "CARDENAS, EDUARDO JR AND CATHERINE J": "Eduardo & Catherine Cardenas",
        "COLLINS, DAVID M TRUST": "David Collins",
        "BOYLES, CAROL D & DAWN M MARTIN": "Carol Boyles & Dawn Martin",
        "HETHERINGTON, JAMES D JR & ANN M WAYLAND": "James Hetherington & Ann Wayland",
        "KRAMER, ROBERT S TTEE ROBERT S KRAMER": "Robert Kramer",
    }

    for test, expected in TEST_NAMES.items():
        print("-------------------------------------------------")
        actual = pretty_print_name(test)
        matches = actual == expected
        emoji = "💥" if not matches else "💅"
        print("{} --> {}".format(emoji, actual))
        print("{} <-- {}".format(emoji, test))
        if not matches:
            print("{} !== {}".format(emoji, expected))
