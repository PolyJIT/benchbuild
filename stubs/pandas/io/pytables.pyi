import numpy as np
from pandas import DataFrame, Index, MultiIndex, Series
from pandas._typing import ArrayLike as ArrayLike, FrameOrSeries as FrameOrSeries
from pandas.core.computation.pytables import PyTablesExpr
from pandas.core.dtypes.generic import ABCExtensionArray
from tables import Col as Col, File as File, Node as Node
from typing import Any, Dict, Hashable, List, Optional, Tuple, Type, Union

Term = PyTablesExpr

class PossibleDataLossError(Exception): ...
class ClosedFileError(Exception): ...
class IncompatibilityWarning(Warning): ...

incompatibility_doc: str

class AttributeConflictWarning(Warning): ...

attribute_conflict_doc: str

class DuplicateWarning(Warning): ...

duplicate_doc: str
performance_doc: str
dropna_doc: str
format_doc: str

def to_hdf(path_or_buf: Any, key: str, value: FrameOrSeries, mode: str=..., complevel: Optional[int]=..., complib: Optional[str]=..., append: bool=..., format: Optional[str]=..., index: bool=..., min_itemsize: Optional[Union[int, Dict[str, int]]]=..., nan_rep: Any=..., dropna: Optional[bool]=..., data_columns: Optional[List[str]]=..., errors: str=..., encoding: str=...) -> Any: ...
def read_hdf(path_or_buf: Any, key: Any=..., mode: str=..., errors: str=..., where: Any=..., start: Optional[int]=..., stop: Optional[int]=..., columns: Any=..., iterator: Any=..., chunksize: Optional[int]=..., **kwargs: Any) -> Any: ...

class HDFStore:
    def __init__(self, path: Any, mode: str=..., complevel: Optional[int]=..., complib: Any=..., fletcher32: bool=..., **kwargs: Any) -> None: ...
    def __fspath__(self): ...
    @property
    def root(self): ...
    @property
    def filename(self): ...
    def __getitem__(self, key: str) -> Any: ...
    def __setitem__(self, key: str, value: Any) -> Any: ...
    def __delitem__(self, key: str) -> Any: ...
    def __getattr__(self, name: str) -> Any: ...
    def __contains__(self, key: str) -> bool: ...
    def __len__(self) -> int: ...
    def __enter__(self): ...
    def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> None: ...
    def keys(self) -> List[str]: ...
    def __iter__(self) -> Any: ...
    def items(self) -> None: ...
    iteritems: Any = ...
    def open(self, mode: str=..., **kwargs: Any) -> Any: ...
    def close(self) -> None: ...
    @property
    def is_open(self) -> bool: ...
    def flush(self, fsync: bool=...) -> Any: ...
    def get(self, key: str) -> Any: ...
    def select(self, key: str, where: Any=..., start: Any=..., stop: Any=..., columns: Any=..., iterator: Any=..., chunksize: Any=..., auto_close: bool=...) -> Any: ...
    def select_as_coordinates(self, key: str, where: Any=..., start: Optional[int]=..., stop: Optional[int]=...) -> Any: ...
    def select_column(self, key: str, column: str, start: Optional[int]=..., stop: Optional[int]=...) -> Any: ...
    def select_as_multiple(self, keys: Any, where: Any=..., selector: Any=..., columns: Any=..., start: Any=..., stop: Any=..., iterator: Any=..., chunksize: Any=..., auto_close: bool=...) -> Any: ...
    def put(self, key: str, value: FrameOrSeries, format: Any=..., index: Any=..., append: Any=..., complib: Any=..., complevel: Optional[int]=..., min_itemsize: Optional[Union[int, Dict[str, int]]]=..., nan_rep: Any=..., data_columns: Optional[List[str]]=..., encoding: Any=..., errors: str=...) -> Any: ...
    def remove(self, key: str, where: Any=..., start: Any=..., stop: Any=...) -> Any: ...
    def append(self, key: str, value: FrameOrSeries, format: Any=..., axes: Any=..., index: Any=..., append: Any=..., complib: Any=..., complevel: Optional[int]=..., columns: Any=..., min_itemsize: Optional[Union[int, Dict[str, int]]]=..., nan_rep: Any=..., chunksize: Any=..., expectedrows: Any=..., dropna: Optional[bool]=..., data_columns: Optional[List[str]]=..., encoding: Any=..., errors: str=...) -> Any: ...
    def append_to_multiple(self, d: Dict, value: Any, selector: Any, data_columns: Any=..., axes: Any=..., dropna: Any=..., **kwargs: Any) -> Any: ...
    def create_table_index(self, key: str, columns: Any=..., optlevel: Optional[int]=..., kind: Optional[str]=...) -> Any: ...
    def groups(self): ...
    def walk(self, where: str = ...) -> None: ...
    def get_node(self, key: str) -> Optional[Node]: ...
    def get_storer(self, key: str) -> Union[GenericFixed, Table]: ...
    def copy(self, file: Any, mode: Any=..., propindexes: bool=..., keys: Any=..., complib: Any=..., complevel: Optional[int]=..., fletcher32: bool=..., overwrite: Any=...) -> Any: ...
    def info(self) -> str: ...

