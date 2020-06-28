from IPython.core.magic import Magics
from typing import Any, Optional

valid_choices: Any

class OutputMagics(Magics):
    def to(self, line: Any, cell: Any, local_ns: Optional[Any] = ...) -> None: ...
