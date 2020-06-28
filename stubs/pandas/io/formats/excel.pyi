from typing import Any, Callable, Dict, List, Optional, Sequence, Union

class ExcelCell:
    __fields__: Any = ...
    row: Any = ...
    col: Any = ...
    val: Any = ...
    style: Any = ...
    mergestart: Any = ...
    mergeend: Any = ...
    def __init__(self, row: int, col: int, val: Any, style: Any=..., mergestart: Any=..., mergeend: Any=...) -> None: ...

class CSSToExcelConverter:
    inherited: Any = ...
    def __init__(self, inherited: Optional[str]=...) -> None: ...
    compute_css: Any = ...
    def __call__(self, declarations_str: str) -> Dict[str, Dict[str, str]]: ...
    def build_xlstyle(self, props: Dict[str, str]) -> Dict[str, Dict[str, str]]: ...
    VERTICAL_MAP: Any = ...
    def build_alignment(self, props: Any) -> Dict[str, Optional[Union[bool, str]]]: ...
    def build_border(self, props: Dict) -> Dict[str, Dict[str, str]]: ...
    def build_fill(self, props: Dict[str, str]) -> Any: ...
    BOLD_MAP: Any = ...
    ITALIC_MAP: Any = ...
    def build_font(self, props: Any) -> Dict[str, Optional[Union[bool, int, str]]]: ...
    NAMED_COLORS: Any = ...
    def color_to_excel(self, val: Optional[str]) -> Any: ...
    def build_number_format(self, props: Dict) -> Dict[str, Optional[str]]: ...

class ExcelFormatter:
    max_rows: Any = ...
    max_cols: Any = ...
    rowcounter: int = ...
    na_rep: Any = ...
    styler: Any = ...
    style_converter: Any = ...
    df: Any = ...
    columns: Any = ...
    float_format: Any = ...
    index: Any = ...
    index_label: Any = ...
    header: Any = ...
    merge_cells: Any = ...
    inf_rep: Any = ...
    def __init__(self, df: Any, na_rep: str=..., float_format: Optional[str]=..., cols: Optional[Sequence]=..., header: Union[bool, List[str]]=..., index: bool=..., index_label: Union[str, Sequence, None]=..., merge_cells: bool=..., inf_rep: str=..., style_converter: Optional[Callable]=...) -> None: ...
    @property
    def header_style(self): ...
    def get_formatted_cells(self) -> None: ...
    def write(self, writer: Any, sheet_name: str = ..., startrow: int = ..., startcol: int = ..., freeze_panes: Optional[Any] = ..., engine: Optional[Any] = ...) -> None: ...
