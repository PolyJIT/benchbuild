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


def handle(
    message: Message, uow: unit_of_work.AbstractUnitOfWork
) -> CommandResults:
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


def handle_event(
    event: events.Event, queue: Messages, uow: unit_of_work.AbstractUnitOfWork
) -> None:
    for handler in EVENT_HANDLERS[type(event)]:
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
) -> str:
    LOG.debug('handling command %s', command)
    try:
        handler = COMMAND_HANDLERS[type(command)]
        result = handler(command, uow)
        queue.extend(uow.collect_new_events())
        return result
    except Exception:
        LOG.exception('Exception handling command %s', command)
        raise


EVENT_HANDLERS: tp.Dict[tp.Type[events.Event], tp.List[EventHandlerT]] = {
    events.CreatingLayer: [ui.progress_print_creating_layer],
    events.LayerCreated: [ui.progress_print_layer_created],
    events.ImageCreated: [ui.progress_print_image_created],
    events.ImageCommitted: [ui.progress_print_image_committed],
    events.ImageDestroyed: [ui.progress_print_image_destroyed]
}

COMMAND_HANDLERS: tp.Dict[tp.Type[commands.Command], CommandHandlerT] = {
    commands.CreateImage: handlers.create_image,
    commands.UpdateImage: handlers.update_image,
    commands.CreateBenchbuildBase: handlers.create_benchbuild_base,
    commands.RunContainer: handlers.run_experiment_images
}
