import abc

import attr

from benchbuild.environments.adapters import repository

from . import buildah


class AbstractUnitOfWork(abc.ABC):
    registry: repository.AbstractRegistry

    def __enter__(self) -> 'AbstractUnitOfWork':
        return self

    def __exit__(self, *args) -> None:
        self.rollback()

    @abc.abstractmethod
    def commit(self) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def rollback(self) -> None:
        raise NotImplementedError


class BuildahUnitOfWork(AbstractUnitOfWork):

    def __init__(self):
        self.registry = repository.BuildahRegistry()

    def __enter__(self) -> AbstractUnitOfWork:
        return super.__enter__()

    def rollback(self) -> None:
        for container in self.registry.containers:
            buildah.destroy_working_container(container)

    def commit(self) -> None:
        for container in self.registry.containers:
            buildah.commit_working_container(container)
