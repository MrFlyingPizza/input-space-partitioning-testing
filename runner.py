"""
Describes and runs test cases.
"""

import csv

from typing import NamedTuple

_handlers = {
    "input_files": {"one_file": None, "multiple_files": None, "no_file": None},
    "input_file_characteristics": {
        "read_protected": None,
        "readable_only": None,
        "not_applicable": None,
        "non_existent": None,
    },
    "standard_input": {"has_standard_input": None, "no_standard_input": None},
    "input_lines": {
        "one_line": None,
        "multiple_lines": None,
        "not_applicable": None,
        "empty": None,
    },
    "input_line_emptiness": {
        "some_empty": None,
        "never_empty": None,
        "not_applicable": None,
        "all_empty": None,
    },
    "input_content_type": {
        "any": None,
        "lower": None,
        "upper": None,
        "mixed": None,
        "alphanum": None,
        "months": None,
        "numeric_only": None,
        "human_readable_numbers": None,
        "version_numbers": None,
        "not_applicable": None,
    },
    "input_line_length": {"not_applicable": None},
    "input_content_blanks": {
        "some_leading": None,
        "no_blanks": None,
        "not_applicable": None,
        "all_leading": None,
    },
    "input_character_encoding": {
        "utf8": None,
        "utf16": None,
        "not_applicable": None,
        "ascii": None,
    },
    "input_content_sorting": {
        "descending": None,
        "unsorted": None,
        "not_applicable": None,
        "ascending": None,
    },
    "ignore_leading_blanks": {"false": None, "not_applicable": None, "true": None},
    "dictionary_order": {"false": None, "not_applicable": None, "true": None},
    "ignore_case": {"false": None, "not_applicable": None, "true": None},
    "ignore_non_printable_characters": {
        "false": None,
        "not_applicable": None,
        "true": None,
    },
    "sort_type": {
        "lexigraphical": None,
        "month": None,
        "numeric": None,
        "human_numeric": None,
        "random": None,
        "version": None,
        "not_applicable": None,
    },
    "sort_reverse": {"false": None, "not_applicable": None, "true": None},
    "random_source": {
        "none": None,
        "non_existent_file": None,
        "empty_file": None,
        "non_empty_file": None,
        "read_protected_file": None,
    },
}


class TestCase(NamedTuple):
    names: list[str]
    values: list[str]


def read_test_cases(filename):
    with open(filename) as tests_file:
        csv_reader = csv.reader(filter(lambda row: row[0] != "#", tests_file))
        names = next(csv_reader)
        return list(TestCase(names, values) for values in csv_reader)
