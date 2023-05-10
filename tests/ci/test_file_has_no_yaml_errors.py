"""yamllint dynamic pytest wrapper"""

import glob
import subprocess
import pytest

FILTER_YAML = './../../**/*.yaml'
FILTER_YML = './../../**/*.yml'
YAML_FILES = glob.glob(FILTER_YML, recursive=True) + glob.glob(FILTER_YAML, recursive=True)  # noqa: 501 pylint: disable=line-too-long


@pytest.mark.parametrize('filepath', YAML_FILES)
def test_file_has_no_yamllint_errors(filepath):
    """validate that there are zero yamllint warnings against an YAML file"""
    print(F"creating tests for file {filepath}")

    with subprocess.Popen("yamllint " + filepath + " -c ../../.yamllint",
                          stdout=subprocess.PIPE, shell=True) as proc:
        (out, _err) = proc.communicate()

    if out and out.strip():
        print(out)

    # pylint: disable=C1801
    assert len(out) == 0
