""" print worksheets at a time now! """
import sys
from openpyxl import Workbook, load_workbook


def create_workbook():
    """ create a workbook handle """
    return Workbook()


def open_workbook(path):
    """ open existing workbook """
    return load_workbook(filename=path)


def make_street_sheet(wb, street, residences):
    """ copies template and makes sure that we print everything """
    current_street_sheet = wb.copy_worksheet(wb["Street 2 Name"])
    current_street_sheet.title = street
    row = 3
    for doc in residences:
        current_street_sheet["A{}".format(row)] = doc


if __name__ == "__main__":
    wb = open_workbook("template.xlsx")
    # fetch all records
    # for each street
    # make_street_sheet and print residences
        # make the printer work better, more reliably anyway
        # print
        # name | address | phone number OR dnc | first_note | second_note | letter_note | notes
        # row is red if DNC
        # letter is gray if NO sign
    # save as territory.xlsx
    make_street_sheet(wb, "E 104th St", ["123 E 104th St, Tulsa, OK"])
    wb.save(filename="test.xlsx")