class TableIterator:
    chunksize: Optional[int]
    store: HDFStore
    s: Union[GenericFixed, Table]
    func: Any = ...
    where: Any = ...
    nrows: Any = ...
    start: Any = ...
    stop: Any = ...
    coordinates: Any = ...
    auto_close: Any = ...
    def __init__(self, store: HDFStore, s: Union[GenericFixed, Table], func: Any, where: Any, nrows: Any, start: Any=..., stop: Any=..., iterator: bool=..., chunksize: Optional[int]=..., auto_close: bool=...) -> None: ...
    def __iter__(self) -> Any: ...
    def close(self) -> None: ...
    def get_result(self, coordinates: bool=...) -> Any: ...

class IndexCol:
    is_an_indexable: bool = ...
    is_data_indexable: bool = ...
    name: str
    cname: str
    values: Any = ...
    kind: Any = ...
    typ: Any = ...
    axis: Any = ...
    pos: Any = ...
    freq: Any = ...
    tz: Any = ...
    index_name: Any = ...
    ordered: Any = ...
    table: Any = ...
    meta: Any = ...
    metadata: Any = ...
    def __init__(self, name: str, values: Any=..., kind: Any=..., typ: Any=..., cname: Optional[str]=..., axis: Any=..., pos: Any=..., freq: Any=..., tz: Any=..., index_name: Any=..., ordered: Any=..., table: Any=..., meta: Any=..., metadata: Any=...) -> None: ...
    @property
    def itemsize(self) -> int: ...
    @property
    def kind_attr(self) -> str: ...
    def set_pos(self, pos: int) -> Any: ...
    def __eq__(self, other: Any) -> bool: ...
    def __ne__(self, other: Any) -> bool: ...
    @property
    def is_indexed(self) -> bool: ...
    def convert(self, values: np.ndarray, nan_rep: Any, encoding: str, errors: str) -> Any: ...
    def take_data(self): ...
    @property
    def attrs(self): ...
    @property
    def description(self): ...
    @property
    def col(self): ...
    @property
    def cvalues(self): ...
    def __iter__(self) -> Any: ...
    def maybe_set_size(self, min_itemsize: Optional[Any] = ...) -> None: ...
    def validate_names(self) -> None: ...
    def validate_and_set(self, handler: AppendableTable, append: bool) -> Any: ...
    def validate_col(self, itemsize: Optional[Any] = ...): ...
    def validate_attr(self, append: bool) -> Any: ...
    def update_info(self, info: Any) -> None: ...
    def set_info(self, info: Any) -> None: ...
    def set_attr(self) -> None: ...
    def validate_metadata(self, handler: AppendableTable) -> Any: ...
    def write_metadata(self, handler: AppendableTable) -> Any: ...

