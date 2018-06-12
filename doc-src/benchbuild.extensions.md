# Extensions

Extensions are Benchbuild's way to encode composable experiments.
In essence, an extension is just a callable (or Functor) with (optional) additional attributes.
Composability is achieved by storing an arbitrary number of child extensions that can be triggered at any point in the call method.
You can define your own extension by subclassing from ``benchbuild.extensions.Extension``.
Your constructor should handle ``*args`` as child extensions and use ``**kwargs`` for additional
attributes required by the extension.
The ``__call__`` operator of your extension has to deal with arbitrary ``*args`` which are the binary and binary arguments for the experiment. Any additional dynamic parameters used by the extension can
be passed in via ``**kwargs`` again.

## Wrap a binary with a timeout command

As an example, let us wrap an arbitrary binary with a timeout command. For that we need
the ``RunWithTimeout`` extension as shown below:
```python
class RunWithTimeout(Extension):
    def __init__(self, *extensions, limit="10m", **kwargs):
        super(RunWithTimeout, self).__init__(*extensions, **kwargs)
        self.limit = limit

    def __call__(self, binary_command, *args, **kwargs):
        from benchbuild.utils.cmd import timeout
        return self.call_next(
            timeout[self.limit, binary_command],
            *args, **kwargs)
```

On initialization, we set the time limit to "10m" by default.
As soon as this extension is run, we get the binary_command as part of the ``*args`` and wrap
it with the command ``timeout`` with the given time limit.
The wrapped command then serves as the new ``binary_command`` for our child extensions.

Now, when you want to use this extension, you need to compose it with an extension that actually runs
the command afterwards. Benchbuild provides one that controls database tracking at the same time ``benchbuild.extensions.RuntimeExtension``. You should use this one by default as at takes care of
tracking the binary call properly..

```python
import benchbuild.extensions as ext

class RawTimeout(Experiment):
    NAME = 'raw-timeout'
    def actions_for_project(self, project):
        project.runtime_extension = ext.RunWithTimeout(
            ext.RuntimeExtension(project), timeout="2m")
```

If you compose many extensions, you can use the left shift operator to avoid cluttering your code with
a high nesting depth. Note, that you need to reverse the chaining order compared to the nested one, from outermost first to innermost first.
After composition, you have to assign the extension to the ``runtime_extension`` attribute of a ``project``.

```python
import benchbuild.extensions as ext

class RawTimeout(Experiment):
    NAME = 'raw-timeout'
    def actions_for_project(self, project):
        project.runtime_extension = \
               ext.RuntimeExtension(project, self) \
            << ext.RunWithTimeout(timeout="2m")

        ...
```

## API reference

```eval_rst
.. automodule:: benchbuild.extensions
    :members:
    :undoc-members:
    :show-inheritance:
```