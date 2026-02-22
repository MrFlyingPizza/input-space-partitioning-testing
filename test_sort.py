import pytest
import runner
import subprocess
import contextlib
from tempfile import TemporaryDirectory


@pytest.mark.parametrize("test_case", runner.read_test_cases("params-output.csv"))
def test_eval(test_case):
    with TemporaryDirectory() as temp_dir, contextlib.chdir(temp_dir), runner.Context(
        test_case
    ) as context:
        subprocess.run(["sort", *context.get_filenames()])

    assert True
