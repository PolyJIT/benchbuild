import logging
import shutil
import sys
import typing as tp
from contextlib import contextmanager
from pathlib import Path
from typing import Protocol, runtime_checkable

from plumbum import local
from plumbum.commands.base import BoundEnvCommand

from benchbuild.settings import CFG
from benchbuild.source.base import primary
from benchbuild.utils.revision_ranges import RevisionRange
from benchbuild.utils.run import watch
from benchbuild.utils.wrapping import wrap

if tp.TYPE_CHECKING:
    import benchbuild.project.Project  # pylint: disable=unused-import

LOG = logging.getLogger(__name__)


@runtime_checkable
class ArgsRenderStrategy(Protocol):
    """
    Rendering strategy protocol for command line argument tokens.
    """

    @property
    def unrendered(self) -> str:
        """
        Returns an unrendered representation of this strategy.
        """

    def rendered(self, **kwargs: tp.Any) -> tp.Tuple[str, ...]:
        """Renders this strategy."""


@runtime_checkable
class PathRenderStrategy(Protocol):
    """
    Rendering strategy protocol for path components.
    """

    @property
    def unrendered(self) -> str:
        """
        Returns an unrendered representation of this strategy.
        """

    def rendered(self, **kwargs: tp.Any) -> Path:
        """Renders this strategy."""


class RootRenderer:
    """
    Renders the root directory.
    """

    @property
    def unrendered(self) -> str:
        return "/"

    def rendered(self, **kwargs: tp.Any) -> Path:
        del kwargs
        return Path("/")

    def __str__(self) -> str:
        return self.unrendered

    def __repr__(self) -> str:
        return str(self)


class ConstStrRenderer:
    """
    Renders a constant string defined by the user.
    """
    value: str

    def __init__(self, value: str) -> None:
        self.value = value

    @property
    def unrendered(self) -> str:
        return self.value

    def rendered(self, **kwargs: tp.Any) -> Path:
        del kwargs
        return Path(self.value)

    def __str__(self) -> str:
        return self.value

    def __repr__(self) -> str:
        return str(self)


class BuilddirRenderer:
    """
    Renders the build directory of the assigned project.
    """

    @property
    def unrendered(self) -> str:
        return "<builddir>"

    def rendered(
        self,
        project: tp.Optional['benchbuild.project.Project'] = None,
        **kwargs: tp.Any
    ) -> Path:
        """
        Render the project's build directory.

        If rendering is not possible, the unrendered representation is
        provided and an error will be loggged.

        Args:
            project: the project to render the build directory from.
        """
        del kwargs

        if project is None:
            LOG.error("Cannot render a build directory without a project.")
            return Path(self.unrendered)

        return Path(project.builddir)

    def __str__(self) -> str:
        return self.unrendered


class SourceRootRenderer:
    """
    Renders the source root of the given local source name.

    The attribute 'local' refers to the local attribute in a project's
    source definition.
    If the local name cannot be found inside the project's source definition,
    it will concatenate the project's builddir with the given name.
    """
    local: str

    def __init__(self, local_name: str) -> None:
        self.local = local_name

    @property
    def unrendered(self) -> str:
        return f"<source_of({self.local})>"

    def rendered(
        self,
        project: tp.Optional['benchbuild.project.Project'] = None,
        **kwargs: tp.Any
    ) -> Path:
        """
        Render the project's source directory.

        If rendering is not possible, the unrendered representation is
        provided and an error will be loggged.

        Args:
            project: the project to render the build directory from.
        """
        del kwargs

        if project is None:
            LOG.error("Cannot render a source directory without a project.")
            return Path(self.unrendered)

        if (src_path := project.source_of(self.local)):
            return Path(src_path)
        return Path(project.builddir) / self.local

    def __str__(self) -> str:
        return self.unrendered


class ArgsToken:
    """
    Base class for tokens that can be rendered into command-line arguments.
    """
    renderer: ArgsRenderStrategy

    @classmethod
    def make_token(
        cls, renderer: ArgsRenderStrategy
    ) -> 'ArgsToken':
        return ArgsToken(renderer)

    def __init__(self, renderer: ArgsRenderStrategy) -> None:
        self.renderer = renderer

    def render(self, **kwargs: tp.Any) -> tp.Tuple[str, ...]:
        """
        Renders the PathToken as a standard pathlib Path.

        Any kwargs will be forwarded to the PathRenderStrategy.
        """
        return self.renderer.rendered(**kwargs)

    def __str__(self) -> str:
        return self.renderer.unrendered

    def __repr__(self) -> str:
        return str(self)


