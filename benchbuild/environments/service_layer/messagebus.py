import logging
import typing as tp

from rich import print

from benchbuild.environments.domain import model
from benchbuild.environments.service_layer import ensure

LOG = logging.getLogger(__name__)

Message = tp.Union[model.Command, model.Event]
Messages = tp.List[Message]

#EventHandlerT = tp.Callable[[events.Event, unit_of_work.AbstractUnitOfWork],
EventHandlerT = tp.Callable[[model.Event], tp.Generator[model.Event, None,
                                                        None]]
#CommandHandlerT = tp.Callable[
#    [commands.Command, unit_of_work.AbstractUnitOfWork], str]
CommandHandlerT = tp.Callable[[model.Command], tp.Generator[model.Event, None,
                                                            None]]

MessageT = tp.Union[tp.Type[model.Command], tp.Type[model.Event]]

MessageHandler = tp.Callable[[Message], tp.Generator]
MessageHandlers = tp.Dict[MessageT, MessageHandler]

EventHandlers = tp.Dict[tp.Type[model.Event], EventHandlerT]
CommandHandlers = tp.Dict[tp.Type[model.Command], CommandHandlerT]


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
        if isinstance(message, model.Event):
            _handle_event(evt_handlers, message, queue)
        elif isinstance(message, model.Command):
            _handle_command(cmd_handlers, message, queue)
        else:
            raise Exception(f'{message} was not an Event or Command')


def _handle_event(
    handlers: EventHandlers, event: model.Event, queue: Messages
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
            queue.extend(handler(event))
        except Exception:
            LOG.exception('Exception handling event %s', event)
            continue


def _handle_command(
    handlers: CommandHandlers, command: model.Command, queue: Messages
) -> None:
    """
    Invokes a registered command handler.

    Args:
        handlers:
        command: The command to handler
        queue: The message queue to hold new events/commands that spawn
               from this handler.
    """
    try:
        handler = handlers[type(command)]
        queue.extend(handler(command))
    except ensure.ImageNotFound as ex:
        print((
            'Command could not be executed, because I could not find a required'
            f' image: {ex}'
        ))
    except Exception:
        LOG.exception('Exception handling command %s', command)
        raise
