import logging
import typing as tp

from benchbuild.environments.domain import commands, model
from benchbuild.environments.service_layer import unit_of_work
from benchbuild.settings import CFG

from . import ensure

LOG = logging.getLogger(__name__)

MessageHandler = tp.Callable[[unit_of_work.EventCollector, model.Message], None]
MessageHandlerWithUOW = tp.Callable[[model.Message], tp.Generator[model.Message,
                                                                  None, None]]


def bootstrap(
    handler, uow: unit_of_work.EventCollector
) -> MessageHandlerWithUOW:
    """
    Bootstrap prepares a message handler with a unit of work.
    """

    def wrapped_handler(
        msg: model.Message
    ) -> tp.Generator[model.Message, None, None]:
        handler(uow, msg)
        return uow.collect_new_events()

    return wrapped_handler


def create_image(
    uow: unit_of_work.ImageUnitOfWork, cmd: commands.CreateImage
) -> None:
    """
    Create a container image using a pre-configured registry.
    """
    replace = CFG['container']['replace']
    with uow:
        image = uow.registry.find(cmd.name)
        if image and not replace:
            return

        container = uow.create(cmd.name, cmd.layers.base)
        if container:
            image = container.image
            image.append(*cmd.layers)

            success = uow.registry.add(image)
            if success:
                uow.commit()


def create_benchbuild_base(
    uow: unit_of_work.ImageUnitOfWork, cmd: commands.CreateBenchbuildBase
) -> None:
    """
    Create a benchbuild base image.
    """
    create_image(uow, commands.CreateImage(cmd.name, cmd.layers))


def run_project_container(
    uow: unit_of_work.ContainerUnitOfWork, cmd: commands.RunProjectContainer
) -> None:
    """
    Run a project container.
    """
    with uow:
        ensure.container_image_exists(cmd.image, uow)

        build_dir = uow.registry.env(cmd.image, 'BB_BUILD_DIR')
        if build_dir:
            uow.registry.mount(cmd.image, cmd.build_dir, build_dir)
        else:
            LOG.warning(
                'The image misses a configured "BB_BUILD_DIR" variable.'
            )
            LOG.warning('No result artifacts will be copied out.')

        container = uow.create(cmd.image, cmd.name, cmd.args)
        uow.start(container)


def export_image_handler(
    uow: unit_of_work.ImageUnitOfWork, cmd: commands.ExportImage
) -> None:
    """
    Export a container image.
    """
    with uow:
        ensure.image_exists(cmd.image, uow)
        image = uow.registry.find(cmd.image)
        if image:
            uow.export_image(image.name, cmd.out_name)


def import_image_handler(
    uow: unit_of_work.ImageUnitOfWork, cmd: commands.ImportImage
) -> None:
    """
    Import a container image.
    """
    with uow:
        uow.import_image(cmd.in_path)


def delete_image_handler(
    uow: unit_of_work.ImageUnitOfWork, cmd: commands.DeleteImage
) -> None:
    """
    Delete a contaienr image.
    """
    with uow:
        image = uow.registry.find(cmd.name)
        if image:
            uow.destroy(image)
