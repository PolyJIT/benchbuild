"""An extensible dictionary."""
from contextlib import contextmanager


def extend_as_list(original_dict, **kwargs):
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
    return new_dict


class ExtensibleDict:
    """A dictionary that provides temporary modification."""

    _current = dict()
    _extender_fn = None

    def __init__(self, extender_fn=None):
        self._extender_fn = extender_fn
        super().__init__()

    @contextmanager
    def __call__(self, *args, extender_fn=None, **kwargs):
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

    def __iter__(self):
        return iter(self._current.items())

    def __len__(self):
        return len(self._current)

    def __contains__(self, name):
        return name in self._current

    def __getitem__(self, name):
        return self._current[name]

    def keys(self):
        return self._current.keys()

    def values(self):
        return self._current.values()

    def items(self):
        return self._current.items()

    def get(self, name, *default):
        return self._current.get(name, *default)

    def __delitem__(self, name):
        del self._current[name]

    def __setitem__(self, name, value):
        self._current[name] = value

    def pop(self, name, *default):
        return self._current.pop(name, *default)

    def clear(self):
        self._current.clear()

    def update(self, extender_fn, *args, **kwargs):
        if extender_fn is not None:
            self._current.update(*args, **extender_fn(self._current, **kwargs))
        else:
            self._current.update(*args, **kwargs)

    def getdict(self):
        return dict((k, str(v)) for k, v in self._current.items())

    def __str__(self):
        return str(self._current)

    def __repr__(self):
        return repr(self._current)
