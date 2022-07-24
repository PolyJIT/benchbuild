import sys
import typing as tp
from collections.abc import Mapping
from pathlib import Path, PosixPath

from plumbum import local
from plumbum.commands.base import BoundEnvCommand

from benchbuild import source
from benchbuild.settings import CFG
from benchbuild.utils.run import watch
from benchbuild.utils.wrapping import wrap

if tp.TYPE_CHECKING:
    import benchbuild.project.Project  # pylint: disable=unused-import

if sys.version_info <= (3, 8):
    from typing_extensions import Protocol, runtime_checkable
else:
    from typing import Protocol, runtime_checkable


class SourceRoot(PosixPath):
    """Named wrapper around PosixPath."""


@runtime_checkable
class RenderablePath(Protocol):

    def render(self, **kwargs: tp.Any) -> str:
        ...

    def __truediv__(self, rhs: tp.Union[str, 'RenderablePath']) -> 'PathToken':
        ...


@runtime_checkable
class PathRenderStrategy(Protocol):

    def __call__(self, **kwargs: tp.Any) -> Path:
        ...


class NullRenderer:

    def __call__(self, **kwargs: tp.Any) -> Path:
        return Path("/")

    def __str__(self) -> str:
        return str(Path("/"))

    def __repr__(self) -> str:
        return str(self)


class ConstStrRenderer:
    value: str

    def __init__(self, value: str) -> None:
        self.value = value

    def __call__(self, **kwargs: tp.Any) -> Path:
        return Path(self.value)

    def __str__(self) -> str:
        return self.value

    def __repr__(self) -> str:
        return str(self)


class BuilddirRenderer:

    def __call__(
        self,
        project: 'benchbuild.project.Project' = None,
        **kwargs: tp.Any
    ) -> Path:
        assert project is not None
        return Path(project.builddir)

    def __str__(self) -> str:
        return '<BUILD_DIR>'


class SourceRootRenderer:
    local: str

    def __init__(self, local: str) -> None:
        self.local = local

    def __call__(
        self,
        project: 'benchbuild.project.Project' = None,
        **kwargs: tp.Any
    ) -> Path:
        assert project is not None

        src_path = project.source_of(self.local)
        if src_path:
            return Path(src_path)
        return Path(project.build_dir) / self.local


class PathToken:
    """Base class used for command token substitution."""
    renderer: PathRenderStrategy

    left: tp.Optional['PathToken']
    right: tp.Optional['PathToken']

    @classmethod
    def make_token(
        cls, renderer: tp.Optional[PathRenderStrategy] = None
    ) -> 'PathToken':
        if renderer:
            return PathToken(renderer)
        return PathToken(NullRenderer())

    def __init__(
        self,
        renderer: PathRenderStrategy = None,
        left: tp.Optional['PathToken'] = None,
        right: tp.Optional['PathToken'] = None
    ) -> None:

        self.renderer = renderer
        self.left = left
        self.right = right

    @property
    def name(self) -> str:
        return Path(str(self)).name

    @property
    def dirname(self) -> str:
        return Path(str(self)).parent

    def exists(self) -> bool:
        return Path(str(self)).exists()

    def render(self, **kwargs: tp.Any) -> Path:
        token = self.renderer(**kwargs)
        p = Path()

        if self.left:
            p = self.left.render(**kwargs)

        p = p / token

        if self.right:
            p = p / self.right.render(**kwargs)

        return p

    def __truediv__(self, rhs: tp.Union[str, 'PathToken']) -> 'PathToken':
        if isinstance(rhs, str):
            render_str = ConstStrRenderer(rhs)
            rhs_token = PathToken(render_str)
        else:
            rhs_token = rhs

        if self.right is None:
            return PathToken(self.renderer, self.left, rhs_token)
        return PathToken(self.renderer, self.left, self.right / rhs_token)

    def __str__(self) -> str:
        parts = [self.left, str(self.renderer), self.right]
        return str(Path(*[str(part) for part in parts if part is not None]))

    def __repr__(self) -> str:
        return str(self)


def source_root(local: str) -> PathToken:
    return PathToken.make_token(SourceRootRenderer(local))


SourceRoot = source_root


def project_root() -> PathToken:
    return PathToken.make_token(BuilddirRenderer())


ProjectRoot = project_root


class WorkloadSet(Mapping):
    """An immutable set of workload descriptors.

    A WorkloadSet is immutable and usable as a key in a job mapping.
    WorkloadSets support composition through intersection and union.

    Example:
    >>> WorkloadSet(a=1, b=0) & WorkloadSet(a=1)
    WorkloadSet({a=1})
    >>> WorkloadSet(a=1, b=0) & WorkloadSet(c=1)
    WorkloadSet({})
    >>> WorkloadSet(a=1, b=0) | WorkloadSet(c=1)
    WorkloadSet({a=1, b=0, c=1})

    Warning:
    >>> WorkloadSet(a=1) | WorkloadSet(a=2)
    WorkloadSet({a=1, a=2})
    """

    _tags: tp.FrozenSet[tp.Tuple[str, tp.Any]]

    def __init__(self, **kwargs: tp.Any) -> None:
        self._tags = frozenset((k, v) for k, v in kwargs.items())

    def __getitem__(self, key: str) -> tp.Any:
        for k, v in self._tags:
            if k == key:
                return v
        raise KeyError()

    def __iter__(self) -> tp.Iterator[str]:
        return [k for k, _ in self._tags].__iter__()

    def __len__(self) -> int:
        return len(self._tags)

    def __and__(self, rhs: "WorkloadSet") -> "WorkloadSet":
        lhs_t = self._tags
        rhs_t = rhs._tags

        ret = WorkloadSet()
        ret._tags = lhs_t & rhs_t
        return ret

    def __or__(self, rhs: "WorkloadSet") -> "WorkloadSet":
        lhs_t = self._tags
        rhs_t = rhs._tags

        ret = WorkloadSet()
        ret._tags = lhs_t | rhs_t
        return ret

    def __hash__(self) -> int:
        return hash(self._tags)

    def __repr__(self) -> str:
        repr_str = ", ".join([f"{k}={v}" for k, v in sorted(self._tags)])

        return f"WorkloadSet({{{repr_str}}})"


