import logger
from typing import (
    Dict,
    List,
    Literal,
)


__all__ = (
    "log",
    "_Data",
    "_TimeFormat",
    "TimeFormatError",
)


class TimeFormatError(Exception):
    ...


log = logger.Logger(1)
_Data = Dict[str, List[int]]
_TimeFormat = Literal[12, 24]
