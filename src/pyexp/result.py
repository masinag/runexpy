from __future__ import annotations

import copy
from dataclasses import dataclass
from typing import Dict, Union, cast

ParamsT = Dict[str, Union[int, str, float]]


@dataclass(frozen=True)
class Result:
    id: str
    time: float
    exitcode: int
    params: ParamsT

    def __post_init__(self):
        object.__setattr__(self, "params", copy.deepcopy(self.params))

    def to_json(self) -> ParamsT:
        data = {
            "id": self.id,
            "time": self.time,
            "exitcode": self.exitcode,
        }
        data.update(self.params)
        return data

    @classmethod
    def from_json(cls, params: ParamsT) -> Result:
        id = cast(str, params.pop("id"))
        time = cast(float, params.pop("time"))
        exitcode = cast(int, params.pop("exitcode"))
        return cls(id, time, exitcode, params)
