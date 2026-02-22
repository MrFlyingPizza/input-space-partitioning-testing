import pytest
import subprocess
from contextlib import chdir, nullcontext
from tempfile import TemporaryDirectory

from testcase import read_test_cases
from context import Context
from contextinit import pipeline


@pytest.mark.parametrize("test_case", read_test_cases("tests.csv"))
def test_eval(test_case):
    with (
        TemporaryDirectory() as temp_dir,
        chdir(temp_dir),
        Context(test_case, pipeline) as context,
        (
            open(context.stdin_file.name) if context.stdin_file else nullcontext()
        ) as stdin_file,
    ):
        assert (context.stdin_file is None) == (stdin_file is None)

        args = context.args + context.get_filenames()

        result = subprocess.run(
            ["sort", *args],
            stdin=stdin_file,
            capture_output=True,
        )
        stderr = result.stderr.decode()
        stdout = result.stderr.decode()

        has_incompatible_args = any(
            all(incompatible_arg in args for incompatible_arg in incompatible_args)
            for incompatible_args in [
                ("--human-numeric-sort", "--dictionary-order"),
                ("--ignore-nonprinting", "--month-sort"),
                ("--ignore-nonprinting", "--general-numeric-sort"),
                ("--ignore-nonprinting", "--human-numeric-sort"),
                ("--dictionary-order", "--ignore-case", "--general-numeric-sort"),
                ("--dictionary-order", "--month-sort"),
            ]
        )

        has_random_source = context.random_source is not None
        random_source_file_no_exist = (
            has_random_source
            and context.random_source.meta == Context.File.Meta.NON_EXISTENT
        )
        random_source_file_read_protected = (
            has_random_source
            and context.random_source.meta == Context.File.Meta.READ_PROTECTED
        )
        random_source_file_empty = (
            has_random_source and context.random_source_content == ""
        )

        assert ("incompatible" in stderr) == has_incompatible_args

        assert (
            "random_source.txt" in stderr
            and "No such file or directory" in stderr
            and result.returncode != 0
        ) == random_source_file_no_exist

        assert (
            "random_source.txt" in stderr
            and "Permission denied" in stderr
            and result.returncode != 0
        ) == random_source_file_read_protected

        assert (
            "random_source.txt" in stderr
            and "end of file" in stderr
            and result.returncode != 0
        ) == (
            random_source_file_empty
            and not random_source_file_no_exist
            and not random_source_file_read_protected
        )

        has_random_source_error = (
            random_source_file_no_exist
            or random_source_file_read_protected
            or random_source_file_empty
        )

        non_existent_file = context.find_file_with_meta(Context.File.Meta.NON_EXISTENT)
        assert (
            "No such file or directory" in stderr
            and (non_existent_file.name in stderr if non_existent_file else False)
            and result.returncode != 0
        ) == (
            non_existent_file is not None
            and not has_incompatible_args
            and not has_random_source_error
        )

        permission_denied_file = context.find_file_with_meta(
            Context.File.Meta.READ_PROTECTED
        )
        assert (
            "Permission denied" in stderr
            and (
                permission_denied_file.name in stderr
                if permission_denied_file
                else False
            )
            and result.returncode != 0
        ) == (
            permission_denied_file is not None
            and not has_incompatible_args
            and not has_random_source_error
        )

        has_file_error = any([non_existent_file, permission_denied_file])

        has_error = has_incompatible_args or has_random_source_error or has_file_error

        assert (result.returncode == 0) == (not has_error)

        # Implement stdout checks
