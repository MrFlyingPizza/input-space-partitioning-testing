from test_sort import *
from pprint import pprint

from runner import read_test_cases


def main():
    value_handlers = dict()
    for names, values in read_test_cases("params-output.csv"):
        for name, value in zip(names, values):
            values = value_handlers.setdefault(name, dict())
            values.setdefault(value, None)

    pprint(value_handlers)


if __name__ == "__main__":
    main()
