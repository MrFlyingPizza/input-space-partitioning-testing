from test_sort import *
from pprint import pprint

from testcase import read_test_cases


def main():
    value_handlers = dict()
    for names, values in read_test_cases("tests.csv"):
        for name, value in zip(names, values):
            values = value_handlers.setdefault(name, dict())
            values.setdefault(value, None)

    pprint(list(value_handlers.items()))


if __name__ == "__main__":
    main()
