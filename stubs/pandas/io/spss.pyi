from pandas.core.api import DataFrame
from pathlib import Path
from typing import Optional, Sequence, Union

def read_spss(path: Union[str, Path], usecols: Optional[Sequence[str]]=..., convert_categoricals: bool=...) -> DataFrame: ...
