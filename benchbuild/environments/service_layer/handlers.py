import typing as tp

from benchbuild.environments.domain import commands, model
from benchbuild.environments.service_layer import unit_of_work


def _create_container(
    name: str, layers: tp.List[tp.Any],
    uow: unit_of_work.AbstractImageUnitOfWork
) -> model.Image:
    container = uow.create(name, layers)
    image = container.image
    for layer in image.layers:
        uow.add_layer(container, layer)
    return image


def create_image(
    cmd: commands.CreateImage, uow: unit_of_work.AbstractImageUnitOfWork
) -> str:
    with uow:
        image = uow.registry.get(cmd.name)
        if image:
            return str(image.name)

        image = _create_container(cmd.name, cmd.layers, uow)
        uow.commit()

        return str(image.name)


def update_image(
    cmd: commands.UpdateImage, uow: unit_of_work.AbstractImageUnitOfWork
) -> str:
    with uow:
        image = _create_container(cmd.name, cmd.layers, uow)
        uow.commit()

        return str(image.name)


def create_benchbuild_base(
    cmd: commands.CreateBenchbuildBase,
    uow: unit_of_work.AbstractImageUnitOfWork
) -> str:
    with uow:
        image = uow.registry.get(cmd.name)
        if image:
            return str(image.name)

        image = _create_container(cmd.name, cmd.layers, uow)
        uow.commit()

        return str(image.name)


def run_experiment_images(
    cmd: commands.RunContainer, uow: unit_of_work.AbstractContainerUOW
) -> None:
    if not isinstance(uow, unit_of_work.PodmanUnitOfWork):
        raise TypeError('I need a Podman UOW to complete this request.')

    with uow:
        container = uow.create(cmd.image, cmd.name)
        uow.run_container(container)
