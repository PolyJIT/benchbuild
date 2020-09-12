import typing as tp

from rich.progress import Task, Progress, BarColumn

from benchbuild.environments.domain import events
from benchbuild.environments.service_layer import unit_of_work


def progress_print_image_created(
    event: events.ImageCreated, uow: unit_of_work.AbstractUnitOfWork
) -> None:
    __progress__.console.print(f'Building {event.name}')
    # __tasks__[event.name
    #          ] = __progress__.add_task(event.name, total=event.num_layers - 1)


def progress_print_creating_layer(
    event: events.CreatingLayer, uow: unit_of_work.AbstractUnitOfWork
) -> None:
    __progress__.console.print(event.layer)


def progress_print_layer_created(
    event: events.LayerCreated, uow: unit_of_work.AbstractUnitOfWork
) -> None:
    # __progress__.update(__tasks__[event.name], advance=1)
    # __progress__.refresh()
    pass


def progress_print_image_committed(
    event: events.ImageCommitted, uow: unit_of_work.AbstractUnitOfWork
) -> None:
    __progress__.console.print(f'Finished {event.name}')


def progress_print_image_destroyed(
    event: events.ImageCommitted, uow: unit_of_work.AbstractUnitOfWork
) -> None:
    # del __tasks__[event.name]
    pass


__progress__ = Progress(
    "[progress.description]{task.description}", BarColumn(),
    "[progress.percentage]{task.percentage:>3.0f}%"
)
__progress__ = Progress()
__tasks__: tp.Dict[str, Task] = {}
