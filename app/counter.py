""" territory helper locations converter """
import sys
import pandas as pd

def get_rows():
    """ loads up spreadsheet and yields rows """
    DATA = pd.read_excel("sample.xlsx")
    for r in range(DATA.shape[0]):
        yield DATA.at[r, "Territory number"]


def load_territory():
    """ fetch all locations for a territory """
    book = {}
    for doc in get_rows():
        if not book.get(doc, None):
            book[doc] = 1
        else:
            book[doc] = book[doc] + 1
    return sorted(book.items(), key=lambda x: x[1], reverse=True)


def load_territory_with_logs():
    """ load territory with logs along the way """
    for t_id, count in load_territory():
        print(f"{t_id}: {count}")

if __name__ == "__main__":
    load_territory_with_logs()
