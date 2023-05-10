"""safety dynamic pytest wrapper"""

import glob
import subprocess
import json
import pytest

FILTER = './../../**/requirements.txt'
PYTHON_FILES = glob.glob(FILTER, recursive=True)


@pytest.mark.parametrize('filepath', PYTHON_FILES)
def test_file_has_no_safety_errors(filepath):
    """validate that there are zero safety warnings against a python file"""
    print(F"creating tests for file {filepath}")

    with subprocess.Popen("safety check --file=" + filepath + " --json",
                          stdout=subprocess.PIPE, shell=True) as proc:
        (out, _err) = proc.communicate()

    lint_json = []
    if out and out.strip():
        lint_json = json.loads(out)
        print(out)

        # pylint: disable=C1801
        assert len(lint_json['vulnerabilities']) == 0
