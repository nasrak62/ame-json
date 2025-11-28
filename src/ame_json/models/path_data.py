import dataclasses
from typing import Any


@dataclasses.dataclass
class PathData:
    value: Any
    path: list[str]


type PathDataMapper = dict[str, PathData]
