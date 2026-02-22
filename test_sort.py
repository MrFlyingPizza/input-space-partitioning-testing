import pytest
import subprocess
from contextlib import chdir, nullcontext
from tempfile import TemporaryDirectory

from runner import Context, File, read_test_cases


@pytest.mark.parametrize("test_case", read_test_cases("params-output.csv"))
def test_eval(test_case):
    with TemporaryDirectory() as temp_dir, chdir(temp_dir), Context(
        test_case
    ) as context, (
        open(context.stdin_file.name) if context.stdin_file else nullcontext()
    ) as stdin_file:
        args = context.args + context.get_filenames()
        result = subprocess.run(["sort", *args], stdin=stdin_file, capture_output=True)
        assert (
            "No such file or directory" in result.stderr.decode()
            and result.returncode != 0
        ) == context.has_file_with_meta(File.Meta.NON_EXISTENT)

        assert (
            "Permission denied" in result.stderr.decode() and result.returncode != 0
        ) == context.has_file_with_meta(File.Meta.READ_PROTECTED)
        print(result.stderr, result.stdout)

    assert True
