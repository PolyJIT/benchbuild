import typing as tp
from functools import partial

from benchbuild.environments.adapters import buildah, podman
from benchbuild.environments.domain import events, commands
from benchbuild.environments.service_layer import messagebus, ui, handlers
from benchbuild.environments.service_layer import unit_of_work as uow

Messagebus = tp.Callable[[messagebus.Message], None]


def bus() -> Messagebus:
    images_uow = uow.BuildahImageUOW()
    containers_uow = uow.PodmanContainerUOW()

    evt_handlers = {
        events.CreatingLayer: [
            handlers.bootstrap(ui.print_creating_layer, images_uow)
        ],
        events.LayerCreated: [
            handlers.bootstrap(ui.print_layer_created, images_uow)
        ],
        events.ImageCreated: [
            handlers.bootstrap(ui.print_image_created, images_uow)
        ],
        events.ImageCommitted: [
            handlers.bootstrap(ui.print_image_committed, images_uow)
        ],
        events.ImageDestroyed: [
            handlers.bootstrap(ui.print_image_destroyed, images_uow)
        ],
        events.ContainerCreated: [
            handlers.bootstrap(ui.print_container_created, containers_uow)
        ]
    }

    cmd_handlers = {
        commands.CreateImage:
            handlers.bootstrap(handlers.create_image, images_uow),
        commands.UpdateImage:
            handlers.bootstrap(handlers.update_image, images_uow),
        commands.CreateBenchbuildBase:
            handlers.bootstrap(handlers.create_benchbuild_base, images_uow),
        commands.RunProjectContainer:
            handlers.bootstrap(handlers.run_project_container, containers_uow),
        commands.ExportImage:
            handlers.bootstrap(handlers.export_image_handler, images_uow),
        commands.ImportImage:
            handlers.bootstrap(handlers.import_image_handler, images_uow)
    }

    return partial(messagebus.handle, cmd_handlers, evt_handlers)
