import sys

if "__main__" == __name__:
    for f in sys.stdin:
        if f.strip():
            print(f.replace(") ", "-"))

