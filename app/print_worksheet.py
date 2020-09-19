""" print worksheets at a time now! """
import sys
from collections import namedtuple
from datetime import datetime

from openpyxl import Workbook, load_workbook

from addresses import get_gather_address
from names import pretty_print_name
from print_territory import get_territory_docs, key_residence, phone_number_sort


def create_workbook():
    """ create a workbook handle """
    return Workbook()


def open_workbook(path):
    """ open existing workbook """
    return load_workbook(filename=path)


def make_street_sheet(workbook, t_id, street):
    """ copies template and makes sure that we print everything """
    current_street_sheet = workbook.copy_worksheet(workbook["Street Name"])
    current_street_sheet.title = street
    write_to_sheet(current_street_sheet, 0, 1, t_id)
    return current_street_sheet


COLS = [chr(65 + i) for i in range(26)]

def write_to_sheet(sheet, col, row, val):
    """ write to sheet """
    sheet["{}{}".format(COLS[col], row)] = val


def write_row(sheet, row, data):
    """ print a whole row at a time """
    write_to_sheet(sheet, 0, row, data.name)
    write_to_sheet(sheet, 1, row, data.address)
    write_to_sheet(sheet, 2, row, data.phone)
    if data.call1:
        write_to_sheet(sheet, 3, row, data.call1)
    if data.call2:
        write_to_sheet(sheet, 4, row, data.call2)
    if data.letter:
        write_to_sheet(sheet, 5, row, data.letter)
    if data.note:
        write_to_sheet(sheet, 6, row, data.note)
    return row + 1


ROW_FIELDS = ("name", "address", "phone", "call1", "call2", "letter", "note")
Row = namedtuple("Row", ROW_FIELDS, defaults=(None,) * len(ROW_FIELDS))

def stamp_last_updated(workbook, newest_date):
    """ stamps the last updated date on the readme page """
    workbook["Read Me"]["C1"] = "Last Updated: {}".format(newest_date)


def remove_template_sheets(workbook):
    """ cleans up template sheets """
    for name in ("Street Name", "Street 2 Name"):
        workbook.remove(workbook[name])


def print_workbook(t_id):
    """  ready! to print """
    workbook = open_workbook("template.xlsx")

    for street, residences in get_territory_docs(t_id):
        residences.sort(key=key_residence)
        row = 3
        sheet = make_street_sheet(workbook, t_id, street)
        youngest_change = datetime(2000, 1, 1)

        for resident in residences:
            addr = get_gather_address(resident["address"])
            name = pretty_print_name(resident.get("name", None) or "Current Resident")

            if youngest_change < resident.get("lastUpdate"):
                youngest_change = resident.get("lastUpdate")

            # do not call check
            if resident.get("doNotCall", None):
                row = write_row(sheet, row, Row(name, addr, "Do Not Call", "DNC", "DNC", "DNC"))
                continue

            phone_numbers = resident.get("phoneNumbers", [])
            if phone_numbers:
                phones = sorted(
                    list({p["number"] for p in phone_numbers}),
                    key=phone_number_sort
                )[0:2]

                for i, phone in enumerate(phones):
                    if i > 0:
                        row_data = Row("▲", "▲", phone, None, None, "⃠")
                    else:
                        row_data = Row(name, addr, phone)
                    row = write_row(sheet, row, row_data)

            else:
                row = write_row(sheet, row, Row(name, addr, "No Number Found", "-", "-"))

    stamp_last_updated(workbook, youngest_change)
    remove_template_sheets(workbook)
    workbook.save(filename="{}.xlsx".format(t_id))


if __name__ == "__main__":
    print_workbook(sys.argv[1])
    # fetch all records
    # for each street
    # make_street_sheet and print residences
        # make the printer work better, more reliably anyway
        # print
        # name | address | phone number OR dnc | first_note | second_note | letter_note | notes
        # row is red if DNC
        # letter is gray if NO sign
    # save as territory.xlsx
