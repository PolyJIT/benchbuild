import numpy as np
from pandas import Interval as Interval
from pandas._libs import Period as Period, Timedelta as Timedelta, Timestamp as Timestamp
from pathlib import Path
from typing import Any, AnyStr, Callable, Collection, Dict, Hashable, IO, List, Mapping, Optional, TypeVar, Union

AnyArrayLike = TypeVar('AnyArrayLike', 'ExtensionArray', 'Index', 'Series', np.ndarray)
ArrayLike = TypeVar('ArrayLike', 'ExtensionArray', np.ndarray)
PythonScalar = Union[str, int, float, bool]
DatetimeLikeScalar = TypeVar('DatetimeLikeScalar', 'Period', 'Timestamp', 'Timedelta')
PandasScalar: Any
Scalar = Union[PythonScalar, PandasScalar]
Dtype: Any
FilePathOrBuffer = Union[str, Path, IO[AnyStr]]
FrameOrSeriesUnion: Any
FrameOrSeries = TypeVar('FrameOrSeries', bound='NDFrame')
Axis = Union[str, int]
Label = Optional[Hashable]
Level = Union[Label, int]
Ordered = Optional[bool]
JSONSerializable = Union[PythonScalar, List, Dict]
Axes = Collection
Renamer = Union[Mapping[Label, Any], Callable[[Label], Label]]
T = TypeVar('T')
