import csv
from collections import namedtuple

import pytest


def get_test_cases(filename):
    with open(filename) as tests_file:
        csv_reader = csv.reader(filter(lambda row: row[0] != "#", tests_file))
        headers = next(csv_reader)
        TestCase = namedtuple("TestCase", headers)
        for row in csv_reader:
            yield TestCase(*row)


@pytest.mark.parametrize("test_case", get_test_cases("params-output.csv"))
def test_eval(test_case):
    print(test_case)
    assert True