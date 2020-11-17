import typing as tp

from benchbuild.environments.domain import commands, model
from benchbuild.environments.service_layer import unit_of_work

from . import ensure


def _create_build_container(
    name: str, layers: tp.List[tp.Any], uow: unit_of_work.AbstractUnitOfWork
) -> model.Image:
    container = uow.create_image(name, layers)
    image = container.image
    for layer in image.layers:
        uow.add_layer(container, layer)
    return image


def create_image(
    cmd: commands.CreateImage, uow: unit_of_work.AbstractUnitOfWork
) -> str:
    """
    Create a container image using a registry.
    """
    with uow:
        image = uow.registry.get_image(cmd.name)
        if image:
            return str(image.name)

        image = _create_build_container(cmd.name, cmd.layers, uow)
        uow.commit()

        return str(image.name)


def update_image(
    cmd: commands.UpdateImage, uow: unit_of_work.AbstractUnitOfWork
) -> str:
    """
    Update a benchbuild image.
    """
    with uow:
        ensure.image_exists(cmd, uow)

        image = _create_build_container(cmd.name, cmd.layers, uow)
        uow.commit()

        return str(image.name)


def create_benchbuild_base(
    cmd: commands.CreateBenchbuildBase, uow: unit_of_work.AbstractUnitOfWork
) -> str:
    """
    Create a benchbuild base image.
    """
    with uow:
        image = uow.registry.get_image(cmd.name)
        if image:
            return str(image.name)

        image = _create_build_container(cmd.name, cmd.layers, uow)
        uow.commit()

        return str(image.name)


def run_project_container(
    cmd: commands.RunProjectContainer, uow: unit_of_work.AbstractUnitOfWork
) -> None:
    with uow:
        ensure.image_exists(cmd, uow)

        build_dir = uow.registry.env(cmd.image, 'BB_BUILD_DIR')
        if build_dir:
            uow.registry.temporary_mount(cmd.image, cmd.build_dir, build_dir)
        container = uow.create_container(cmd.image, cmd.name)
        uow.run_container(container)
