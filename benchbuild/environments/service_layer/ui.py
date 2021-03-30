import typing as tp

import rich
from rich.progress import Task, Progress, BarColumn

from benchbuild.environments.domain import events
from benchbuild.environments.service_layer import unit_of_work


def print_image_created(
    _: unit_of_work.ImageUnitOfWork, event: events.ImageCreated
) -> None:
    __progress__.console.print(f'Building {event.name}')


def print_layer_created(
    _: unit_of_work.ImageUnitOfWork, event: events.LayerCreated
) -> None:
    rich.print(f'[bold]{event.image_tag}[/bold] {event.name}')


def print_container_created(
    _: unit_of_work.ContainerUnitOfWork, event: events.ContainerCreated
) -> None:
    __progress__.console.print(
        f'Created {event.name} for image: {event.image_id}'
    )


def print_layer_creation_failed(
    _: unit_of_work.ImageUnitOfWork, event: events.LayerCreationFailed
) -> None:
    rich.print((
        f'[bold]{event.name}[/bold] {event.image_tag} '
        f'container: {event.container_id}'
    ))
    rich.print(f'[red]{event.message}[/red]')


def print_container_start_failed(
    _: unit_of_work.ContainerUnitOfWork, event: events.ContainerStartFailed
) -> None:
    rich.print(
        f'[bold]{event.name}[/bold] [red]start of container failed.[/red]\n'
    )
    rich.print(f'container: {event.container_id}')
    rich.print(f'command: {event.message}')


def print_container_started(
    _: unit_of_work.ContainerUnitOfWork, event: events.ContainerStarted
) -> None:
    rich.print(f'[bold]{event.container_id}[/bold] started')


__progress__ = Progress(
    "[progress.description]{task.description}", BarColumn(),
    "[progress.percentage]{task.percentage:>3.0f}%"
)
__progress__ = Progress()
__tasks__: tp.Dict[str, Task] = {}
