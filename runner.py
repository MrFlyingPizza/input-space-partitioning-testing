"""
Describes and runs test cases.
"""

import string
import random
import csv
import os
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
    encoding: str = field(init=False, default="utf-8")
    args: list[str] = field(init=False, default_factory=list)
    random_source: File = field(init=False, default=None)
    random_source_empty: bool = field(init=False, default=False)

    ascii_upper = string.ascii_uppercase
    ascii_lower = string.ascii_lowercase
    ascii_letters = string.ascii_letters
    ascii_alphanum = string.ascii_letters + string.digits
    ascii_all = string.printable
    months = [
        "January",
        "February",
        "March",
        "April",
        "May",
        "June",
        "July",
        "August",
        "September",
        "October",
        "November",
        "December",
    ]

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
                with open(file.name, "w", encoding=self.encoding) as f:
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

        if self.random_source and self.random_source.meta != File.Meta.NON_EXISTENT:
            with open(self.random_source.name, "w", encoding=self.encoding) as f:
                if not self.random_source_empty:
                    f.write("".join(random.choices(self.ascii_alphanum, k=10)))

            match self.random_source.meta:
                case File.Meta.READ_PROTECTED:
                    os.chmod(self.random_source.name, 0)

        return self

    def __exit__(self, exc_type, exc, tb):
        pass

    def find_file_with_meta(self, meta: File.Meta):
        return next(filter(lambda f: f.meta == meta, self.input_files), None)

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
        for _ in range(amount):
            self.add_one_file()

    def set_random_file_meta(self, meta: File.Meta, /):
        random.choice(self.input_files).meta = meta

    def add_standard_input_file(self):
        self.stdin_file = File("stdin.txt")

    def add_lines_per_input(self, lines_per_input: int = 1):
        self.input_lines += [None] * (self.get_input_count() * 1)

    def set_all_input_lines_empty(self):
        self.input_lines = [""] * len(self.input_lines)

    def set_random_input_lines_empty(self, amount_per_input: int = 2):
        if not self.input_lines:
            return
        indices = random.sample(
            range(len(self.input_lines)),
            k=min(amount_per_input * self.get_input_count(), len(self.input_lines)),
        )
        for index in indices:
            self.input_lines[index] = ""

    def set_input_line_length(self, length: int, /):
        self.max_line_length = length

    def fill_input_lines_using_function(self, func: Callable[[int, str], None]):
        for i, line in enumerate(self.input_lines):
            self.input_lines[i] = func(i, line)

    def fill_input_lines_using_charset(self, charset: str, /):
        self.fill_input_lines_using_function(
            lambda *_: "".join(
                random.choices(charset, k=random.randint(1, self.max_line_length))
            )
        )

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

    def fill_input_lines_with_random_elements(self, elements: list[str]):
        self.fill_input_lines_using_function(lambda *_: random.choice(elements))

    def fill_input_lines_with_random_months(self):
        self.fill_input_lines_with_random_elements(self.months)

    def fill_input_lines_with_random_numerics(self):
        formats = ["{:.5f}", "{:.5e}", "{:+.5f}", "{:+.5e}"]
        self.fill_input_lines_using_function(
            lambda *_: random.choice(
                [
                    lambda: random.choice(formats).format(random.uniform(-1e10, 1e10)),
                    lambda: str(random.randint(-1000, 1000)),
                ]
            )()
        )

    def fill_input_lines_with_random_human_numerics(self):
        suffixes = ["", "K", "M", "G", "T", "P", "E", "Z", "Y"]
        self.fill_input_lines_using_function(lambda *_: f"{random.choice([
                lambda: str(random.randint(-1000, 1000)),
                lambda: f"{random.uniform(-1000, 1000):.3f}",
            ])()}{random.choice(suffixes)}")

    def fill_input_lines_with_random_version_numbers(self):
        self.fill_input_lines_using_function(
            lambda *_: ".".join(str(random.randint(0, 100)) for i in range(3))
        )

    def add_leading_blanks_to_all_lines(self):
        blank = "          "
        self.fill_input_lines_using_function(lambda _, line: blank + line)

    def add_leading_blanks_to_some_random_lines(self):
        blank = "          "
        self.fill_input_lines_using_function(
            lambda _, line: blank + line if random.random() < 0.5 else line
        )

    def set_file_encoding(self, encoding: str, /):
        self.encoding = encoding

    def add_arg(self, arg: str, /):
        self.args.append(arg)

    def add_random_source_file(self):
        self.random_source = File("random_source.txt")
        self.add_arg("--random-source")
        self.add_arg(self.random_source.name)

    def add_empty_random_source_file(self):
        self.add_random_source_file()
        self.random_source_empty = True

    def add_non_existent_source_file(self, /):
        self.add_random_source_file()
        self.random_source_empty = True
        self.random_source.meta = File.Meta.NON_EXISTENT

    def add_read_protected_source_file(self, /):
        self.add_random_source_file()
        self.random_source_empty = True
        self.random_source.meta = File.Meta.NON_EXISTENT


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
            "multiple_lines": lambda context: context.add_lines_per_input(20),
            "not_applicable": None,
            "one_line": lambda context: context.add_lines_per_input(1),
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
            "human_readable_numbers": Context.fill_input_lines_with_random_human_numerics,
            "lower": Context.fill_input_lines_with_random_lowercase_letters,
            "mixed": Context.fill_input_lines_with_random_mixedcase_letters,
            "months": Context.fill_input_lines_with_random_months,
            "not_applicable": None,
            "numeric": Context.fill_input_lines_with_random_numerics,
            "upper": Context.fill_input_lines_with_random_uppercase_letters,
            "version_numbers": Context.fill_input_lines_with_random_version_numbers,
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
            "all_leading": Context.add_leading_blanks_to_all_lines,
            "no_blanks": None,
            "not_applicable": None,
            "some_leading": Context.add_leading_blanks_to_some_random_lines,
        },
    ),
    (
        "input_character_encoding",
        {
            "ascii": lambda context: context.set_file_encoding("ascii"),
            "not_applicable": None,
            "utf16": lambda context: context.set_file_encoding("utf-16"),
            "utf8": lambda context: context.set_file_encoding("utf-8"),
        },
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
    (
        "ignore_leading_blanks",
        {
            "false": None,
            "not_applicable": None,
            "true": lambda context: context.add_arg("--ignore-leading-blanks"),
        },
    ),
    (
        "dictionary_order",
        {
            "false": None,
            "not_applicable": None,
            "true": lambda context: context.add_arg("--dictionary-order"),
        },
    ),
    (
        "ignore_case",
        {
            "false": None,
            "not_applicable": None,
            "true": lambda context: context.add_arg("--ignore-case"),
        },
    ),
    (
        "ignore_non_printable_characters",
        {
            "false": None,
            "not_applicable": None,
            "true": lambda context: context.add_arg("--ignore-nonprinting"),
        },
    ),
    (
        "sort_type",
        {
            "human_numeric": lambda context: context.add_arg("--human-numeric-sort"),
            "lexigraphical": None,
            "month": lambda context: context.add_arg("--month-sort"),
            "not_applicable": None,
            "numeric": lambda context: context.add_arg("--numeric-sort"),
            "general_numeric": lambda context: context.add_arg(
                "--general-numeric-sort"
            ),
            "random": lambda context: context.add_arg("--random-sort"),
            "version": lambda context: context.add_arg("--version-sort"),
        },
    ),
    (
        "sort_reverse",
        {
            "false": None,
            "not_applicable": None,
            "true": lambda context: context.add_arg("--reverse"),
        },
    ),
    (
        "random_source",
        {
            "empty_file": Context.add_empty_random_source_file,
            "non_empty_file": Context.add_random_source_file,
            "non_existent_file": Context.add_non_existent_source_file,
            "none": None,
            "read_protected_file": Context.add_read_protected_source_file,
        },
    ),
]


def read_test_cases(filename):
    with open(filename) as tests_file:
        csv_reader = csv.reader(filter(lambda row: row[0] != "#", tests_file))
        names = next(csv_reader)
        return list(TestCase(names, values) for values in csv_reader)
