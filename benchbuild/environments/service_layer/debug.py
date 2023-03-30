from plumbum import ProcessExecutionError
from rich import print

from benchbuild.environments.adapters.common import bb_buildah
from benchbuild.environments.domain import events
from benchbuild.environments.service_layer import unit_of_work

DEBUG_SESSION_INTRO = """
# Debug Session
The build of **{image_name}** failed.

The failed build state has been stored to **{failed_image_name}**.
You have been placed in a build container to debug this error.
The failed layer command has been:

    {layer_name}

"""


def debug_image_kept(
    uow: unit_of_work.ImageUnitOfWork, event: events.DebugImageKept
) -> None:
    """
    Spawn a debug session of the kept image and provide diagnostics.
    """
    # pylint: disable=import-outside-toplevel
    from rich.markdown import Markdown
    with uow:
        container = uow.create(event.image_name, event.failed_image_name)
        if container is None:
            raise ValueError('Unable to create debug session.')

        print(
            Markdown(
                DEBUG_SESSION_INTRO.format(
                    image_name=event.image_name,
                    failed_image_name=event.failed_image_name,
                    layer_name=event.failed_layer
                )
            )
        )
        run_shell = bb_buildah('run')[container.container_id, '--', '/bin/sh']
        try:
            run_shell.run_fg()
            uow.commit()
        except ProcessExecutionError as ex:
            print(f'Debug session ended with retcode: {ex.retcode}')
            print('[red]No image will be stored![/red]')
