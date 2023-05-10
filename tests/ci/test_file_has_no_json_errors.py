"""pylint dynamic json validation wrapper"""

import glob
import json
import pytest


FILTER = './../../**/*.json'
JSON_FILES = glob.glob(FILTER, recursive=True)


@pytest.mark.parametrize('filepath', JSON_FILES)
def test_file_is_valid_json(filepath):
    """validate that there the file is valid json"""
    print(F"creating tests for file {filepath}")

    json_payload = []

    # read file
    with open(filepath, 'r', encoding="utf8") as jsonfile:
        obj = jsonfile.read()

    # parse file
    json_payload = json.loads(obj)

    # pylint: disable=C1801
    assert len(json_payload) > 0
