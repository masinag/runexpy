import os
import subprocess
import time
import uuid
from abc import ABC, abstractmethod
from typing import Generator, Iterable, List

from pyexp.result import Result
from pyexp.utils import ParamsT


class Runner(ABC):
    @abstractmethod
    def run_simulations(
        self, script: List[str], dir: str, param_combinations: Iterable[ParamsT]
    ) -> Generator[Result, None, None]:
        pass


class SimpleRunner(Runner):
    def run_simulations(
        self, script: List[str], data_dir: str, param_combinations: List[ParamsT]
    ) -> Generator[Result, None, None]:
        """Run several simulations"""
        for params in param_combinations:
            run_id = str(uuid.uuid4())
            start_time = time.time()
            run_dir = os.path.join(data_dir, run_id)
            command = script + [f"--{p}={v}" for p, v in params.items()]
            os.makedirs(run_dir)
            outfile = os.path.join(run_dir, "stdout")
            errfile = os.path.join(run_dir, "stderr")
            print("Run dir: ", os.path.abspath(run_dir))
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
            yield Result(run_id, tot_time, return_code, params)
