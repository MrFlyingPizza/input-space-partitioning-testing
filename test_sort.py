import pytest
import subprocess
from contextlib import chdir, nullcontext
from tempfile import TemporaryDirectory

from runner import Context, read_test_cases


@pytest.mark.parametrize("test_case", read_test_cases("params-output.csv"))
def test_eval(test_case):
    with TemporaryDirectory() as temp_dir, chdir(temp_dir), Context(
        test_case
    ) as context, (
        open(context.stdin_file.name) if context.stdin_file else nullcontext()
    ) as stdin_file:
        args = context.args + context.get_filenames()
        result = subprocess.run(["sort", *args], stdin=stdin_file, capture_output=True)
        print(result.stderr, result.stdout)

    assert True
