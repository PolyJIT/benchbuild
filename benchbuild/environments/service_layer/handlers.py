import logging
import typing as tp

from benchbuild.environments.domain import commands, model, events
from benchbuild.environments.service_layer import unit_of_work
from benchbuild.settings import CFG

from . import ensure

LOG = logging.getLogger(__name__)


class EventCollector(tp.Protocol):

    def collect_new_events(self) -> tp.Generator[events.Event, None, None]:
        ...


Message = tp.Union[commands.Command, events.Event]
MessageT = tp.Union[tp.Type[commands.Command], tp.Type[events.Event]]
MessageHandler = tp.Callable[[EventCollector, Message], None]


def bootstrap(handler: MessageHandler, uow: EventCollector):

    def wrapped_handler(msg: Message) -> tp.Generator[events.Event, None, None]:
        handler(uow, msg)
        return uow.collect_new_events()

    return wrapped_handler


def _create_build_container(
    name: str, layers: tp.List[tp.Any], uow: unit_of_work.ImageUnitOfWork
) -> model.Image:
    container = uow.create(name, layers)
    image = container.image
    for layer in image.layers:
        uow.add_layer(container, layer)
    return image


def create_image(
    uow: unit_of_work.ImageUnitOfWork, cmd: commands.CreateImage
) -> None:
    """
    Create a container image using a registry.
    """
    replace = CFG['container']['replace']
    with uow:
        image = uow.registry.find(cmd.name)
        if image and not replace:
            return

        image = _create_build_container(cmd.name, cmd.layers, uow)
        uow.commit()


def create_benchbuild_base(
    uow: unit_of_work.ImageUnitOfWork, cmd: commands.CreateBenchbuildBase
) -> None:
    """
    Create a benchbuild base image.
    """
    replace = CFG['container']['replace']
    with uow:
        image = uow.registry.find(cmd.name)
        if image and not replace:
            return

        image = _create_build_container(cmd.name, cmd.layers, uow)
        uow.commit()


def update_image(
    uow: unit_of_work.ImageUnitOfWork, cmd: commands.UpdateImage
) -> None:
    """
    Update a benchbuild image.
    """
    with uow:
        ensure.image_exists(cmd.name, uow)

        _create_build_container(cmd.name, cmd.layers, uow)
        uow.commit()


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
            uow.registry.temporary_mount(cmd.image, cmd.build_dir, build_dir)
        else:
            LOG.warning(
                'The image misses a configured "BB_BUILD_DIR" variable.'
            )
            LOG.warning('No result artifacts will be copied out.')

        container = uow.create(cmd.image, cmd.name)
        uow.start(container)

    return uow.collect_new_events()


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
