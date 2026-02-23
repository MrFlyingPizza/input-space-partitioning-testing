import string
import random
import os
from typing import Callable
from enum import Enum
from dataclasses import InitVar, dataclass, field

from testcase import TestCase


@dataclass
class Context:
    @dataclass
    class File:

        Meta = Enum("Meta", ["NON_EXISTENT", "READ_PROTECTED", "READABLE"])

        name: str
        meta: Meta = Meta.READABLE

        def set_characteristic(self, meta: Meta, /):
            self.meta = meta

    type InitPipeline = list[tuple[str, dict[str, Callable[[Context], None]]]]

    test_case: InitVar[TestCase]
    init_pipeline: InitVar[InitPipeline]
    stdin_file: File = field(init=False, default=None)
    input_files: list[File] = field(init=False, default_factory=list)
    input_lines: list[str] = field(init=False, default_factory=list)
    max_line_length: int = field(init=False, default=10)
    encoding: str = field(init=False, default="utf-8")
    args: list[str] = field(init=False, default_factory=list)
    random_source: File = field(init=False, default=None)
    random_source_content: str = field(init=False, default="")
    sort_key: str = field(init=False, default=None)
    ignore_leading_blanks: bool = field(init=False, default=False)
    dictionary_order: bool = field(init=False, default=False)
    ignore_case: bool = field(init=False, default=False)
    ignore_non_printable: bool = field(init=False, default=False)
    reverse: bool = field(init=False, default=False)

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
    incompatible_args = [
        ("--human-numeric-sort", "--dictionary-order"),
        ("--ignore-nonprinting", "--month-sort"),
        ("--ignore-nonprinting", "--general-numeric-sort"),
        ("--ignore-nonprinting", "--human-numeric-sort"),
        ("--dictionary-order", "--ignore-case", "--general-numeric-sort"),
        ("--dictionary-order", "--month-sort"),
    ]

    def __post_init__(self, test_case: TestCase, init_pipeline: InitPipeline):
        self.process_pipeline(test_case, init_pipeline)

    def __enter__(self):
        existing_inputs = list(
            filter(
                lambda f: f.meta != Context.File.Meta.NON_EXISTENT,
                self.get_all_inputs(),
            )
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
                    case Context.File.Meta.READ_PROTECTED:
                        os.chmod(file.name, 0)

        if (
            self.random_source
            and self.random_source.meta != Context.File.Meta.NON_EXISTENT
        ):
            with open(self.random_source.name, "w", encoding=self.encoding) as f:
                f.write(self.random_source_content)

            match self.random_source.meta:
                case Context.File.Meta.READ_PROTECTED:
                    os.chmod(self.random_source.name, 0)

        if self.random_source:
            self.add_arg("--random-source")
            self.add_arg(self.random_source.name)

        if self.ignore_leading_blanks:
            self.add_arg("--ignore-leading-blanks")
        if self.dictionary_order:
            self.add_arg("--dictionary-order")
        if self.ignore_case:
            self.add_arg("--ignore-case")
        if self.ignore_non_printable:
            self.add_arg("--ignore-nonprinting")

        if self.reverse:
            self.add_arg("--reverse")

        return self

    def __exit__(self, exc_type, exc, tb):
        pass

    def process_pipeline(self, test_case: TestCase, init_pipeline: InitPipeline, /):
        values = test_case.to_dict()
        for name, handlers in init_pipeline:
            handler = handlers[values[name]]
            if handler:
                handler(self)

    def has_incompatible_args(self):
        return any(
            all(incompatible_arg in self.args for incompatible_arg in incompatible_args)
            for incompatible_args in self.incompatible_args
        )

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
        self.input_files.append(Context.File(f"{len(self.input_files)}.txt"))

    def add_multiple_files(self, amount: int = 3, /):
        for _ in range(amount):
            self.add_one_file()

    def set_random_file_meta(self, meta: File.Meta, /):
        random.choice(self.input_files).meta = meta

    def add_standard_input_file(self):
        self.stdin_file = Context.File("stdin.txt")

    def add_lines_per_input(self, lines_per_input: int = 1):
        self.input_lines += [None] * (self.get_input_count() * lines_per_input)

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

    def add_random_source_file(self, meta=File.Meta.READABLE, *, content: str = ""):
        self.random_source = Context.File("random_source.txt", meta)
        self.random_source_content = content

    def set_ignore_leading_blanks(self):
        self.ignore_leading_blanks = True

    def set_dictionary_order(self):
        self.dictionary_order = True

    def set_ignore_case(self):
        self.ignore_case = True

    def set_ignore_non_printable(self):
        self.ignore_non_printable = True

    def set_reverse(self):
        self.reverse = True

    def get_expected_output(self):
        return "".join(
            sorted(self.input_lines, key=self.sort_key, reverse=self.reverse)
        )
