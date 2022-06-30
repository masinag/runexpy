from __future__ import annotations

import itertools
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Generator, List, Union

from pyexp.database import Database
from pyexp.result import ParamsT, Result
from pyexp.runner import Runner, SimpleRunner

IterParamsT = Dict[str, Union[int, str, float, List[int], List[str], List[float]]]


@dataclass
class Campaign:
    db: Database = field(compare=False)

    _script: List[str] = field(init=False)
    _campaign_dir: str = field(init=False)
    _default_params: ParamsT = field(init=False)

    def __post_init__(self):
        self._script = self.db.get_script()
        self._campaign_dir = self.db.get_campaign_dir()
        self._default_params = self.db.get_default_params()

    @classmethod
    def new(
        cls,
        script: Union[str, List],
        campaign_dir: str,
        default_params: ParamsT,
        overwrite: bool = False,
    ):
        # Convert paths to be absolute
        campaign_dir = os.path.abspath(campaign_dir)
        if isinstance(script, str):
            script = [script]

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
        self, runner: Runner, param_combinations: Union[IterParamsT, List[IterParamsT]]
    ) -> None:
        missing_simulations = self.get_missing_simulations(param_combinations)
        script = self._script
        for result in runner.run_simulations(
            script, self.db.get_data_dir(), missing_simulations
        ):
            self.write_result(result)

    def get_missing_simulations(
        self, param_combinations: Union[IterParamsT, List[IterParamsT]]
    ) -> Generator[ParamsT, None, None]:
        for comb in self.list_param_combinations(param_combinations):
            if not self.db.count_results_for(comb):
                yield comb

    def write_result(self, result: Result) -> None:
        self.db.insert_result(result)

    def list_param_combinations(self, param_ranges: Dict | list):
        if isinstance(param_ranges, dict):
            param_lists = []
            if not set(param_ranges.keys()).issubset(self._default_params.keys()):
                raise ValueError(
                    "Unknown parameters: "
                    f"{set(param_ranges.keys()) - self._default_params.keys()}"
                )
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
