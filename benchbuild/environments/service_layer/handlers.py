from benchbuild.environments.domain import commands, model
from benchbuild.environments.service_layer import unit_of_work


def create_image(cmd: commands.CreateImage,
                 uow: unit_of_work.AbstractUnitOfWork) -> str:
    with uow:
        image = uow.registry.get(cmd.name)
        if image is None:
            image = uow.registry.create(cmd.name, cmd.layers)
            uow.commit()
        return image.name


def update_image(cmd: commands.UpdateImage,
                 uow: unit_of_work.AbstractUnitOfWork) -> str:
    with uow:
        image = uow.registry.create(cmd.name, cmd.layers)
        uow.commit()
        return image.name


def create_benchbuild_base(cmd: commands.CreateBenchbuildBase,
                           uow: unit_of_work.AbstractUnitOfWork) -> str:
    with uow:
        image = uow.registry.get(cmd.name)
        if image is None:
            image = uow.registry.create(cmd.name, cmd.layers)
            uow.commit()
        return image.name
