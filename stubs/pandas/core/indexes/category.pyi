import numpy as np
from pandas._typing import AnyArrayLike as AnyArrayLike
from pandas.core import accessor
from pandas.core.indexes.base import Index
from pandas.core.indexes.extension import ExtensionIndex
from typing import Any, Optional

class CategoricalIndex(ExtensionIndex, accessor.PandasDelegate):
    codes: np.ndarray
    categories: Index
    def __new__(cls, data: Optional[Any] = ..., categories: Optional[Any] = ..., ordered: Optional[Any] = ..., dtype: Optional[Any] = ..., copy: bool = ..., name: Optional[Any] = ...): ...
    def equals(self, other: Any): ...
    @property
    def inferred_type(self) -> str: ...
    @property
    def values(self): ...
    def __contains__(self, key: Any) -> bool: ...
    def __array__(self, dtype: Any=...) -> np.ndarray: ...
    def astype(self, dtype: Any, copy: bool = ...): ...
    def fillna(self, value: Any, downcast: Optional[Any] = ...): ...
    def is_unique(self) -> bool: ...
    @property
    def is_monotonic_increasing(self): ...
    @property
    def is_monotonic_decreasing(self) -> bool: ...
    def unique(self, level: Optional[Any] = ...): ...
    def duplicated(self, keep: str = ...): ...
    def get_loc(self, key: Any, method: Optional[Any] = ...): ...
    def get_value(self, series: AnyArrayLike, key: Any) -> Any: ...
    def where(self, cond: Any, other: Optional[Any] = ...): ...
    def reindex(self, target: Any, method: Optional[Any] = ..., level: Optional[Any] = ..., limit: Optional[Any] = ..., tolerance: Optional[Any] = ...): ...
    def get_indexer(self, target: Any, method: Optional[Any] = ..., limit: Optional[Any] = ..., tolerance: Optional[Any] = ...): ...
    def get_indexer_non_unique(self, target: Any): ...
    def take_nd(self, *args: Any, **kwargs: Any): ...
    def map(self, mapper: Any): ...
    def delete(self, loc: Any): ...
    def insert(self, loc: Any, item: Any): ...
