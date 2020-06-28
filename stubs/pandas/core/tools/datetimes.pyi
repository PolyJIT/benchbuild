from datetime import datetime
from pandas._libs.tslibs.parsing import DateParseError as DateParseError, parse_time_string as parse_time_string
from pandas._typing import ArrayLike
from pandas.core.dtypes.generic import ABCSeries
from typing import Any, Optional, TypeVar, Union

ArrayConvertible = Union[list, tuple, ArrayLike, ABCSeries]
Scalar = Union[int, float, str]
DatetimeScalar = TypeVar('DatetimeScalar', Scalar, datetime)
DatetimeScalarOrArrayConvertible = Union[DatetimeScalar, list, tuple, ArrayLike, ABCSeries]

def should_cache(arg: ArrayConvertible, unique_share: float=..., check_count: Optional[int]=...) -> bool: ...
def to_datetime(arg: Any, errors: str = ..., dayfirst: bool = ..., yearfirst: bool = ..., utc: Optional[Any] = ..., format: Optional[Any] = ..., exact: bool = ..., unit: Optional[Any] = ..., infer_datetime_format: bool = ..., origin: str = ..., cache: bool = ...): ...
def to_time(arg: Any, format: Optional[Any] = ..., infer_time_format: bool = ..., errors: str = ...): ...
