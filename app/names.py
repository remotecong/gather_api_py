""" module to clean up names """
import re

MULTI_SPACE_RE = re.compile(r'\\s+')

def squish(name):
    """ normalize spaces """
    return MULTI_SPACE_RE.sub(" ", name).strip()

LAST_FIRST_RE = re.compile(r'^([A-Z]+), ([A-Z\']+) ?[A-Z]*$', flags=re.IGNORECASE)

def last_first(name):
    """ LASTNAME, FIRSTNAME """
    match = LAST_FIRST_RE.match(name)
    if match:
        lname = clean_last_name(match[1])
        return "{} {}".format(match[2], lname)
    return None

MR_MRS_LAST_FIRST_RE = re.compile(r'^([A-Z]+), ([A-Z\']+) ?[A-Z]* & ([A-Z]+) ?[A-Z]*$', flags=re.IGNORECASE)
def mr_mrs_last_first(name):
    """ LASTNAME, NAME1 (M) & NAME2 (M) """
    match = MR_MRS_LAST_FIRST_RE.match(name)
    if match:
        lname = clean_last_name(match[1])
        return "{} & {} {}".format(match[2], match[3], lname)
    return None

MAC_ATTACK_RE = re.compile(r'^(MA?C)([A-Z])(.*)', flags=re.IGNORECASE)

def clean_last_name(lname):
    """ special case handler for last names """
    match = MAC_ATTACK_RE.match(lname)
    if match:
        return match[1].title() + match[2].upper() + match[3]
    return lname

AND_RE = re.compile(r' and ', flags=re.IGNORECASE)
NON_NAME_PIECES = re.compile(
    r'(Co Trustees.*Trust|Rev Trusts?|' +
    r'Revocable Trust)',
    flags=re.IGNORECASE
)

def pretty_print_name(name):
    """ try to clean up names """
    name = AND_RE.sub(' & ', name)
    name = NON_NAME_PIECES.sub('', name)
    name = squish(name).title()
    return last_first(name) or \
        mr_mrs_last_first(name) or \
        name
