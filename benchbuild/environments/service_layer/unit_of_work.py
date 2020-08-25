import abc
import typing as tp

from benchbuild.environments.adapters import repository
from benchbuild.environments.domain import events

from . import buildah


class AbstractUnitOfWork(abc.ABC):
    registry: repository.AbstractRegistry

    def __enter__(self) -> 'AbstractUnitOfWork':
        return self

    def __exit__(self, *args) -> None:
        self.rollback()

    def collect_new_events(self) -> tp.Generator[events.Event, None, None]:
        for image in self.registry.seen:
            while image.events:
                yield image.events.pop(0)

    @abc.abstractmethod
    def commit(self) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def rollback(self) -> None:
        raise NotImplementedError


class BuildahUnitOfWork(AbstractUnitOfWork):

    def __init__(self):
        self.registry = repository.BuildahRegistry()

    def rollback(self) -> None:
        for container in self.registry.containers:
            buildah.destroy_working_container(container)
            buildah.destroy_build_context(container.context)

    def commit(self) -> None:
        for container in self.registry.containers:
            buildah.commit_working_container(container)
            buildah.destroy_build_context(container.context)
