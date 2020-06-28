import numpy as np
from pandas._typing import ArrayLike as ArrayLike
from pandas.core.dtypes.inference import is_array_like as is_array_like, is_bool as is_bool, is_complex as is_complex, is_decimal as is_decimal, is_dict_like as is_dict_like, is_file_like as is_file_like, is_float as is_float, is_integer as is_integer, is_interval as is_interval, is_iterator as is_iterator, is_named_tuple as is_named_tuple, is_nested_list_like as is_nested_list_like, is_number as is_number, is_re as is_re, is_re_compilable as is_re_compilable, is_sequence as is_sequence
from typing import Any, Callable, Union

ensure_float64: Any
ensure_float32: Any

def ensure_float(arr: Any): ...

ensure_uint64: Any
ensure_int64: Any
ensure_int32: Any
ensure_int16: Any
ensure_int8: Any
ensure_platform_int: Any
ensure_object: Any

def ensure_str(value: Union[bytes, Any]) -> str: ...
def ensure_categorical(arr: Any): ...
def ensure_int_or_float(arr: ArrayLike, copy: bool=...) -> np.array: ...
def ensure_python_int(value: Union[int, np.integer]) -> int: ...
def classes(*klasses: Any) -> Callable: ...
def classes_and_not_datetimelike(*klasses: Any) -> Callable: ...
def is_object_dtype(arr_or_dtype: Any) -> bool: ...
def is_sparse(arr: Any) -> bool: ...
def is_scipy_sparse(arr: Any) -> bool: ...
def is_categorical(arr: Any) -> bool: ...
def is_datetime64_dtype(arr_or_dtype: Any) -> bool: ...
def is_datetime64tz_dtype(arr_or_dtype: Any) -> bool: ...
def is_timedelta64_dtype(arr_or_dtype: Any) -> bool: ...
def is_period_dtype(arr_or_dtype: Any) -> bool: ...
def is_interval_dtype(arr_or_dtype: Any) -> bool: ...
def is_categorical_dtype(arr_or_dtype: Any) -> bool: ...
def is_string_dtype(arr_or_dtype: Any) -> bool: ...
def is_period_arraylike(arr: Any) -> bool: ...
def is_datetime_arraylike(arr: Any) -> bool: ...
def is_dtype_equal(source: Any, target: Any) -> bool: ...
def is_any_int_dtype(arr_or_dtype: Any) -> bool: ...
def is_integer_dtype(arr_or_dtype: Any) -> bool: ...
def is_signed_integer_dtype(arr_or_dtype: Any) -> bool: ...
def is_unsigned_integer_dtype(arr_or_dtype: Any) -> bool: ...
def is_int64_dtype(arr_or_dtype: Any) -> bool: ...
def is_datetime64_any_dtype(arr_or_dtype: Any) -> bool: ...
def is_datetime64_ns_dtype(arr_or_dtype: Any) -> bool: ...
def is_timedelta64_ns_dtype(arr_or_dtype: Any) -> bool: ...
def is_datetime_or_timedelta_dtype(arr_or_dtype: Any) -> bool: ...
def is_numeric_v_string_like(a: Any, b: Any): ...
def is_datetimelike_v_numeric(a: Any, b: Any): ...
def needs_i8_conversion(arr_or_dtype: Any) -> bool: ...
def is_numeric_dtype(arr_or_dtype: Any) -> bool: ...
def is_string_like_dtype(arr_or_dtype: Any) -> bool: ...
def is_float_dtype(arr_or_dtype: Any) -> bool: ...
def is_bool_dtype(arr_or_dtype: Any) -> bool: ...
def is_extension_type(arr: Any) -> bool: ...
def is_extension_array_dtype(arr_or_dtype: Any) -> bool: ...
def is_complex_dtype(arr_or_dtype: Any) -> bool: ...
def infer_dtype_from_object(dtype: Any): ...
def pandas_dtype(dtype: Any): ...