class PathToken:
    """
    Base class used for command token substitution.

    A path token can use similar to pathlib's Path components. However, each
    token can render dynamically based on the given render context.
    """
    renderer: PathRenderStrategy

    left: tp.Optional['PathToken']
    right: tp.Optional['PathToken']

    @classmethod
    def make_token(
        cls, renderer: tp.Optional[PathRenderStrategy] = None
    ) -> 'PathToken':
        if renderer:
            return PathToken(renderer)
        return PathToken(RootRenderer())

    def __init__(
        self,
        renderer: PathRenderStrategy,
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
    def dirname(self) -> Path:
        return Path(str(self)).parent

    def exists(self) -> bool:
        return Path(str(self)).exists()

    def render(self, **kwargs: tp.Any) -> Path:
        """
        Renders the PathToken as a standard pathlib Path.

        Any kwargs will be forwarded to the PathRenderStrategy.
        """
        token = self.renderer.rendered(**kwargs)
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
        parts = [self.left, self.renderer.unrendered, self.right]
        return str(Path(*[str(part) for part in parts if part is not None]))

    def __repr__(self) -> str:
        return str(self)


def source_root(local_name: str) -> PathToken:
    """
    Create a SourceRoot token for the given name.

    Args:
        local_name (str): The source's local name to access.
    """
    return PathToken.make_token(SourceRootRenderer(local_name))


SourceRoot = source_root


def project_root() -> PathToken:
    return PathToken.make_token(BuilddirRenderer())


ProjectRoot = project_root


@runtime_checkable
class SupportsUnwrap(Protocol):
    """
    Support unwrapping a WorkloadSet.

    Unwrapping ensures access to a WorkloadSet from any wrapper object.
    """

    def unwrap(self, project: "benchbuild.project.Project") -> "WorkloadSet":
        ...


class WorkloadSet:
    """An immutable set of workload descriptors.

    A WorkloadSet is immutable and usable as a key in a job mapping.
    WorkloadSets support composition through intersection and union.

    Example:
    >>> WorkloadSet(1, 0) & WorkloadSet(1)
    WorkloadSet({1})
    >>> WorkloadSet(1, 0) & WorkloadSet(2)
    WorkloadSet({})
    >>> WorkloadSet(1, 0) | WorkloadSet(2)
    WorkloadSet({0, 1, 2})
    >>> WorkloadSet(1, 0) | WorkloadSet("1")
    WorkloadSet({0, 1, 1})

    A workload set is not sorted, therefore, requires no comparability between
    inserted values.
    """

    _tags: tp.FrozenSet[tp.Any]

    def __init__(self, *args: tp.Any) -> None:
        self._tags = frozenset(args)

    def __iter__(self) -> tp.Iterator[str]:
        return [k for k, _ in self._tags].__iter__()

    def __contains__(self, v: tp.Any) -> bool:
        return self._tags.__contains__(v)

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
        repr_str = ", ".join([f"{k}" for k in self._tags])

        return f"WorkloadSet({{{repr_str}}})"

    def unwrap(self, project: "benchbuild.project.Project") -> "WorkloadSet":
        """
        Implement the `SupportsUnwrap` protocol.

        WorkloadSets only implement identity.
        """
        del project
        return self


class OnlyIn:
    """
    Provide a filled `WorkloadSet` only if, given revision is inside the range.

    This makes use of the unwrap protocol and returns the given WorkloadSet,
    iff, the Project's revision is included in the range specified by the
    RevisionRange.
    """
    rev_range: RevisionRange
    workload_set: WorkloadSet

    def __init__(
        self, rev_range: RevisionRange, workload_set: WorkloadSet
    ) -> None:
        self.rev_range = rev_range
        self.workload_set = workload_set

    def unwrap(self, project: "benchbuild.project.Project") -> WorkloadSet:
        """
        Provide the store WorkloadSet only if our revision is in the range.
        """
        source = primary(*project.source)
        self.rev_range.init_cache(source.fetch())

        revision = project.version_of_primary
        if revision in set(self.rev_range):
            return self.workload_set
        return WorkloadSet()


ArtefactPath = tp.Union[PathToken, str]


class Command:
    """
    A command wrapper for benchbuild's commands.

    Commands are defined by a path to an executable binary and it's arguments.
    Optional, commands can provide output and output_param parameters to
    declare the Command's output behavior.

    Attributes:
        path: The binary path of the command
        *args: Command arguments.
        output_param: A format string that encodes the output parameter argument
            using the `output` attribute.

            Example: output_param = f"--out {output}".
            BenchBuild will construct the output argument from this.
        output: An optional PathToken to declare an output file of the command.
        label: An optional Label that can be used to name a command.
        creates: A list of PathToken that encodes any artifacts that are
            created by this command.
            This will include the output PathToken automatically. Any
            additional PathTokens provided will be provided for cleanup.
        consumes: A list of PathToken that holds any artifacts that will be
            consumed by this command.
        **kwargs: Any remaining kwargs will be added as environment variables
            to the command.

    Base command path:
    >>> ROOT = PathToken.make_token()
    >>> base_c = Command(ROOT / "bin" / "true")
    >>> base_c
    Command(path=/bin/true)
    >>> str(base_c)
    '/bin/true'

    Test environment representations:
    >>> env_c = Command(ROOT / "bin"/ "true", BB_ENV_TEST=1)
    >>> env_c
    Command(path=/bin/true env={'BB_ENV_TEST': 1})
    >>> str(env_c)
    'BB_ENV_TEST=1 /bin/true'

    Argument representations:
    >>> args_c = Command(ROOT / "bin" / "true", "--arg1", "--arg2")
    >>> args_c
    Command(path=/bin/true args=('--arg1', '--arg2'))
    >>> str(args_c)
    '/bin/true --arg1 --arg2'

    Use str for creates:
    >>> cmd = Command(ROOT / "bin" / "true", creates=["tmp/foo"])
    >>> cmd.creates
    [<builddir>/tmp/foo]

    Use absolute path-str for creates:
    >>> cmd = Command(ROOT / "bin" / "true", creates=["/tmp/foo"])
    >>> cmd.creates
    [/tmp/foo]
    """

    _args: tp.Tuple[tp.Any, ...]
    _env: tp.Dict[str, str]
    _label: tp.Optional[str]
    _output: tp.Optional[PathToken]
    _output_param: tp.Sequence[str]
    _path: PathToken
    _creates: tp.Sequence[PathToken]
    _consumes: tp.Sequence[PathToken]

    def __init__(
        self,
        path: PathToken,
        *args: tp.Any,
        output: tp.Optional[PathToken] = None,
        output_param: tp.Optional[tp.Sequence[str]] = None,
        label: tp.Optional[str] = None,
        creates: tp.Optional[tp.Sequence[ArtefactPath]] = None,
        consumes: tp.Optional[tp.Sequence[ArtefactPath]] = None,
        **kwargs: str,
    ) -> None:

        def _to_pathtoken(token: ArtefactPath) -> PathToken:
            if isinstance(token, str):
                return ProjectRoot() / token
            return token

        self._path = path
        self._args = tuple(args)
        self._output = output

        self._output_param = output_param if output_param is not None else []
        self._label = label
        self._env = kwargs

        _creates = creates if creates is not None else []
        _consumes = consumes if consumes is not None else []

        self._creates = [_to_pathtoken(token) for token in _creates]
        self._consumes = [_to_pathtoken(token) for token in _consumes]

        if output:
            self._creates.append(output)

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
    def dirname(self) -> Path:
        return self._path.dirname

    @property
    def output(self) -> tp.Optional[PathToken]:
        return self._output

    @property
    def creates(self) -> tp.Sequence[PathToken]:
        return self._creates

    @property
    def consumes(self) -> tp.Sequence[PathToken]:
        return self._consumes

    def env(self, **kwargs: str) -> None:
        self._env.update(kwargs)

    @property
    def label(self) -> str:
        return self._label if self._label else self.name

    @label.setter
    def label(self, new_label: str) -> None:
        self._label = new_label

    def __getitem__(self, args: tp.Tuple[tp.Any, ...]) -> "Command":
        return Command(
            self._path,
            *self._args,
            *args,
            output=self._output,
            output_param=self._output_param,
            creates=self._creates,
            consumes=self._consumes,
            **self._env
        )

    def __call__(self, *args: tp.Any, **kwargs: tp.Any) -> tp.Any:
        """Run the command in foreground."""
        cmd_w_output = self.as_plumbum(**kwargs)
        return watch(cmd_w_output)(*args)

    def rendered_args(self, **kwargs: tp.Any) -> tp.Tuple[str, ...]:
        args: tp.List[str] = []

        for arg in self._args:
            if isinstance(arg, ArgsToken):
                args.extend(arg.render(**kwargs))
            else:
                args.append(str(arg))

        return tuple(args)

    def as_plumbum(self, **kwargs: tp.Any) -> BoundEnvCommand:
        """
        Convert this command into a plumbum compatible command.

        This renders all tokens in the command's path and creates a new
        plumbum command with the given parameters and environment.

        Args:
            **kwargs: parameters passed to the path renderers.

        Returns:
            An executable plumbum command.
        """
        cmd_path = self.path.render(**kwargs)
        assert cmd_path.exists(), f"{str(cmd_path)} doesn't exist!"

        cmd = local[str(cmd_path)]
        cmd_w_args = cmd[self.rendered_args(**kwargs)]
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

        if self._label:
            repr_str = f"{self._label} {repr_str}"
        if self._args:
            repr_str += f" args={tuple(str(arg) for arg in self._args)}"
        if self._env:
            repr_str += f" env={self._env}"
        if self._output:
            repr_str += f" output={self._output}"
        if self._output_param:
            repr_str += f" output_param={self._output_param}"

        return f"Command({repr_str})"

    def __str__(self) -> str:
        env_str = " ".join([f"{k}={str(v)}" for k, v in self._env.items()])
        args_str = " ".join(tuple(str(arg) for arg in self._args))

        command_str = f"{self._path}"
        if env_str:
            command_str = f"{env_str} {command_str}"
        if args_str:
            command_str = f"{command_str} {args_str}"
        if self._label:
            command_str = f"{self._label} {command_str}"
        return command_str


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
    def path(self) -> Path:
        return self.command.path.render(project=self.project)

    def __call__(self, *args: tp.Any):
        build_dir = self.project.builddir

        CFG.store(Path(build_dir) / ".benchbuild.yml")
        with local.cwd(build_dir):
            cmd_path = self.path

            wrap(str(cmd_path), self.project)
            return self.command.__call__(*args, project=self.project)

    def __repr__(self) -> str:
        return f"ProjectCommand({self.project.name}, {self.path})"

    def __str__(self) -> str:
        return str(self.command)


def _is_relative_to(p: Path, other: Path) -> bool:
    return p.is_relative_to(other)


def _default_prune(project_command: ProjectCommand) -> None:
    command = project_command.command
    project = project_command.project
    builddir = Path(str(project.builddir))

    for created in command.creates:
        created_path = created.render(project=project)
        if created_path.exists() and created_path.is_file():
            if not _is_relative_to(created_path, builddir):
                LOG.error("Pruning outside project builddir was rejected!")
            else:
                created_path.unlink()


def _default_backup(
    project_command: ProjectCommand,
    _suffix: str = ".benchbuild_backup"
) -> tp.List[Path]:
    command = project_command.command
    project = project_command.project
    builddir = Path(str(project.builddir))

    backup_destinations: tp.List[Path] = []
    for backup in command.consumes:
        backup_path = backup.render(project=project)
        backup_destination = backup_path.with_suffix(_suffix)
        if backup_path.exists():
            if not _is_relative_to(backup_path, builddir):
                LOG.error("Backup outside project builddir was rejected!")
            else:
                shutil.copy(backup_path, backup_destination)
                backup_destinations.append(backup_destination)

    return backup_destinations


def _default_restore(backup_paths: tp.List[Path]) -> None:
    for backup_path in backup_paths:
        original_path = backup_path.with_suffix("")
        if not original_path.exists() and backup_path.exists():
            backup_path.rename(original_path)

        if not original_path.exists() and not backup_path.exists():
            LOG.error("No backup to restore from. %s missing", str(backup_path))

        if original_path.exists() and backup_path.exists():
            LOG.error("%s not consumed, ignoring backup", str(original_path))


class PruneFn(Protocol):
    """Prune function protocol."""

    def __call__(self, project_command: ProjectCommand) -> None:
        ...


class BackupFn(Protocol):
    """Backup callback function protocol."""

    def __call__(self,
                 project_command: ProjectCommand,
                 _suffix: str = ...) -> tp.List[Path]:
        ...


class RestoreFn(Protocol):
    """Restore function protocol."""

    def __call__(self, backup_paths: tp.List[Path]) -> None:
        ...


@contextmanager
def cleanup(
    project_command: ProjectCommand,
    backup: BackupFn = _default_backup,
    restore: RestoreFn = _default_restore,
    prune: PruneFn = _default_prune
):
    """
    Encapsulate a command in automatic backup, restore and prune.

    This will wrap a ProjectCommand inside a contextmanager. All consumed
    files inside the project's build directory will be backed up by benchbuild.
    You can then run your command as usual.
    When you leave the context, all created paths are deleted and all consumed
    paths restored.
    """

    backup_paths = backup(project_command)
    yield project_command
    prune(project_command)
    restore(backup_paths)


WorkloadIndex = tp.MutableMapping[WorkloadSet, tp.List[Command]]


def unwrap(
    index: WorkloadIndex, project: 'benchbuild.project.Project'
) -> WorkloadIndex:
    """
    Unwrap all keys in a workload index.

    'Empty' WorkloadSets will be removed. A WorkloadSet is empty, if it's
    boolean representation evaluates to `False`.
    """
    return {k: v for k, v in index.items() if bool(k.unwrap(project))}


def filter_workload_index(
    only: tp.Optional[WorkloadSet], index: WorkloadIndex
) -> tp.Generator[tp.List[Command], None, None]:
    """
    Yield only commands from the index that match the filter.

    This removes all command lists from the index not matching `only`.
    """

    keys = [k for k in index if k and ((only and (k & only)) or (not only))]
    for k in keys:
        yield index[k]
