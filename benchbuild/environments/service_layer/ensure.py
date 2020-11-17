import typing as tp

from benchbuild.environments.domain import commands

from . import unit_of_work


class ImageNotFound(Exception):

    def __init__(self, message: tp.Any):
        self.message = message


def image_exists(
    cmd: commands.RunProjectContainer, uow: unit_of_work.AbstractUnitOfWork
) -> None:
    image = uow.registry.get_image(cmd.name)
    if not image:
        raise ImageNotFound(cmd)
