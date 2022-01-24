"""An extensible dictionary."""
import typing as tp
from contextlib import contextmanager


def extend_as_list(
    original_dict: tp.MutableMapping[tp.Any, tp.Any], **kwargs: tp.Any
) -> tp.Dict[tp.Any, tp.Any]:
    """
    Extend values in a map by treating them as a list.
    """
    new_dict = original_dict
    for k, v in kwargs.items():
        if k in original_dict:
            oldv = new_dict[k]
            if not hasattr(oldv, 'extend'):
                oldv = [oldv]

            if isinstance(v, str):
                v = [v]
            if hasattr(v, '__iter__'):
                oldv.extend(v)
            else:
                oldv.append(v)
            new_dict[k] = oldv
        else:
            new_dict[k] = v
    return dict(new_dict)


AnyDictTy = tp.Dict[tp.Any, tp.Any]
ExtenderFnTy = tp.Callable[[AnyDictTy], AnyDictTy]


class ExtensibleDict:
    """A dictionary that provides temporary modification."""

    _current: AnyDictTy = {}
    _extender_fn = None

    def __init__(self, extender_fn: tp.Optional[ExtenderFnTy] = None):
        self._extender_fn = extender_fn
        super().__init__()

    @contextmanager
    def __call__(
        self,
        extender_fn: tp.Optional[ExtenderFnTy] = None,
        **kwargs: tp.Any
    ) -> tp.Generator[None, None, None]:
        """
        A context manager to temporarily modify the content of dict.

        Any time you enter the context the existing dictionary is updated with
        the content of **kwargs. When the context exits the original dictionary
        is restored.

        If ``extender_fn`` is not None the existing content of the dictionary
        is not overwritten, but handed to the extender_fn as first argument in
        addition to the changes supplied in the ``kwargs``.

        The result will be stored temporarily int he dictionary.

        Args:
            extender_fn:
        Returns:
            An updated dictionary.
        """
        previous = self._current.copy()
        if extender_fn is None:
            extender_fn = self._extender_fn

        self.update(extender_fn, **kwargs)
        try:
            yield
        finally:
            self._current = previous

    def __iter__(self) -> tp.Iterator[tp.Tuple[tp.Any, tp.Any]]:
        return iter(self._current.items())

    def __len__(self) -> int:
        return len(self._current)

    def __contains__(self, name: tp.Any) -> bool:
        return name in self._current

    def __getitem__(self, name: str) -> tp.Any:
        return self._current[name]

    def keys(self):
        return self._current.keys()

    def values(self):
        return self._current.values()

    def items(self):
        return self._current.items()

    def get(self, name: tp.Any, *default: tp.Any) -> tp.Any:
        return self._current.get(name, *default)

    def __delitem__(self, name: tp.Any) -> None:
        del self._current[name]

    def __setitem__(self, name: tp.Any, value: tp.Any) -> None:
        self._current[name] = value

    def pop(self, name: tp.Any, *default: tp.Any) -> tp.Any:
        return self._current.pop(name, *default)

    def clear(self) -> None:
        self._current.clear()

    def update(
        self, extender_fn: tp.Optional[ExtenderFnTy], *args: tp.Any,
        **kwargs: tp.Any
    ) -> None:
        if extender_fn is not None:
            self._current.update(*args, **extender_fn(self._current, **kwargs))
        else:
            self._current.update(*args, **kwargs)

    def getdict(self) -> tp.Dict[tp.Any, tp.Any]:
        return dict((k, str(v)) for k, v in self._current.items())

    def __str__(self) -> str:
        return str(self._current)

    def __repr__(self) -> str:
        return repr(self._current)