class GenericIndexCol(IndexCol):
    @property
    def is_indexed(self) -> bool: ...
    def convert(self, values: np.ndarray, nan_rep: Any, encoding: str, errors: str) -> Any: ...
    def set_attr(self) -> None: ...

class DataCol(IndexCol):
    is_an_indexable: bool = ...
    is_data_indexable: bool = ...
    dtype: Any = ...
    data: Any = ...
    def __init__(self, name: str, values: Any=..., kind: Any=..., typ: Any=..., cname: Any=..., pos: Any=..., tz: Any=..., ordered: Any=..., table: Any=..., meta: Any=..., metadata: Any=..., dtype: Any=..., data: Any=...) -> None: ...
    @property
    def dtype_attr(self) -> str: ...
    @property
    def meta_attr(self) -> str: ...
    def __eq__(self, other: Any) -> bool: ...
    kind: Any = ...
    def set_data(self, data: Union[np.ndarray, ABCExtensionArray]) -> Any: ...
    def take_data(self): ...
    @classmethod
    def get_atom_string(cls, shape: Any, itemsize: Any): ...
    @classmethod
    def get_atom_coltype(cls: Any, kind: str) -> Type[Col]: ...
    @classmethod
    def get_atom_data(cls: Any, shape: Any, kind: str) -> Col: ...
    @classmethod
    def get_atom_datetime64(cls, shape: Any): ...
    @classmethod
    def get_atom_timedelta64(cls, shape: Any): ...
    @property
    def shape(self): ...
    @property
    def cvalues(self): ...
    def validate_attr(self, append: Any) -> None: ...
    def convert(self, values: np.ndarray, nan_rep: Any, encoding: str, errors: str) -> Any: ...
    def set_attr(self) -> None: ...

class DataIndexableCol(DataCol):
    is_data_indexable: bool = ...
    def validate_names(self) -> None: ...
    @classmethod
    def get_atom_string(cls, shape: Any, itemsize: Any): ...
    @classmethod
    def get_atom_data(cls: Any, shape: Any, kind: str) -> Col: ...
    @classmethod
    def get_atom_datetime64(cls, shape: Any): ...
    @classmethod
    def get_atom_timedelta64(cls, shape: Any): ...

class GenericDataIndexableCol(DataIndexableCol): ...

class Fixed:
    pandas_kind: str
    format_type: str = ...
    obj_type: Type[Union[DataFrame, Series]]
    ndim: int
    encoding: str
    parent: HDFStore
    group: Node
    errors: str
    is_table: bool = ...
    def __init__(self, parent: HDFStore, group: Node, encoding: str=..., errors: str=...) -> None: ...
    @property
    def is_old_version(self) -> bool: ...
    @property
    def version(self) -> Tuple[int, int, int]: ...
    @property
    def pandas_type(self): ...
    def set_object_info(self) -> None: ...
    def copy(self): ...
    @property
    def shape(self): ...
    @property
    def pathname(self): ...
    @property
    def attrs(self): ...
    def set_attrs(self) -> None: ...
    def get_attrs(self) -> None: ...
    @property
    def storable(self): ...
    @property
    def is_exists(self) -> bool: ...
    @property
    def nrows(self): ...
    def validate(self, other: Any): ...
    def validate_version(self, where: Optional[Any] = ...): ...
    def infer_axes(self): ...
    def read(self, where: Any=..., columns: Any=..., start: Optional[int]=..., stop: Optional[int]=...) -> Any: ...
    def write(self, **kwargs: Any) -> None: ...
    def delete(self, where: Any=..., start: Optional[int]=..., stop: Optional[int]=...) -> Any: ...

