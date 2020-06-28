import numpy as np
from pandas._libs.tslibs import Timestamp
from pandas.tseries.offsets import DateOffset
from typing import Tuple

def generate_regular_range(start: Timestamp, end: Timestamp, periods: int, freq: DateOffset) -> Tuple[np.ndarray, str]: ...
