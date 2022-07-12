import os
import tempfile
from typing import Generator, List

import pytest

from runexpy.utils import DefaultParamsT


@pytest.fixture()
def script() -> List[str]:
    command = """import sys
print("stdout")
print("stderr", file=sys.stderr)
with open("out.txt", "w") as f:
    f.write("file\\n")
"""
    script = ["python3", "-c", f"{command}"]
    return script


@pytest.fixture()
def default_params() -> DefaultParamsT:
    return {
        "p1": "x",
        "p2": 3,
        "p3": None,
    }


@pytest.fixture()
def campaign_dir() -> Generator[str, None, None]:
    with tempfile.TemporaryDirectory() as tempdir:
        yield os.path.join(tempdir, "temp_campaign")
