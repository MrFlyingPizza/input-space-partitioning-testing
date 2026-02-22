"""
Describes and runs test cases.
"""

import string
import random
import csv
import os
import stat
from typing import NamedTuple, Callable
from enum import Enum
from dataclasses import InitVar, dataclass, field


class TestCase(NamedTuple):
    names: list[str]
    values: list[str]

    def zip(self):
        return zip(self.names, self.values)

    def to_dict(self):
        return dict(self.zip())


@dataclass
class File:

    Meta = Enum("Meta", ["NON_EXISTENT", "READ_PROTECTED", "READABLE"])

    name: str
    meta: Meta = Meta.READABLE

    def set_characteristic(self, meta: Meta, /):
        self.meta = meta


@dataclass
class Context:
    test_case: InitVar[TestCase]
    stdin_file: File = field(init=False, default=None)
    input_files: list[File] = field(init=False, default_factory=list)
    input_lines: list[str] = field(init=False, default_factory=list)
    max_line_length: int = field(init=False, default=10)

    ascii_upper = string.ascii_uppercase
    ascii_lower = string.ascii_lowercase
    ascii_letters = string.ascii_letters
    ascii_alphanum = string.ascii_letters + string.digits
    ascii_all = string.printable

    def __post_init__(self, test_case: TestCase):
        values = test_case.to_dict()
        for name, handlers in _context_creation_pipeline:
            handler = handlers[values[name]]
            if handler:
                handler(self)

    def __enter__(self):
        existing_inputs = list(
            filter(lambda f: f.meta != File.Meta.NON_EXISTENT, self.get_all_inputs())
        )

        if existing_inputs:
            batch_size = len(self.input_lines) // len(existing_inputs)
            for i, file in enumerate(existing_inputs):
                with open(file.name, "w") as f:
                    f.writelines(
                        self.input_lines[
                            i
                            * batch_size : min(
                                (i + 1) * batch_size, len(self.input_lines)
                            )
                        ]
                    )

                match file.meta:
                    case File.Meta.READ_PROTECTED:
                        os.chmod(file.name, 0)

        return self

    def __exit__(self, exc_type, exc, tb):
        pass

    def get_all_inputs(self):
        return ([self.stdin_file] if self.stdin_file else []) + self.input_files

    def get_sorted_input_lines(self):
        return "\n".join(sorted(self.input_lines))

    def get_filenames(self):
        return [file.name for file in self.input_files]

    def get_input_count(self):
        input_count = len(self.input_files)
        if self.stdin_file:
            input_count += 1
        return input_count

    def add_one_file(self):
        self.input_files.append(File(f"{len(self.input_files)}.txt"))

    def add_multiple_files(self, amount: int = 3, /):
        for i in range(amount):
            self.add_one_file()

    def set_random_file_meta(self, meta: File.Meta, /):
        random.choice(self.input_files).meta = meta

    def add_standard_input_file(self):
        self.stdin_file = File("stdin.txt")

    def add_one_line(self):
        self.input_lines.append(None)

    def add_multiple_lines(self, amount_per_input: int = 10, /):
        self.input_lines += [None] * (self.get_input_count() * amount_per_input)

    def set_all_input_lines_empty(self):
        self.input_lines = [""] * len(self.input_lines)

    def set_random_input_lines_empty(self, amount_per_input: int = 2):
        indices = random.sample(
            range(len(self.input_lines)),
            k=min(amount_per_input * self.get_input_count(), len(self.input_lines)),
        )
        for index in indices:
            self.input_lines[index] = ""

    def set_input_line_length(self, length: int, /):
        self.max_line_length = length

    def fill_input_lines_using_charset(self, charset: str, /):
        for i in range(len(self.input_lines)):
            length = random.randint(1, self.max_line_length)
            self.input_lines[i] = "".join(random.choices(charset, k=length))

    def fill_input_lines_with_random_uppercase_letters(self):
        self.fill_input_lines_using_charset(self.ascii_upper)

    def fill_input_lines_with_random_lowercase_letters(self):
        self.fill_input_lines_using_charset(self.ascii_lower)

    def fill_input_lines_with_random_mixedcase_letters(self):
        self.fill_input_lines_using_charset(self.ascii_letters)

    def fill_input_lines_with_random_alphanum(self):
        self.fill_input_lines_using_charset(self.ascii_alphanum)

    def fill_input_lines_with_random_ascii(self):
        self.fill_input_lines_using_charset(self.ascii_all)


