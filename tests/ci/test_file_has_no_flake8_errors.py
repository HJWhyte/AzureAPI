"""pylint dynamic flake8 wrapper"""

import glob
import subprocess
import pytest

FILTER = './../../**/*.py'
PYTHON_FILES = glob.glob(FILTER, recursive=True)


@pytest.mark.parametrize('filepath', PYTHON_FILES)
def test_file_has_no_flake8_errors(filepath):
    """validate that there are zero flake8 warnings against a python file"""
    print(F"creating tests for file {filepath}")

    with subprocess.Popen("flake8 " + filepath + " --isolated --max-complexity 10",  # noqa: 501 pylint: disable=line-too-long
                          stdout=subprocess.PIPE, shell=True) as proc:
        (out, _err) = proc.communicate()

        # pylint: disable=C1801
        assert len(out) == 0
