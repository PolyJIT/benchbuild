from pandas._libs.ops_dispatch import maybe_dispatch_ufunc_to_dunder_op as maybe_dispatch_ufunc_to_dunder_op
from pandas.core.ops.array_ops import comp_method_OBJECT_ARRAY as comp_method_OBJECT_ARRAY
from pandas.core.ops.invalid import invalid_comparison as invalid_comparison
from pandas.core.ops.mask_ops import kleene_and as kleene_and, kleene_or as kleene_or, kleene_xor as kleene_xor
from pandas.core.ops.methods import add_flex_arithmetic_methods as add_flex_arithmetic_methods, add_special_arithmetic_methods as add_special_arithmetic_methods
from pandas.core.ops.roperator import rdiv as rdiv
from typing import Any, Optional, Set, Tuple

ARITHMETIC_BINOPS: Set[str]
COMPARISON_BINOPS: Set[str]

def get_op_result_name(left: Any, right: Any): ...
def maybe_upcast_for_op(obj: Any, shape: Tuple[int, ...]) -> Any: ...
def fill_binop(left: Any, right: Any, fill_value: Any): ...
def dispatch_to_series(left: Any, right: Any, func: Any, str_rep: Optional[Any] = ..., axis: Optional[Any] = ...): ...
