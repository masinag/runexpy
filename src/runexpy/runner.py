import os
import subprocess
import sys
import time
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass
from functools import partial
from multiprocessing import Pool
from typing import Iterable, List

from runexpy.result import Result
from runexpy.utils import ParamsT


class Runner(ABC):
    @abstractmethod
    def run_experiments(
        self, script: List[str], dir: str, param_combinations: Iterable[ParamsT]
    ) -> Iterable[Result]:
        pass

    @staticmethod
    def _run_experiment(script, data_dir, params) -> Result:
        run_id = str(uuid.uuid4())
        start_time = time.time()
        run_dir = os.path.join(data_dir, run_id)
        command = script + [f"--{p}={v}" for p, v in params.items()]
        print(" ".join(command), file=sys.stderr)
        os.makedirs(run_dir)
        outfile = os.path.join(run_dir, "stdout")
        errfile = os.path.join(run_dir, "stderr")
        with open(outfile, "w") as stdout, open(errfile, "w") as stderr:
            subprocess.call(
                command,
                cwd=run_dir,
                # env=env,
                stdout=stdout,
                stderr=stderr,
            )
        # subprocess.call(script, params, stdout=...)
        tot_time = time.time() - start_time
        return_code = 0
        return Result(run_id, tot_time, return_code, params)


class SimpleRunner(Runner):
    def run_experiments(
        self, script: List[str], data_dir: str, param_combinations: Iterable[ParamsT]
    ) -> Iterable:
        """Run several simulations"""
        for params in param_combinations:
            yield self._run_experiment(script, data_dir, params)


@dataclass
class ParallelRunner(Runner):
    max_processes: int

    def run_experiments(
        self, script: List[str], data_dir: str, param_combinations: Iterable[ParamsT]
    ) -> Iterable[Result]:
        """Run several simulations in parallel"""
        sim_fn = partial(self._run_experiment, script, data_dir)
        with Pool(self.max_processes) as p:
            results = list(p.map(sim_fn, param_combinations))
        return results
