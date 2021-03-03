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
    handler: MessageHandler, uow: unit_of_work.EventCollector
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
    Create a container image using a registry.

    This will first add the layers to our model image. The image layers will
    be spawned by subsequent commands over the messagebus.
    This is *not* an atomic operation.
    """
    replace = CFG['container']['replace']
    with uow:
        image = uow.registry.find(cmd.name)
        if image and not replace:
            return

        from_ = cmd.layers.base
        container = uow.create(cmd.name, from_)
        for layer in cmd.layers:
            uow.add_layer(container, layer)

        if cmd.layers:
            uow.registry.hold(container)
        uow.commit()


def create_layer(
    uow: unit_of_work.ImageUnitOfWork, cmd: commands.CreateLayer
) -> None:
    """
    Spawn a layer in an image container.

    """
    with uow:
        image = uow.registry.find(cmd.name)
        if not image:
            LOG.error("create_layer: image not found")
            return

        container = uow.registry.container(cmd.container_id)
        image.append(cmd.layer)
        uow.registry.add(image, container)
        uow.registry.hold(container)
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
        ensure.image_exists(cmd.image, uow)

        build_dir = uow.registry.env(cmd.image, 'BB_BUILD_DIR')
        if build_dir:
            uow.registry.mount(cmd.image, cmd.build_dir, build_dir)
        else:
            LOG.warning(
                'The image misses a configured "BB_BUILD_DIR" variable.'
            )
            LOG.warning('No result artifacts will be copied out.')

        container = uow.create(cmd.image, cmd.name)
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
        uow.import_image(cmd.image, cmd.in_path)
