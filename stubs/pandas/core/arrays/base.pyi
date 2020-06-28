import numpy as np
from pandas._typing import ArrayLike as ArrayLike
from pandas.core.dtypes.dtypes import ExtensionDtype
from pandas.core.dtypes.generic import ABCExtensionArray
from typing import Any, Optional, Sequence, Tuple, Union

def try_cast_to_ea(cls_or_instance: Any, obj: Any, dtype: Optional[Any] = ...): ...

class ExtensionArray:
    def __getitem__(self, item: Any) -> None: ...
    def __setitem__(self, key: Union[int, np.ndarray], value: Any) -> None: ...
    def __len__(self) -> int: ...
    def __iter__(self) -> Any: ...
    def to_numpy(self, dtype: Optional[Any] = ..., copy: bool = ..., na_value: Any = ...): ...
    @property
    def dtype(self) -> ExtensionDtype: ...
    @property
    def shape(self) -> Tuple[int, ...]: ...
    @property
    def size(self) -> int: ...
    @property
    def ndim(self) -> int: ...
    @property
    def nbytes(self) -> int: ...
    def astype(self, dtype: Any, copy: bool = ...): ...
    def isna(self) -> ArrayLike: ...
    def argsort(self, ascending: bool=..., kind: str=..., *args: Any, **kwargs: Any) -> np.ndarray: ...
    def fillna(self, value: Optional[Any] = ..., method: Optional[Any] = ..., limit: Optional[Any] = ...): ...
    def dropna(self): ...
    def shift(self, periods: int=..., fill_value: object=...) -> ABCExtensionArray: ...
    def unique(self): ...
    def searchsorted(self, value: Any, side: str = ..., sorter: Optional[Any] = ...): ...
    def factorize(self, na_sentinel: int=...) -> Tuple[np.ndarray, ABCExtensionArray]: ...
    def repeat(self, repeats: Any, axis: Optional[Any] = ...): ...
    def take(self, indices: Sequence[int], allow_fill: bool=..., fill_value: Any=...) -> ABCExtensionArray: ...
    def copy(self) -> ABCExtensionArray: ...
    def view(self, dtype: Any=...) -> Union[ABCExtensionArray, np.ndarray]: ...
    def ravel(self, order: Any=...) -> ABCExtensionArray: ...

class ExtensionOpsMixin: ...
class ExtensionScalarOpsMixin(ExtensionOpsMixin): ...
