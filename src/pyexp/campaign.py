from __future__ import annotations

import itertools
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Generator

from pyexp.database import Database
from pyexp.result import ParamsT, Result
from pyexp.runner import Runner, SimpleRunner


@dataclass
class Campaign:
    db: Database

    _script: str = field(init=False)
    _dir: str = field(init=False)
    _default_params: ParamsT = field(init=False)

    def __post_init__(self):
        self._script = self.db.get_script()
        self._dir = self.db.get_campaign_dir()
        self._default_params = self.db.get_default_params()

    @classmethod
    def new(
        cls,
        script: str,
        campaign_dir: str,
        default_params: ParamsT,
        overwrite: bool = False,
    ):
        # Convert paths to be absolute
        campaign_dir = os.path.abspath(campaign_dir)

        # Verify if the specified campaign is already available
        if Path(campaign_dir).exists() and not overwrite:
            # Try loading
            campaign = Campaign.load(campaign_dir)
            if campaign.db.get_script() != script:
                raise ValueError("Found database with a different script")
            if campaign.db.get_default_params() != default_params:
                raise ValueError(
                    "Found database with different params\n"
                    f"Old params: {campaign.db.get_default_params()}\n"
                    f"New params: {default_params}"
                )
            return campaign

        db = Database.new(script, default_params, campaign_dir, overwrite)
        return cls(db)

    @classmethod
    def load(cls, campaign_dir):
        # Convert paths to be absolute
        campaign_dir = os.path.abspath(campaign_dir)
        # Read the existing configuration into the new DatabaseManager
        db = Database.load(campaign_dir)
        return cls(db)

    def run_missing_simulations(
        self, runner: Runner, param_combinations: ParamsT
    ) -> None:
        missing_simulations = self.get_missing_simulations(param_combinations)
        script = self._script
        dir = self._dir
        for result in runner.run_simulations(script, dir, missing_simulations):
            self.write_result(result)

    def get_missing_simulations(
        self, param_combinations: ParamsT
    ) -> Generator[ParamsT, None, None]:
        for comb in self.list_param_combinations(param_combinations):
            if not self.db.count_results_for(comb):
                yield comb

    def write_result(self, result: Result) -> None:
        self.db.insert_result(result)

    def list_param_combinations(self, param_ranges: Dict | list):
        if isinstance(param_ranges, dict):
            param_lists = []
            for param, default in self._default_params.items():
                if param not in param_ranges:
                    if default is None:
                        raise ValueError(f"Non-default field {param} has not been set")
                    value = default
                else:
                    value = param_ranges[param]
                values_list = value if isinstance(value, list) else [value]
                param_lists.append(values_list)
            for param_comb in itertools.product(*param_lists):
                yield dict(zip(self._default_params.keys(), param_comb))
        else:
            for x in param_ranges:
                yield from self.list_param_combinations(x)


def main():
    campaign = Campaign.new("simulate", "./campaigns/", {"k": None, "q": None})
    param_combinations = {}
    campaign.run_missing_simulations(SimpleRunner(), param_combinations)
