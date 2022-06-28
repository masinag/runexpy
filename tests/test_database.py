import os
import tempfile
from typing import Generator

import pytest

from pyexp.database import Database
from pyexp.result import ParamsT, Result


@pytest.fixture()
def script() -> str:
    return "script"


@pytest.fixture()
def default_params() -> ParamsT:
    return {
        "p1": "x",
        "p2": 3,
        "p3": None,
    }


@pytest.fixture()
def campaign_dir() -> Generator[str, None, None]:
    with tempfile.TemporaryDirectory() as tempdir:
        yield os.path.join(tempdir, "temp_exp")


def test_new_db(script: str, default_params, campaign_dir):
    db = Database.new(script, default_params, campaign_dir, False)
    assert db.get_script() == script
    assert db.get_campaign_dir() == campaign_dir
    assert db.get_default_params() == default_params


def test_new_db_existing_dir_overwrite(script, default_params, campaign_dir):
    _ = Database.new(script, default_params, campaign_dir, False)
    default_params["p4"] = 0
    db = Database.new(script, default_params, campaign_dir, True)
    assert db.get_script() == script
    assert db.get_campaign_dir() == campaign_dir
    assert db.get_default_params() == default_params


def test_new_db_existing_dir_no_overwrite(script, default_params, campaign_dir):
    _ = Database.new(script, default_params, campaign_dir, False)
    default_params["p4"] = 0
    with pytest.raises(FileExistsError):
        _ = Database.new(script, default_params, campaign_dir, False)


def test_load_db(script, default_params, campaign_dir):
    _ = Database.new(script, default_params, campaign_dir, False)
    db = Database.load(campaign_dir)
    assert db.get_script() == script
    assert db.get_campaign_dir() == campaign_dir
    assert db.get_default_params() == default_params


def test_load_db_non_existing_dir(campaign_dir):
    with pytest.raises(ValueError):
        _ = Database.load(campaign_dir)


def test_insert_result(script, default_params, campaign_dir):
    db = Database.new(script, default_params, campaign_dir, False)
    params = default_params
    params["p1"] = 13
    params["p3"] = 2
    result = Result("exp_1", 0.01, 0, params)
    db.insert_result(result)
    result = Result("exp_2", 0.01, 0, params)
    # params["p2"] = "foo"
    db.insert_result(result)
    assert db.count_results_for(params) == 2


def test_insert_bad_result1(script, default_params, campaign_dir):
    db = Database.new(script, default_params, campaign_dir, False)
    params = default_params
    result = Result("exp_1", 0.01, 0, params)
    db.insert_result(result)
    with pytest.raises(ValueError):
        db.insert_result(result)


def test_insert_bad_result2(script, default_params, campaign_dir):
    db = Database.new(script, default_params, campaign_dir, False)
    params = {
        "a": 0,
        "b": 1,
    }
    result = Result("exp_1", 0.01, 0, params)
    with pytest.raises(ValueError):
        db.insert_result(result)


def test_retrieve_result(script, default_params, campaign_dir):
    db = Database.new(script, default_params, campaign_dir, False)
    params = default_params
    result1 = Result("exp_1", 0.01, 0, params)
    db.insert_result(result1)
    result2 = Result("exp_2", 0.02, 0, params)
    db.insert_result(result2)
    entries = db.get_results_for(params)
    assert entries == [result1, result2]
