# typings
import os
from typing import Any, Dict, List, Optional, Union

ParamsT = Dict[str, Union[int, str, float]]
DefaultParamsT = Dict[str, Optional[Union[int, str, float]]]
IterParamsT = Dict[
    str, Optional[Union[int, str, float, List[int], List[str], List[float]]]
]


def to_abs_if_path(item: Any) -> str:
    if isinstance(item, str) and os.path.exists(item):
        return os.path.abspath(item)
    else:
        return item