class GenericFixed(Fixed):
    attributes: List[str] = ...
    def validate_read(self, columns: Any, where: Any) -> None: ...
    @property
    def is_exists(self) -> bool: ...
    def set_attrs(self) -> None: ...
    encoding: Any = ...
    errors: Any = ...
    def get_attrs(self) -> None: ...
    def write(self, obj: Any, **kwargs: Any) -> None: ...
    def read_array(self, key: str, start: Optional[int]=..., stop: Optional[int]=...) -> Any: ...
    def read_index(self, key: str, start: Optional[int]=..., stop: Optional[int]=...) -> Index: ...
    def write_index(self, key: str, index: Index) -> Any: ...
    def write_multi_index(self, key: str, index: MultiIndex) -> Any: ...
    def read_multi_index(self, key: str, start: Optional[int]=..., stop: Optional[int]=...) -> MultiIndex: ...
    def read_index_node(self, node: Node, start: Optional[int]=..., stop: Optional[int]=...) -> Index: ...
    def write_array_empty(self, key: str, value: ArrayLike) -> Any: ...
    def write_array(self, key: str, value: ArrayLike, items: Optional[Index]=...) -> Any: ...

class SeriesFixed(GenericFixed):
    pandas_kind: str = ...
    attributes: Any = ...
    name: Optional[Hashable]
    @property
    def shape(self): ...
    def read(self, where: Any=..., columns: Any=..., start: Optional[int]=..., stop: Optional[int]=...) -> Any: ...
    def write(self, obj: Any, **kwargs: Any) -> None: ...

class BlockManagerFixed(GenericFixed):
    attributes: Any = ...
    nblocks: int
    @property
    def shape(self): ...
    def read(self, where: Any=..., columns: Any=..., start: Optional[int]=..., stop: Optional[int]=...) -> Any: ...
    def write(self, obj: Any, **kwargs: Any) -> None: ...

class FrameFixed(BlockManagerFixed):
    pandas_kind: str = ...
    obj_type: Any = ...

class Table(Fixed):
    pandas_kind: str = ...
    format_type: str = ...
    table_type: str
    levels: int = ...
    is_table: bool = ...
    index_axes: List[IndexCol]
    non_index_axes: List[Tuple[int, Any]]
    values_axes: List[DataCol]
    data_columns: List
    metadata: List
    info: Dict
    nan_rep: Any = ...
    def __init__(self, parent: HDFStore, group: Node, encoding: Any=..., errors: str=..., index_axes: Any=..., non_index_axes: Any=..., values_axes: Any=..., data_columns: Any=..., info: Any=..., nan_rep: Any=...) -> None: ...
    @property
    def table_type_short(self) -> str: ...
    def __getitem__(self, c: str) -> Any: ...
    def validate(self, other: Any) -> None: ...
    @property
    def is_multi_index(self) -> bool: ...
    def validate_multiindex(self, obj: Any): ...
    @property
    def nrows_expected(self) -> int: ...
    @property
    def is_exists(self) -> bool: ...
    @property
    def storable(self): ...
    @property
    def table(self): ...
    @property
    def dtype(self): ...
    @property
    def description(self): ...
    @property
    def axes(self): ...
    @property
    def ncols(self) -> int: ...
    @property
    def is_transposed(self) -> bool: ...
    @property
    def data_orientation(self): ...
    def queryables(self) -> Dict[str, Any]: ...
    def index_cols(self): ...
    def values_cols(self) -> List[str]: ...
    def write_metadata(self, key: str, values: np.ndarray) -> Any: ...
    def read_metadata(self, key: str) -> Any: ...
    def set_attrs(self) -> None: ...
    encoding: Any = ...
    errors: Any = ...
    def get_attrs(self) -> None: ...
    def validate_version(self, where: Optional[Any] = ...) -> None: ...
    def validate_min_itemsize(self, min_itemsize: Any) -> None: ...
    def indexables(self): ...
    def create_index(self, columns: Any=..., optlevel: Any=..., kind: Optional[str]=...) -> Any: ...
    @classmethod
    def get_object(cls: Any, obj: Any, transposed: bool) -> Any: ...
    def validate_data_columns(self, data_columns: Any, min_itemsize: Any, non_index_axes: Any): ...
    def process_axes(self, obj: Any, selection: Selection, columns: Any=...) -> Any: ...
    def create_description(self, complib: Any, complevel: Optional[int], fletcher32: bool, expectedrows: Optional[int]) -> Dict[str, Any]: ...
    def read_coordinates(self, where: Any=..., start: Optional[int]=..., stop: Optional[int]=...) -> Any: ...
    def read_column(self, column: str, where: Any=..., start: Optional[int]=..., stop: Optional[int]=...) -> Any: ...

