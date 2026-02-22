"""
Defines test cases that contain test parameters.
"""

import csv
from typing import NamedTuple


class TestCase(NamedTuple):
    names: list[str]
    values: list[str]

    def zip(self):
        return zip(self.names, self.values)

    def to_dict(self):
        return dict(self.zip())


def read_test_cases(filename):
    with open(filename) as tests_file:
        csv_reader = csv.reader(filter(lambda row: row[0] != "#", tests_file))
        names = next(csv_reader)
        return list(TestCase(names, values) for values in csv_reader)
