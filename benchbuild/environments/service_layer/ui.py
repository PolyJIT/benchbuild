from rich import print

from benchbuild.environments.domain import events
from benchbuild.environments.service_layer import unit_of_work


def print_image_created(
    _: unit_of_work.ImageUnitOfWork, event: events.ImageCreated
) -> None:
    print(f'Building {event.name}')


def print_image_creation_failed(
    _: unit_of_work.ImageUnitOfWork, event: events.ImageCreationFailed
) -> None:
    print(f'[red]Image creation failed for [bold]{event.name}[/bold][/red]')
    print(f'[red]Reason given: {event.reason}[/red]')


def print_layer_created(
    _: unit_of_work.ImageUnitOfWork, event: events.LayerCreated
) -> None:
    print(f'[bold]{event.image_tag}[/bold] {event.name}')


def print_container_created(
    _: unit_of_work.ContainerUnitOfWork, event: events.ContainerCreated
) -> None:
    print(f'Created {event.name} for image: {event.image_id}')


def print_layer_creation_failed(
    _: unit_of_work.ImageUnitOfWork, event: events.LayerCreationFailed
) -> None:
    print((
        f'[bold]{event.name}[/bold]\n'
        f'[red]Failed to create layer while building {event.image_tag}.[/red]\n'
    ))
    print(f'[red]{event.message}[/red]')


def print_container_start_failed(
    _: unit_of_work.ContainerUnitOfWork, event: events.ContainerStartFailed
) -> None:
    print(f'[bold]{event.name}[/bold] [red]start of container failed.[/red]\n')
    print(f'Container: {event.container_id}')
    print(f'Command: {event.message}')


def print_container_started(
    _: unit_of_work.ContainerUnitOfWork, event: events.ContainerStarted
) -> None:
    print(f'[bold]{event.container_id}[/bold] [green]started[/green]')
