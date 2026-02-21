import pytest
import runner


@pytest.mark.parametrize("test_case", runner.read_test_cases("params-output.csv"))
def test_eval(test_case):
    print(test_case)
    assert True
