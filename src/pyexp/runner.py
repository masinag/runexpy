import subprocess
import time
import uuid
from abc import ABC, abstractmethod
from typing import Generator, Iterable, List

from pyexp.result import ParamsT, Result


class Runner(ABC):
    @abstractmethod
    def run_simulations(
        self, script: str, dir: str, param_combinations: Iterable[ParamsT]
    ) -> Generator[Result, None, None]:
        pass


class SimpleRunner(Runner):
    def run_simulations(
        self, script: str, dir: str, param_combinations: List[ParamsT]
    ) -> Generator[Result, None, None]:
        """Run several simulations"""
        for params in param_combinations:
            run_id = str(uuid.uuid4())
            start_time = time.time()
            # subprocess.call(script, params, stdout=...)
            tot_time = time.time() - start_time
            return_code = 0
            yield Result(run_id, tot_time, return_code, params)