class Command:
    """A command wrapper for benchbuild's commands."""

    _path: PathToken
    _output: tp.Optional[PathToken]
    _output_param: tp.List[str]
    _args: tp.Tuple[tp.Any, ...]
    _env: tp.Dict[str, str]

    def __init__(
        self,
        path: PathToken,
        *args: tp.Any,
        output: tp.Optional[PathToken] = None,
        output_param: tp.Optional[tp.List[str]] = None,
        **kwargs: str,
    ) -> None:

        self._path = path
        self._args = tuple(str(arg) for arg in args)
        self._output = output

        self._output_param = output_param if output_param is not None else []
        self._env = kwargs

    @property
    def name(self) -> str:
        return self._path.name

    @property
    def path(self) -> PathToken:
        return self._path

    @path.setter
    def path(self, new_path: PathToken) -> None:
        self._path = new_path

    @property
    def dirname(self) -> PathToken:
        return self._path.dirname

    @property
    def output(self) -> tp.Optional[PathToken]:
        return self._output

    def exists(self) -> bool:
        return self._path.exists()

    def env(self, **kwargs: str) -> None:
        self._env.update(kwargs)

    def __getitem__(self, args: tp.Tuple[tp.Any, ...]) -> "Command":
        return Command(
            self._path,
            *self._args,
            *args,
            output=self._output,
            output_param=self._output_param,
            **self._env
        )

    def __call__(self, *args: tp.Any, **kwargs: tp.Any) -> tp.Any:
        """Run the command in foreground."""
        assert self.exists()
        cmd_w_output = self.as_plumbum(**kwargs)
        return watch(cmd_w_output)(*args)

    def as_plumbum(self, **kwargs: tp.Any) -> BoundEnvCommand:
        assert self.exists()
        cmd_path = self.path.render(**kwargs)

        cmd = local[str(cmd_path)]
        cmd_w_args = cmd[self._args]
        cmd_w_output = cmd_w_args
        if self.output:
            output_path = self.output.render(**kwargs)
            output_params = [
                arg.format(output=output_path) for arg in self._output_param
            ]
            cmd_w_output = cmd_w_args[output_params]
        cmd_w_env = cmd_w_output.with_env(**self._env)

        return cmd_w_env

    def __repr__(self) -> str:
        repr_str = f"path={self._path}"

        if self._args:
            repr_str += f" args={self._args}"
        if self._env:
            repr_str += f" env={self._env}"
        if self._output:
            repr_str += f" output={self._output}"
        if self._output_param:
            repr_str += f" output_param={self._output_param}"

        return f"Command({repr_str})"

    def __str__(self) -> str:
        env_str = " ".join([f"{k}={str(v)}" for k, v in self._env.items()])
        args_str = " ".join(self._args)

        return f"{env_str} {self._path} {args_str}"


class ProjectCommand:
    """ProjectCommands associate a command to a benchbuild project.

    A project command can wrap the given command with the assigned
    runtime extension.
    If the binary is located inside a subdirectory relative to one of the
    project's sources, you can provide a path relative to it's local
    directory.
    A project command will always try to resolve any reference to a local
    source directory in a command's path.

    A call to a project command will drop the current configuration inside
    the project's build directory and confine the run into the project's
    build directory. The binary will be replaced with a wrapper that
    calls the project's runtime_extension.
    """

    project: "benchbuild.project.Project"
    command: Command

    def __init__(
        self, project: "benchbuild.project.Project", command: Command
    ) -> None:
        self.project = project
        self.command = command

    @property
    def path(self) -> PathToken:
        return self.command.path

    def __call__(self, *args: tp.Any):
        build_dir = self.project.builddir

        CFG.store(Path(build_dir) / ".benchbuild.yml")
        with local.cwd(build_dir):
            cmd_path = self.command.path.render(project=self.project)

            wrap(str(cmd_path), self.project)
            return self.command.__call__(*args, project=self.project)

    def __repr__(self) -> str:
        cmd_path = self.command.path.render(project=self.project)

        return f"ProjectCommand({self.project.name}, {cmd_path})"

    def __str__(self) -> str:
        return str(self.command)


WorkloadIndex = tp.MutableMapping[WorkloadSet, tp.List[Command]]


def filter_workload_index(
    only: WorkloadSet, index: WorkloadIndex
) -> tp.Generator[Command, None, None]:
    keys = {k for k in index if k & only}

    for k in keys:
        for job in index[k]:
            yield job
