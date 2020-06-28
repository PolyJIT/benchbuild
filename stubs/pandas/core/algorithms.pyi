import numpy as np
from pandas import Series
from pandas.core.dtypes.generic import ABCIndex
from typing import Any, Optional, Tuple, Union

def unique(values: Any): ...
unique1d = unique

def isin(comps: Any, values: Any) -> np.ndarray: ...
def factorize(values: Any, sort: bool=..., na_sentinel: int=..., size_hint: Optional[int]=...) -> Tuple[np.ndarray, Union[np.ndarray, ABCIndex]]: ...
def value_counts(values: Any, sort: bool=..., ascending: bool=..., normalize: bool=..., bins: Any=..., dropna: bool=...) -> Series: ...
def duplicated(values: Any, keep: Any=...) -> np.ndarray: ...
def mode(values: Any, dropna: bool=...) -> Series: ...
def rank(values: Any, axis: int=..., method: str=..., na_option: str=..., ascending: bool=..., pct: bool=...) -> Any: ...
def checked_add_with_arr(arr: Any, b: Any, arr_mask: Optional[Any] = ..., b_mask: Optional[Any] = ...): ...
def quantile(x: Any, q: Any, interpolation_method: str = ...): ...

class SelectN:
    obj: Any = ...
    n: Any = ...
    keep: Any = ...
    def __init__(self, obj: Any, n: int, keep: str) -> None: ...
    def nlargest(self): ...
    def nsmallest(self): ...
    @staticmethod
    def is_valid_dtype_n_method(dtype: Any) -> bool: ...

class SelectNSeries(SelectN):
    def compute(self, method: Any): ...

class SelectNFrame(SelectN):
    columns: Any = ...
    def __init__(self, obj: Any, n: int, keep: str, columns: Any) -> None: ...
    def compute(self, method: Any): ...

def take(arr: Any, indices: Any, axis: int=..., allow_fill: bool=..., fill_value: Any=...) -> Any: ...
def take_nd(arr: Any, indexer: Any, axis: int=..., out: Any=..., fill_value: Any=..., allow_fill: bool=...) -> Any: ...
take_1d = take_nd

def take_2d_multi(arr: Any, indexer: Any, fill_value: Any = ...): ...
def searchsorted(arr: Any, value: Any, side: str = ..., sorter: Optional[Any] = ...): ...
def diff(arr: Any, n: int, axis: int=..., stacklevel: Any=...) -> Any: ...
def safe_sort(values: Any, codes: Any=..., na_sentinel: int=..., assume_unique: bool=..., verify: bool=...) -> Union[np.ndarray, Tuple[np.ndarray, np.ndarray]]: ...
