from __future__ import annotations

import copy
from dataclasses import dataclass
from typing_extensions import TypedDict

from runexpy.utils import ParamsT


class ResultJSON(TypedDict):
    id: str
    time: float
    exitcode: int
    params: ParamsT


@dataclass(frozen=True)
class Result:
    id: str
    time: float
    exitcode: int
    params: ParamsT

    def __post_init__(self):
        object.__setattr__(self, "params", copy.deepcopy(self.params))

    def to_json(self) -> ResultJSON:
        data: ResultJSON = {
            "id": self.id,
            "time": self.time,
            "exitcode": self.exitcode,
            "params": self.params,
        }
        return data

    @classmethod
    def from_json(cls, params: ResultJSON) -> Result:
        return cls(**params)
