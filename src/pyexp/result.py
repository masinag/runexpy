from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict

ParamsT = Dict[str, Any]


@dataclass()
class Result:
    id: str
    time: float
    exitcode: int
    params: ParamsT

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
        id = params.pop("id")
        time = params.pop("time")
        exitcode = params.pop("exitcode")
        return cls(id, time, exitcode, params)
