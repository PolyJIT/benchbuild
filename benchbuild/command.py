import typing as tp
from pathlib import Path, PosixPath

from plumbum import local
from plumbum.commands.base import BoundEnvCommand

from benchbuild.project import Project
from benchbuild.utils.run import watch
from benchbuild.utils.wrapping import wrap


class SourceRoot(PosixPath):
    pass


class Command:
    _path: Path
    _output: Path
    _output_param: tp.List[str]
    _args: tp.Tuple[tp.Any, ...]
    _env: tp.Dict[str, str]

    def __init__(
        self,
        path: Path,
        *args: tp.Any,
        output: Path = None,
        output_param: tp.List[str] = None,
        **kwargs: str,
    ) -> None:

        self._path = path
        self._args = args if args is not None else []
        self._output = output

        self._output_param = output_param if output_param is not None else []
        self._env = kwargs

    @property
    def name(self) -> str:
        return self._path.name

    @property
    def path(self) -> Path:
        return self._path

    @path.setter
    def path(self, new_path: Path) -> None:
        self._path = new_path

    @property
    def dirname(self) -> Path:
        return self._path.parent

    @property
    def output(self) -> Path:
        return self._output

    def exists(self) -> bool:
        return self._path.exists()

    def env(self, **kwargs: str) -> None:
        self._env.update(kwargs)

    def __getitem__(self, args: tp.Tuple[tp.Any, ...]) -> "Command":
        return Command(self._path, *self._args, *args, output=self._output, **self._env)

    def __call__(self, *args: tp.Any) -> tp.Any:
        assert self.exists()
        cmd_w_output = self.as_plumbum()
        return cmd_w_output(*args)

    def as_plumbum(self) -> BoundEnvCommand:
        assert self.exists()

        cmd = local[str(self.path)]
        cmd_w_args = cmd[self._args]
        output_params = [arg.format(output=self.output) for arg in self._output_param]
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
        env_str = " ".join([f"{k}={v}" for k, v in self._env.items()])
        print(self._args)
        args_str = " ".join(self._args)

        return f"{env_str} {self._path} {args_str}"


class ProjectCommand:
    project: Project
    command: Command

    def __init__(self, project: Project, command: Command) -> None:
        self.project = project
        self.command = command

    @property
    def path(self) -> Path:
        path = self.command.path

        num_parents = len(path.parents)
        assert num_parents >= 2, f"expected 2 parent path elements, got {num_parents}"

        source_name = path.parts[0]
        source_dir = self.project.source_of(source_name)
        if source_dir:
            if isinstance(path, SourceRoot):
                return Path(source_dir) / Path(*path.parts[1:])
        return path

    def __call__(self, *args: tp.Any):
        self.command.path = self.path

        watched_cmd = watch(wrap(str(self.command.path), self.project))
        return watched_cmd(*args)
