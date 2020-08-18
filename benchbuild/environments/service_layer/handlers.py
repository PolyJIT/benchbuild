import typing as tp

from benchbuild.environments.domain import commands
from benchbuild.environments.service_layer import unit_of_work
from benchbuild.experiment import Experiment
from benchbuild.project import Project


def create_project_image(cmd: commands.CreateProjectImage,
                         uow: unit_of_work.AbstractUnitOfWork) -> str:
    with uow:
        image = uow.registry.get(cmd.name)
        if image is None:
            # Build the image.
            uow.commit()
        return image.name


def create_experiment_image(cmd: commands.CreateExperimentImage,
                            uow: unit_of_work.AbstractUnitOfWork) -> str:
    with uow:
        image = uow.registry.get(cmd.name)
        if image is None:
            # Build the image.
            uow.commit()
        return image.name
