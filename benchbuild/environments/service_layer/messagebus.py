import logging
import typing as tp

from benchbuild.environments.domain import commands, events

LOG = logging.getLogger(__name__)

Message = tp.Union[commands.Command, events.Event]
Messages = tp.List[Message]

#EventHandlerT = tp.Callable[[events.Event, unit_of_work.AbstractUnitOfWork],
EventHandlerT = tp.Callable[[events.Event], tp.Generator[events.Event, None,
                                                         None]]
#CommandHandlerT = tp.Callable[
#    [commands.Command, unit_of_work.AbstractUnitOfWork], str]
CommandHandlerT = tp.Callable[[commands.Command], tp.Generator[events.Event,
                                                               None, None]]

MessageT = tp.Union[tp.Type[commands.Command], tp.Type[events.Event]]

MessageHandler = tp.Callable[[Message], tp.Generator]
MessageHandlers = tp.Dict[MessageT, MessageHandler]

EventHandlers = tp.Dict[tp.Type[events.Event], EventHandlerT]
CommandHandlers = tp.Dict[tp.Type[commands.Command], CommandHandlerT]


def handle(
    cmd_handlers: CommandHandlers, evt_handlers: EventHandlers, message: Message
) -> None:
    """
    Distribute the given message to the required handlers.

    Args:
        message: A command/event to dispatch.
        uow: The unit of work used to handle this bus invocation.
    """
    queue = [message]
    while queue:
        message = queue.pop(0)
        print('BUS MSG TYPE', type(message))
        print('BUS MSG', message)
        if isinstance(message, events.Event):
            _handle_event(evt_handlers, message, queue)
        elif isinstance(message, commands.Command):
            _handle_command(cmd_handlers, message, queue)
        else:
            raise Exception(f'{message} was not an Event or Command')


def _handle_event(
    handlers: EventHandlers, event: events.Event, queue: Messages
) -> None:
    """
    Invokes all registered event handlers for this event.

    Args:
        handlers:
        event: The event to handle
        queue: The message queue to hold  new events/commands that spawn from
               this handler.
    """
    for handler in tp.cast(tp.List[EventHandlerT], handlers[type(event)]):
        try:
            LOG.debug('handling event %s with handler %s', event, handler)
            queue.extend(handler(event))
        except Exception:
            LOG.exception('Exception handling event %s', event)
            continue


def _handle_command(
    handlers: CommandHandlers, command: commands.Command, queue: Messages
) -> None:
    """
    Invokes a registered command handler.

    Args:
        handlers:
        command: The command to handler
        queue: The message queue to hold new events/commands that spawn
               from this handler.
    """
    LOG.debug('handling command %s', command)
    try:
        handler = handlers[type(command)]
        queue.extend(handler(command))
    except Exception:
        LOG.exception('Exception handling command %s', command)
        raise
