"""
Test transactional boundary with fake unit of works
"""
import typing as tp

from benchbuild.environments.domain import model
from benchbuild.environments.service_layer import unit_of_work as uow
from tests.environments.adapters import repository


class FakeImageUnitOfWork(uow.AbstractImageUnitOfWork):

    def __init__(self):
        self.registry = repository.FakeRegistry()

    def commit(self) -> None:
        pass

    def rollback(self) -> None:
        pass

    def _add_layer(
        self, container: model.Container, layer: model.Layer
    ) -> None:
        pass

    def _create(
        self, tag: str, layers: tp.List[model.Layer]
    ) -> model.Container:
        pass


class FakeContainerUnitOfWork(uow.AbstractContainerUOW):

    def __init__(self):
        self.registry = repository.FakeRegistry()

    def commit(self) -> None:
        pass

    def rollback(self) -> None:
        pass

    def _create(self, image_id: str, container_name: str) -> model.Container:
        pass
