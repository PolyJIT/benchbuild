import logging
import typing as tp

from benchbuild.environments.domain import commands, events

from . import handlers, ui, unit_of_work

LOG = logging.getLogger(__name__)

Message = tp.Union[commands.Command, events.Event]
Messages = tp.List[Message]

EventHandlerT = tp.Callable[[events.Event, unit_of_work.AbstractUnitOfWork],
                            None]
CommandHandlerT = tp.Callable[
    [commands.Command, unit_of_work.AbstractUnitOfWork], str]
CommandResults = tp.List[str]


def handle(message: Message, uow: unit_of_work.AbstractUnitOfWork) -> None:
    """
    Distribute the given message to the required handlers.

    Args:
        message: A command/event to dispatch.
        uow: The unit of work used to handle this bus invocation.

    Returns:
        CommandResults
    """
    queue = [message]
    while queue:
        message = queue.pop(0)
        if isinstance(message, events.Event):
            handle_event(message, queue, uow)
        elif isinstance(message, commands.Command):
            handle_command(message, queue, uow)
        else:
            raise Exception(f'{message} was not an Event or Command')


def handle_event(
    event: events.Event, queue: Messages, uow: unit_of_work.AbstractUnitOfWork
) -> None:
    """
    Invokes all registered event handlers for this event.

    Args:
        event: The event to handle
        queue: The message queue to hold  new events/commands that spawn from
               this handler.
        uow: The unit of work to handle this command.
    """
    for handler in tp.cast(tp.List[EventHandlerT], EVENT_HANDLERS[type(event)]):
        try:
            LOG.debug('handling event %s with handler %s', event, handler)
            handler(event, uow)
            queue.extend(uow.collect_new_events())
        except Exception:
            LOG.exception('Exception handling event %s', event)
            continue


def handle_command(
    command: commands.Command, queue: Messages,
    uow: unit_of_work.AbstractUnitOfWork
) -> None:
    """
    Invokes a registered command handler.

    Args:
        command: The command to handler
        queue: The message queue to hold new events/commands that spawn
               from this handler.
        uow: The unit of work to handle this command.

    Returns:
        str
    """
    LOG.debug('handling command %s', command)
    try:
        handler = tp.cast(CommandHandlerT, COMMAND_HANDLERS[type(command)])
        handler(command, uow)
        queue.extend(uow.collect_new_events())
    except Exception:
        LOG.exception('Exception handling command %s', command)
        raise


EVENT_HANDLERS = {
    events.CreatingLayer: [ui.print_creating_layer],
    events.LayerCreated: [ui.print_layer_created],
    events.ImageCreated: [ui.print_image_created],
    events.ImageCommitted: [ui.print_image_committed],
    events.ImageDestroyed: [ui.print_image_destroyed],
    events.ContainerCreated: [ui.print_container_created]
}

COMMAND_HANDLERS = {
    commands.CreateImage: handlers.create_image,
    commands.UpdateImage: handlers.update_image,
    commands.CreateBenchbuildBase: handlers.create_benchbuild_base,
    commands.RunProjectContainer: handlers.run_project_container
}
