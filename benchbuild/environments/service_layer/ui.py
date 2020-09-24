import typing as tp

from rich.progress import Task, Progress, BarColumn

from benchbuild.environments.domain import events
from benchbuild.environments.service_layer import unit_of_work


def print_image_created(
    event: events.ImageCreated, uow: unit_of_work.AbstractUnitOfWork
) -> None:
    del uow
    __progress__.console.print(f'Building {event.name}')


def print_creating_layer(
    event: events.CreatingLayer, uow: unit_of_work.AbstractUnitOfWork
) -> None:
    del uow
    __progress__.console.print(event.layer)


def print_layer_created(
    event: events.LayerCreated, uow: unit_of_work.AbstractUnitOfWork
) -> None:
    del event
    del uow


def print_image_committed(
    event: events.ImageCommitted, uow: unit_of_work.AbstractUnitOfWork
) -> None:
    del uow
    __progress__.console.print(f'Finished {event.name}')


def print_image_destroyed(
    event: events.ImageCommitted, uow: unit_of_work.AbstractUnitOfWork
) -> None:
    del event
    del uow


def print_container_created(
    event: events.ContainerCreated, uow: unit_of_work.AbstractContainerUOW
) -> None:
    del uow
    __progress__.console.print(
        f'Created {event.name} for image: {event.image_id}'
    )


__progress__ = Progress(
    "[progress.description]{task.description}", BarColumn(),
    "[progress.percentage]{task.percentage:>3.0f}%"
)
__progress__ = Progress()
__tasks__: tp.Dict[str, Task] = {}
