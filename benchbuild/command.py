import typing as tp
from pathlib import Path, PosixPath

from plumbum import local
from plumbum.commands.base import BoundEnvCommand

from benchbuild import source
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
        args_str = " ".join(self._args)

        return f"{env_str} {self._path} {args_str}"


class ProjectCommand:
    project: "benchbuild.project.Project"
    command: Command

    def __init__(self, project: "benchbuild.project.Project", command: Command) -> None:
        self.project = project
        self.command = command
        self.command.path = self._create_project_path(self.command.path)

    def _create_project_path(self, path: Path) -> Path:
        all_sources = source.sources_as_dict(*self.project.source)
        new_parts = []
        for part in path.parts:
            if part in all_sources:
                new_parts.append(self.project.source_of(part))
            else:
                new_parts.append(part)
        return Path(*new_parts)

    @property
    def path(self) -> Path:
        return self.command.path

    def __call__(self, *args: tp.Any):
        self.command.path = self.path

        watched_cmd = watch(wrap(str(self.command.path), self.project))
        return watched_cmd(*args)

    def __repr__(self) -> str:
        return f"ProjectCommand({self.project.name}, {repr(self.command)})"

    def __str__(self) -> str:
        return str(self.command)
