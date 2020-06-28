import numpy as np
from pandas.core.dtypes.generic import ABCExtensionArray, ABCSeries
from typing import Any, Union

def should_extension_dispatch(left: ABCSeries, right: Any) -> bool: ...
def should_series_dispatch(left: Any, right: Any, op: Any): ...
def dispatch_to_extension_op(op: Any, left: Union[ABCExtensionArray, np.ndarray], right: Any) -> Any: ...
