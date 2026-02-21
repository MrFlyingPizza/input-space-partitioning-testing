import csv
from dataclasses import dataclass

import pytest


@dataclass
class ActsTestCase:
    names: list[str]
    values: list[str]


def get_acts_test_cases(filename):
    with open(filename) as tests_file:
        csv_reader = csv.reader(filter(lambda row: row[0] != "#", tests_file))
        names = next(csv_reader)
        return list(ActsTestCase(names, values) for values in csv_reader)


@pytest.mark.parametrize("test_case", get_acts_test_cases("params-output.csv"))
def test_eval(test_case):
    print(test_case)
    assert True