import logging
import typing as tp

from benchbuild.environments.domain import commands, events

from . import handlers, unit_of_work

logger = logging.getLogger(__name__)

Message = tp.Union[commands.Command, events.Event]


def handle(message: Message, uow: unit_of_work.AbstractUnitOfWork):
    results = []
    queue = [message]
    while queue:
        message = queue.pop(0)
        if isinstance(message, events.Event):
            handle_event(message, queue, uow)
        elif isinstance(message, commands.Command):
            cmd_result = handle_command(message, queue, uow)
            results.append(cmd_result)
        else:
            raise Exception(f'{message} was not an Event or Command')
    return results


def handle_event(event: events.Event, queue: tp.List[Message],
                 uow: unit_of_work.AbstractUnitOfWork):
    for handler in EVENT_HANDLERS[type(event)]:
        try:
            logger.debug('handling event %s with handler %s', event, handler)
            handler(event, uow=uow)
            queue.extend(uow.collect_new_events())
        except Exception:
            logger.exception('Exception handling event %s', event)
            continue


def handle_command(command: commands.Command, queue: tp.List[Message],
                   uow: unit_of_work.AbstractUnitOfWork):
    logger.debug('handling command %s', command)
    try:
        handler = COMMAND_HANDLERS[type(command)]
        result = handler(command, uow=uow)
        queue.extend(uow.collect_new_events())
        return result
    except Exception:
        logger.exception('Exception handling command %s', command)
        raise


EVENT_HANDLERS = {events.ContextCreated: [], events.LayerCreated: []}

COMMAND_HANDLERS: tp.Dict[tp.Type[commands.Command], tp.Callable] = {
    commands.CreateProjectImage: handlers.create_project_image,
    commands.CreateExperimentImage: handlers.create_experiment_image
}
