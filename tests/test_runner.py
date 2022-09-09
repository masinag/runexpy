from typing import List

import pytest

from runexpy.database import Database
from runexpy.runner import ParallelRunner, SimpleRunner
from runexpy.utils import ParamsT


@pytest.fixture(scope="module", params=[SimpleRunner(), ParallelRunner(4)])
def runner(request):
    return request.param


def test_runners(runner, script, default_params, campaign_dir):
    db = Database.new(script, default_params, campaign_dir, False)
    param_combinations: List[ParamsT] = [
        {"p1": 0, "p2": 1, "p3": 2},
        {"p1": 3, "p2": 4, "p3": 5},
        {"p1": 6, "p2": 7, "p3": 8},
    ]
    results = list(
        runner.run_experiments(script, db.get_data_dir(), param_combinations)
    )
    assert len(results) == len(param_combinations)

    # check each param_combination has a result
    for params in param_combinations:
        conf_results = [result for result in results if result.params == params]
        assert len(conf_results) == 1

    # check each result has stored 3 files
    for result in results:
        created_files = db.get_files_for(result)
        assert len(created_files) == 3
        assert "stderr" in created_files
        with open(created_files["stderr"]) as f:
            assert f.read() == "stderr\n"
        assert "stdout" in created_files
        with open(created_files["stdout"]) as f:
            assert f.read() == "stdout\n"
        assert "out.txt" in created_files
        with open(created_files["out.txt"]) as f:
            assert f.read() == "file\n"
