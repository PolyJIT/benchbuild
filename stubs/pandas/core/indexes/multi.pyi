import numpy as np
from pandas._libs import index as libindex
from pandas.core.indexes.base import Index
from typing import Any, Hashable, Optional, Sequence, Union

class MultiIndexUIntEngine(libindex.BaseMultiIndexCodesEngine, libindex.UInt64Engine): ...
class MultiIndexPyIntEngine(libindex.BaseMultiIndexCodesEngine, libindex.ObjectEngine): ...

class MultiIndex(Index):
    rename: Any = ...
    def __new__(cls: Any, levels: Any=..., codes: Any=..., sortorder: Any=..., names: Any=..., dtype: Any=..., copy: Any=..., name: Any=..., verify_integrity: bool=..., _set_identity: bool=...) -> Any: ...
    @classmethod
    def from_arrays(cls, arrays: Any, sortorder: Optional[Any] = ..., names: Any = ...): ...
    @classmethod
    def from_tuples(cls, tuples: Any, sortorder: Optional[Any] = ..., names: Optional[Any] = ...): ...
    @classmethod
    def from_product(cls, iterables: Any, sortorder: Optional[Any] = ..., names: Any = ...): ...
    @classmethod
    def from_frame(cls, df: Any, sortorder: Optional[Any] = ..., names: Optional[Any] = ...): ...
    @property
    def shape(self): ...
    @property
    def array(self) -> None: ...
    def levels(self): ...
    def set_levels(self, levels: Any, level: Optional[Any] = ..., inplace: bool = ..., verify_integrity: bool = ...): ...
    @property
    def codes(self): ...
    def set_codes(self, codes: Any, level: Optional[Any] = ..., inplace: bool = ..., verify_integrity: bool = ...): ...
    def copy(self, names: Optional[Any] = ..., dtype: Optional[Any] = ..., levels: Optional[Any] = ..., codes: Optional[Any] = ..., deep: bool = ..., _set_identity: bool = ..., **kwargs: Any): ...
    def __array__(self, dtype: Any=...) -> np.ndarray: ...
    def view(self, cls: Optional[Any] = ...): ...
    def __contains__(self, key: Any) -> bool: ...
    def dtype(self) -> np.dtype: ...
    def memory_usage(self, deep: bool=...) -> int: ...
    def nbytes(self) -> int: ...
    def format(self, space: int = ..., sparsify: Optional[Any] = ..., adjoin: bool = ..., names: bool = ..., na_rep: Optional[Any] = ..., formatter: Optional[Any] = ...): ...
    def __len__(self) -> int: ...
    names: Any = ...
    def inferred_type(self) -> str: ...
    @property
    def values(self): ...
    def is_monotonic_increasing(self) -> bool: ...
    def is_monotonic_decreasing(self) -> bool: ...
    def duplicated(self, keep: str = ...): ...
    def fillna(self, value: Optional[Any] = ..., downcast: Optional[Any] = ...) -> None: ...
    def dropna(self, how: str = ...): ...
    def get_value(self, series: Any, key: Any): ...
    def get_level_values(self, level: Any): ...
    def unique(self, level: Optional[Any] = ...): ...
    def to_frame(self, index: bool = ..., name: Optional[Any] = ...): ...
    def to_flat_index(self): ...
    @property
    def is_all_dates(self) -> bool: ...
    def is_lexsorted(self) -> bool: ...
    def lexsort_depth(self): ...
    def remove_unused_levels(self): ...
    @property
    def nlevels(self) -> int: ...
    @property
    def levshape(self): ...
    def __reduce__(self): ...
    def __getitem__(self, key: Any): ...
    def take(self, indices: Any, axis: int = ..., allow_fill: bool = ..., fill_value: Optional[Any] = ..., **kwargs: Any): ...
    def append(self, other: Any): ...
    def argsort(self, *args: Any, **kwargs: Any): ...
    def repeat(self, repeats: Any, axis: Optional[Any] = ...): ...
    def where(self, cond: Any, other: Optional[Any] = ...) -> None: ...
    def drop(self, codes: Any, level: Optional[Any] = ..., errors: str = ...): ...
    def swaplevel(self, i: int = ..., j: int = ...): ...
    def reorder_levels(self, order: Any): ...
    def sortlevel(self, level: int = ..., ascending: bool = ..., sort_remaining: bool = ...): ...
    def get_indexer(self, target: Any, method: Optional[Any] = ..., limit: Optional[Any] = ..., tolerance: Optional[Any] = ...): ...
    def get_indexer_non_unique(self, target: Any): ...
    def reindex(self, target: Any, method: Optional[Any] = ..., level: Optional[Any] = ..., limit: Optional[Any] = ..., tolerance: Optional[Any] = ...): ...
    def get_slice_bound(self, label: Union[Hashable, Sequence[Hashable]], side: str, kind: str) -> int: ...
    def slice_locs(self, start: Optional[Any] = ..., end: Optional[Any] = ..., step: Optional[Any] = ..., kind: Optional[Any] = ...): ...
    def get_loc(self, key: Any, method: Optional[Any] = ...): ...
    def get_loc_level(self, key: Any, level: Any=..., drop_level: bool=...) -> Any: ...
    def get_locs(self, seq: Any): ...
    def truncate(self, before: Optional[Any] = ..., after: Optional[Any] = ...): ...
    def equals(self, other: Any) -> bool: ...
    def equal_levels(self, other: Any): ...
    def union(self, other: Any, sort: Optional[Any] = ...): ...
    def intersection(self, other: Any, sort: bool = ...): ...
    def difference(self, other: Any, sort: Optional[Any] = ...): ...
    def astype(self, dtype: Any, copy: bool = ...): ...
    def insert(self, loc: Any, item: Any): ...
    def delete(self, loc: Any): ...
    def isin(self, values: Any, level: Optional[Any] = ...): ...

def maybe_droplevels(index: Any, key: Any): ...
