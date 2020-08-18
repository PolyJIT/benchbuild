import typing as tp

from benchbuild.environments.domain import commands
from benchbuild.environments.service_layer import unit_of_work


def create_project_image(cmd: commands.CreateProjectImage,
                         uow: unit_of_work.AbstractUnitOfWork) -> str:
    with uow:
        image = uow.registry.get(cmd.name)
        if image is None:
            image = uow.registry.create(cmd.name, cmd.layers)
            uow.commit()
        return image.name


def create_experiment_image(cmd: commands.CreateExperimentImage,
                            uow: unit_of_work.AbstractUnitOfWork) -> str:
    with uow:
        image = uow.registry.get(cmd.name)
        if image is None:
            image = uow.registry.create(cmd.name, cmd.layers)
            uow.commit()
        return image.name
