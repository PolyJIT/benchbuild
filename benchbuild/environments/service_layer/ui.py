import rich
from rich.progress import Progress

from benchbuild.environments.domain import events
from benchbuild.environments.service_layer import unit_of_work


def progress_print_image_created(
    event: events.ImageCreated, uow: unit_of_work.AbstractUnitOfWork
) -> None:
    task = __progress__.add_task(event.name, total=event.num_layers - 1)
    __tasks__[event.name] = task


def progress_print_layer_created(
    event: events.LayerCreated, uow: unit_of_work.AbstractUnitOfWork
) -> None:
    __progress__.update(__tasks__[event.name], advance=1)


def progress_print_image_committed(
    event: events.ImageCommitted, uow: unit_of_work.AbstractUnitOfWork
) -> None:
    #rich.print(event)
    pass


def progress_print_image_destroyed(
    event: events.ImageCommitted, uow: unit_of_work.AbstractUnitOfWork
) -> None:
    #rich.print(event)
    pass


__progress__ = Progress()
__tasks__ = {}
