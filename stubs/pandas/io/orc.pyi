from pandas import DataFrame
from pandas._typing import FilePathOrBuffer as FilePathOrBuffer
from typing import Any, List, Optional

def read_orc(path: FilePathOrBuffer, columns: Optional[List[str]]=..., **kwargs: Any) -> DataFrame: ...
