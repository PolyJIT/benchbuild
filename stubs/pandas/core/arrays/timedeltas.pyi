from pandas.core.arrays import datetimelike as dtl
from typing import Any, Optional

class TimedeltaArray(dtl.DatetimeLikeArrayMixin, dtl.TimelikeOps):
    __array_priority__: int = ...
    @property
    def dtype(self): ...
    def __init__(self, values: Any, dtype: Any = ..., freq: Optional[Any] = ..., copy: bool = ...) -> None: ...
    def astype(self, dtype: Any, copy: bool = ...): ...
    def sum(self, axis: Any=..., dtype: Any=..., out: Any=..., keepdims: bool=..., initial: Any=..., skipna: bool=..., min_count: int=...) -> Any: ...
    def std(self, axis: Any=..., dtype: Any=..., out: Any=..., ddof: int=..., keepdims: bool=..., skipna: bool=...) -> Any: ...
    def median(self, axis: Any=..., out: Any=..., overwrite_input: bool=..., keepdims: bool=..., skipna: bool=...) -> Any: ...
    def __mul__(self, other: Any): ...
    __rmul__: Any = ...
    def __truediv__(self, other: Any): ...
    def __rtruediv__(self, other: Any): ...
    def __floordiv__(self, other: Any): ...
    def __rfloordiv__(self, other: Any): ...
    def __mod__(self, other: Any): ...
    def __rmod__(self, other: Any): ...
    def __divmod__(self, other: Any): ...
    def __rdivmod__(self, other: Any): ...
    def __neg__(self): ...
    def __pos__(self): ...
    def __abs__(self): ...
    def total_seconds(self): ...
    def to_pytimedelta(self): ...
    days: Any = ...
    seconds: Any = ...
    microseconds: Any = ...
    nanoseconds: Any = ...
    @property
    def components(self): ...

def sequence_to_td64ns(data: Any, copy: bool = ..., unit: str = ..., errors: str = ...): ...
def ints_to_td64ns(data: Any, unit: str = ...): ...
def objects_to_td64ns(data: Any, unit: str = ..., errors: str = ...): ...
