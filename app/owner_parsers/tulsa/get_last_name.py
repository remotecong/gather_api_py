import re

def get_last_name(raw_name):
    ln = re.sub(r'( the| ttee| revocable| rev| trustee| trust| Living| \d+)', '', raw_name)
    ln = [n.strip() for n in ln.split(',')][0]

    if ' ' in ln:
        return re.match(r'^[^\s]+\s', ln)[0].strip()
    return ln


if __name__ == '__main__':
    print(get_last_name('DOE, JOHN S'))
