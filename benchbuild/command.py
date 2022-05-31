import typing as tp
from pathlib import Path, PosixPath

from plumbum import local
from plumbum.commands.base import BaseCommand

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
        env: tp.Dict[str, str] = None
    ) -> None:

        self._path = path
        self._output = output
        self._output_param = output_param
        self._args = args
        self._env = env

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

    def exists(self) -> bool:
        return self._path.exists()

    def __getitem__(self, *args: tp.Any) -> 'Command':
        return Command(
            self._path,
            *(*self._args, *args),
            output=self._output,
            env=self._env
        )

    def __call__(self, *args: tp.Any) -> tp.Any:
        if self.exists():
            cmd = local[str(self.path)]
            output_params = \
                    [arg.format(output=self.output) for arg in self._output_param]
            cmd_w_output = cmd[output_params]

            return cmd_w_output(*args)
        return None


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
        assert num_parents >= 2, f'expected 2 parent path elements, got {num_parents}'

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