_context_creation_pipeline: list[tuple[str, dict[str, Callable[[Context], None]]]] = [
    (
        "input_files",
        {
            "multiple_files": Context.add_multiple_files,
            "no_file": None,
            "one_file": Context.add_one_file,
        },
    ),
    (
        "input_file_characteristics",
        {
            "non_existent": lambda context: context.set_random_file_meta(
                File.Meta.NON_EXISTENT
            ),
            "not_applicable": None,
            "read_protected": lambda context: context.set_random_file_meta(
                File.Meta.READ_PROTECTED
            ),
            "readable_only": None,
        },
    ),
    (
        "standard_input",
        {
            "has_standard_input": Context.add_standard_input_file,
            "no_standard_input": None,
        },
    ),
    (
        "input_lines",
        {
            "empty": None,
            "multiple_lines": Context.add_multiple_lines,
            "not_applicable": None,
            "one_line": Context.add_one_line,
        },
    ),
    (
        "input_line_length",
        {
            "more_characters": lambda context: context.set_input_line_length(10),
            "not_applicable": None,
            "one_character": lambda context: context.set_input_line_length(1),
        },
    ),
    (
        "input_content_type",
        {
            "alphanum": Context.fill_input_lines_with_random_alphanum,
            "any": Context.fill_input_lines_with_random_ascii,
            "human_readable_numbers": None,
            "lower": Context.fill_input_lines_with_random_lowercase_letters,
            "mixed": Context.fill_input_lines_with_random_mixedcase_letters,
            "months": None,
            "not_applicable": None,
            "numeric_only": None,
            "upper": Context.fill_input_lines_with_random_uppercase_letters,
            "version_numbers": None,
        },
    ),
    (
        "input_line_emptiness",
        {
            "all_empty": Context.set_all_input_lines_empty,
            "never_empty": None,
            "not_applicable": None,
            "some_empty": Context.set_random_input_lines_empty,
        },
    ),
    (
        "input_content_blanks",
        {
            "all_leading": None,
            "no_blanks": None,
            "not_applicable": None,
            "some_leading": None,
        },
    ),
    (
        "input_character_encoding",
        {"ascii": None, "not_applicable": None, "utf16": None, "utf8": None},
    ),
    (
        "input_content_sorting",
        {
            "ascending": None,
            "descending": None,
            "not_applicable": None,
            "unsorted": None,
        },
    ),
    ("ignore_leading_blanks", {"false": None, "not_applicable": None, "true": None}),
    ("dictionary_order", {"false": None, "not_applicable": None, "true": None}),
    ("ignore_case", {"false": None, "not_applicable": None, "true": None}),
    (
        "ignore_non_printable_characters",
        {"false": None, "not_applicable": None, "true": None},
    ),
    (
        "sort_type",
        {
            "human_numeric": None,
            "lexigraphical": None,
            "month": None,
            "not_applicable": None,
            "numeric": None,
            "random": None,
            "version": None,
        },
    ),
    ("sort_reverse", {"false": None, "not_applicable": None, "true": None}),
    (
        "random_source",
        {
            "empty_file": None,
            "non_empty_file": None,
            "non_existent_file": None,
            "none": None,
            "read_protected_file": None,
        },
    ),
]


def read_test_cases(filename):
    with open(filename) as tests_file:
        csv_reader = csv.reader(filter(lambda row: row[0] != "#", tests_file))
        names = next(csv_reader)
        return list(TestCase(names, values) for values in csv_reader)
