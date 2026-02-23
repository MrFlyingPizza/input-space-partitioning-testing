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
        code = result.returncode
        stdout = result.stdout.decode(context.encoding)
        stderr = result.stderr.decode()

        if context.has_incompatible_args():
            assert "incompatible" in stderr
            return

        if (
            context.random_source
            and context.random_source.meta == Context.File.Meta.NON_EXISTENT
        ):
            assert (
                "random_source.txt" in stderr
                and "No such file or directory" in stderr
                and code != 0
            )
            return

        if (
            context.random_source
            and context.random_source.meta == Context.File.Meta.READ_PROTECTED
        ):
            assert (
                "random_source.txt" in stderr
                and "Permission denied" in stderr
                and code != 0
            )
            return

        if (
            context.random_source
            and context.random_source_content == ""
            and context.random_source.meta == Context.File.Meta.READABLE
        ):
            assert (
                "random_source.txt" in stderr and "end of file" in stderr and code != 0
            )
            return

        if non_existent_file := context.find_file_with_meta(
            Context.File.Meta.NON_EXISTENT
        ):
            assert (
                "No such file or directory" in stderr
                and (non_existent_file.name in stderr if non_existent_file else False)
                and code != 0
            )
            return

        if permission_denied_file := context.find_file_with_meta(
            Context.File.Meta.READ_PROTECTED
        ):
            assert (
                "Permission denied" in stderr
                and (
                    permission_denied_file.name in stderr
                    if permission_denied_file
                    else False
                )
                and code != 0
            )
            return

        assert code == 0, "Guard for stdout tests"

        assert stdout.rstrip("\n") == context.get_expected_output()
