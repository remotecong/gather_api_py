from owner_parsers.tulsa.geo_json import find_acct_num

if __name__ == "__main__":
    TEST_CASES = [
        [36.002307, -95.857551],
        [36.0414943928749, -95.9485495090485],
        [36.0415811452406, -95.9485334157944],
        [36.0417850129239, -95.9485334157944],
    ]
    for coord in TEST_CASES:
        #coord.reverse()
        acct_num = find_acct_num(coord)
        print(f"WE GOT FOR {coord}")
        print(f"-- {acct_num}")
    print(f"hello {'there'}")
