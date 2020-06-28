import numpy as np
from pandas._libs.tslibs import NaTType as NaTType
from pandas._libs.tslibs.period import Period
from pandas.core.arrays import datetimelike as dtl
from pandas.tseries.offsets import Tick
from typing import Any, Optional, Sequence, Union

class PeriodArray(dtl.DatetimeLikeArrayMixin, dtl.DatelikeOps):
    __array_priority__: int = ...
    def __init__(self, values: Any, freq: Optional[Any] = ..., dtype: Optional[Any] = ..., copy: bool = ...) -> None: ...
    def dtype(self): ...
    @property
    def freq(self): ...
    def __array__(self, dtype: Any=...) -> np.ndarray: ...
    def __arrow_array__(self, type: Optional[Any] = ...): ...
    year: Any = ...
    month: Any = ...
    day: Any = ...
    hour: Any = ...
    minute: Any = ...
    second: Any = ...
    weekofyear: Any = ...
    week: Any = ...
    dayofweek: Any = ...
    weekday: Any = ...
    dayofyear: Any = ...
    day_of_year: Any = ...
    quarter: Any = ...
    qyear: Any = ...
    days_in_month: Any = ...
    daysinmonth: Any = ...
    @property
    def is_leap_year(self): ...
    @property
    def start_time(self): ...
    @property
    def end_time(self): ...
    def to_timestamp(self, freq: Optional[Any] = ..., how: str = ...): ...
    def asfreq(self, freq: Optional[Any] = ..., how: str = ...): ...
    def astype(self, dtype: Any, copy: bool = ...): ...

def raise_on_incompatible(left: Any, right: Any): ...
def period_array(data: Sequence[Optional[Period]], freq: Optional[Union[str, Tick]]=..., copy: bool=...) -> PeriodArray: ...
def validate_dtype_freq(dtype: Any, freq: Any): ...
def dt64arr_to_periodarr(data: Any, freq: Any, tz: Optional[Any] = ...): ...
