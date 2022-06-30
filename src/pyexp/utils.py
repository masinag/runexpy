# typings
from typing import Dict, List, Optional, Union

ParamsT = Dict[str, Union[int, str, float]]
DefaultParamsT = Dict[str, Optional[Union[int, str, float]]]
IterParamsT = Dict[
    str, Optional[Union[int, str, float, List[int], List[str], List[float]]]
]
