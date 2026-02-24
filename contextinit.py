"""
Defines how to create a context for our tests.
"""

from context import Context

pipeline: Context.InitPipeline = [
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
                Context.File.Meta.NON_EXISTENT
            ),
            "not_applicable": None,
            "read_protected": lambda context: context.set_random_file_meta(
                Context.File.Meta.READ_PROTECTED
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
            "ascending": lambda context: context.input_lines.sort(key=context.sort_key),
            "descending": lambda context: context.input_lines.sort(
                key=context.sort_key, reverse=True
            ),
            "not_applicable": None,
            "unsorted": None,
        },
    ),
    (
        "ignore_leading_blanks",
        {
            "false": None,
            "not_applicable": None,
            "true": Context.set_ignore_leading_blanks,
        },
    ),
    (
        "dictionary_order",
        {
            "false": None,
            "not_applicable": None,
            "true": Context.set_dictionary_order,
        },
    ),
    (
        "ignore_case",
        {
            "false": None,
            "not_applicable": None,
            "true": Context.set_ignore_case,
        },
    ),
    (
        "ignore_non_printable_characters",
        {
            "false": None,
            "not_applicable": None,
            "true": Context.set_ignore_non_printable,
        },
    ),
    (
        "sort_type",
        {
            "human_numeric": lambda context: context.add_arg("--human-numeric-sort"),
            "lexigraphical": None,
            "month": Context.set_sort_type_month,
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
            "true": Context.set_reverse,
        },
    ),
    (
        "random_source",
        {
            "empty_file": Context.add_random_source_file,
            "non_empty_file": lambda context: context.add_random_source_file(
                content="Alkdjfelkjefalkjfelakwhfjkl"
            ),
            "non_existent_file": lambda context: context.add_random_source_file(
                Context.File.Meta.NON_EXISTENT
            ),
            "none": None,
            "read_protected_file": lambda context: context.add_random_source_file(
                Context.File.Meta.READ_PROTECTED
            ),
        },
    ),
]