class WORMTable(Table):
    table_type: str = ...
    def read(self, where: Any=..., columns: Any=..., start: Optional[int]=..., stop: Optional[int]=...) -> Any: ...
    def write(self, **kwargs: Any) -> None: ...

class AppendableTable(Table):
    table_type: str = ...
    def write(self, obj: Any, axes: Optional[Any] = ..., append: bool = ..., complib: Optional[Any] = ..., complevel: Optional[Any] = ..., fletcher32: Optional[Any] = ..., min_itemsize: Optional[Any] = ..., chunksize: Optional[Any] = ..., expectedrows: Optional[Any] = ..., dropna: bool = ..., nan_rep: Optional[Any] = ..., data_columns: Optional[Any] = ...) -> None: ...
    def write_data(self, chunksize: Optional[int], dropna: bool=...) -> Any: ...
    def write_data_chunk(self, rows: np.ndarray, indexes: List[np.ndarray], mask: Optional[np.ndarray], values: List[np.ndarray]) -> Any: ...
    def delete(self, where: Any=..., start: Optional[int]=..., stop: Optional[int]=...) -> Any: ...

class AppendableFrameTable(AppendableTable):
    pandas_kind: str = ...
    table_type: str = ...
    ndim: int = ...
    obj_type: Type[Union[DataFrame, Series]] = ...
    @property
    def is_transposed(self) -> bool: ...
    @classmethod
    def get_object(cls: Any, obj: Any, transposed: bool) -> Any: ...
    def read(self, where: Any=..., columns: Any=..., start: Optional[int]=..., stop: Optional[int]=...) -> Any: ...

class AppendableSeriesTable(AppendableFrameTable):
    pandas_kind: str = ...
    table_type: str = ...
    ndim: int = ...
    obj_type: Any = ...
    @property
    def is_transposed(self) -> bool: ...
    @classmethod
    def get_object(cls: Any, obj: Any, transposed: bool) -> Any: ...
    def write(self, obj: Any, data_columns: Optional[Any] = ..., **kwargs: Any): ...
    def read(self, where: Any=..., columns: Any=..., start: Optional[int]=..., stop: Optional[int]=...) -> Series: ...

class AppendableMultiSeriesTable(AppendableSeriesTable):
    pandas_kind: str = ...
    table_type: str = ...
    def write(self, obj: Any, **kwargs: Any): ...

class GenericTable(AppendableFrameTable):
    pandas_kind: str = ...
    table_type: str = ...
    ndim: int = ...
    obj_type: Any = ...
    @property
    def pandas_type(self) -> str: ...
    @property
    def storable(self): ...
    non_index_axes: Any = ...
    nan_rep: Any = ...
    levels: Any = ...
    index_axes: Any = ...
    values_axes: Any = ...
    data_columns: Any = ...
    def get_attrs(self) -> None: ...
    def indexables(self): ...
    def write(self, **kwargs: Any) -> None: ...

class AppendableMultiFrameTable(AppendableFrameTable):
    table_type: str = ...
    obj_type: Any = ...
    ndim: int = ...
    @property
    def table_type_short(self) -> str: ...
    def write(self, obj: Any, data_columns: Optional[Any] = ..., **kwargs: Any): ...
    def read(self, where: Any=..., columns: Any=..., start: Optional[int]=..., stop: Optional[int]=...) -> Any: ...

class Selection:
    table: Any = ...
    where: Any = ...
    start: Any = ...
    stop: Any = ...
    condition: Any = ...
    filter: Any = ...
    terms: Any = ...
    coordinates: Any = ...
    def __init__(self, table: Table, where: Any=..., start: Optional[int]=..., stop: Optional[int]=...) -> None: ...
    def generate(self, where: Any): ...
    def select(self): ...
    def select_coords(self): ...
