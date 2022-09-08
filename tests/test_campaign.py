import pytest

from runexpy.campaign import Campaign
from runexpy.runner import SimpleRunner


def test_new_campaign(script, default_params, campaign_dir):
    c = Campaign.new(script, campaign_dir, default_params, False)
    assert c.db.get_script() == script
    assert c.db.get_default_params() == default_params
    assert c.db.get_campaign_dir() == campaign_dir


def test_new_campaign_same_dir_same_params(script, default_params, campaign_dir):
    c1 = Campaign.new(script, campaign_dir, default_params, False)
    c2 = Campaign.new(script, campaign_dir, default_params, False)
    assert c1 == c2


def test_new_campaign_same_dir_diff_params_overwrite(
    script, default_params, campaign_dir
):
    c1 = Campaign.new(script, campaign_dir, default_params, False)
    default_params["x"] = "y"
    c2 = Campaign.new(script, campaign_dir, default_params, True)
    assert c1 != c2
    assert Campaign.load(campaign_dir) == c2


def test_new_campaign_same_dir_diff_params_no_overwrite(
    script, default_params, campaign_dir
):
    _ = Campaign.new(script, campaign_dir, default_params, False)
    default_params["x"] = "y"
    with pytest.raises(ValueError):
        Campaign.new(script, campaign_dir, default_params, False)


def test_load_campaign(script, default_params, campaign_dir):
    c1 = Campaign.new(script, campaign_dir, default_params, False)
    c2 = Campaign.load(campaign_dir)
    assert c1 == c2


def test_load_campaign_no_dir(campaign_dir):
    with pytest.raises(ValueError):
        Campaign.load(campaign_dir)


def test_get_missing_simulations_all(script, default_params, campaign_dir):
    c = Campaign.new(script, campaign_dir, default_params, False)
    runs = [
        {
            "p1": 0,
            "p3": [1, 2, 3],
        },
        {
            "p1": 4,
            "p2": 1,
            "p3": [5, 6],
        },
    ]
    expected_runs = [
        {"p1": 0, "p2": default_params["p2"], "p3": 1},
        {"p1": 0, "p2": default_params["p2"], "p3": 2},
        {"p1": 0, "p2": default_params["p2"], "p3": 3},
        {"p1": 4, "p2": 1, "p3": 5},
        {"p1": 4, "p2": 1, "p3": 6},
    ]

    for expected, result in zip(expected_runs, c.get_missing_experiments(runs)):
        assert expected == result


def test_missing_simulations_some(script, default_params, campaign_dir):
    c = Campaign.new(script, campaign_dir, default_params, False)
    runs = {
        "p1": 0,
        "p3": [1, 2, 3],
    }
    c.run_missing_experiments(SimpleRunner(), runs)

    runs = {
        "p1": 4,
        "p2": 1,
        "p3": [5, 6],
    }
    expected_runs = [
        {"p1": 4, "p2": 1, "p3": 5},
        {"p1": 4, "p2": 1, "p3": 6},
    ]

    for expected, result in zip(expected_runs, c.get_missing_experiments(runs)):
        assert expected == result


def test_missing_simulations_bad_params(script, default_params, campaign_dir):
    c = Campaign.new(script, campaign_dir, default_params, False)
    runs = {
        "p4": 0,
        "p3": [1, 2, 3],
    }

    with pytest.raises(ValueError):
        for _ in c.get_missing_experiments(runs):
            pass


def test_missing_simulations_no_non_default_params(
    script, default_params, campaign_dir
):
    c = Campaign.new(script, campaign_dir, default_params, False)
    runs = {
        "p1": 0,
        "p2": [1, 2, 3],
    }
    with pytest.raises(ValueError):
        for _ in c.get_missing_experiments(runs):
            pass


def test_get_results(script, default_params, campaign_dir):
    c = Campaign.new(script, campaign_dir, default_params, False)
    runs = [
        {"p1": 0, "p2": default_params["p2"], "p3": 1},
        {"p1": 0, "p2": default_params["p2"], "p3": 2},
        {"p1": 0, "p2": default_params["p2"], "p3": 3},
        {"p1": 4, "p2": 1, "p3": 5},
        {"p1": 4, "p2": 1, "p3": 6},
    ]
    c.run_missing_experiments(SimpleRunner(), runs)
    all_results = c.get_all_results()
    assert len(all_results) == len(runs)

    partial_results = c.get_results_for(
        {"p1": 0, "p2": default_params["p2"], "p3": [1, 2]}
    )
    assert len(partial_results) == 2
