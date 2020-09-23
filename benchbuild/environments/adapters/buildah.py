import json
import os
import typing as tp

from plumbum import local
from plumbum.commands.base import BaseCommand
from plumbum.path.utils import delete

from benchbuild.environments.domain import model
from benchbuild.settings import CFG
from benchbuild.utils.cmd import buildah, mktemp

BUILDAH_DEFAULT_OPTS = [
    '--root',
    os.path.abspath(str(CFG['container']['root'])), '--runroot',
    os.path.abspath(str(CFG['container']['runroot']))
]

BUILDAH_DEFAULT_COMMAND_OPTS = ['--add-history']


def bb_buildah() -> BaseCommand:
    return buildah[BUILDAH_DEFAULT_OPTS]


BB_BUILDAH_FROM: BaseCommand = bb_buildah()['from']
BB_BUILDAH_BUD: BaseCommand = bb_buildah()['bud']
BB_BUILDAH_ADD: BaseCommand = bb_buildah()['add'][BUILDAH_DEFAULT_COMMAND_OPTS]
BB_BUILDAH_COMMIT: BaseCommand = bb_buildah()['commit']
BB_BUILDAH_CONFIG: BaseCommand = bb_buildah()['config']
BB_BUILDAH_COPY: BaseCommand = bb_buildah(
)['copy'][BUILDAH_DEFAULT_COMMAND_OPTS]
BB_BUILDAH_IMAGES: BaseCommand = bb_buildah()['images']
BB_BUILDAH_RUN: BaseCommand = bb_buildah()['run'][BUILDAH_DEFAULT_COMMAND_OPTS]
BB_BUILDAH_RM: BaseCommand = bb_buildah()['rm']
BB_BUILDAH_CLEAN: BaseCommand = bb_buildah()['clean']
BB_BUILDAH_INSPECT: BaseCommand = bb_buildah()['inspect']


def create_build_context() -> local.path:
    return local.path(mktemp('-dt', '-p', str(CFG['build_dir'])).strip())


def destroy_build_context(context: local.path) -> None:
    if context.exists():
        delete(context)


def create_working_container(from_image: model.FromLayer) -> str:
    return str(BB_BUILDAH_FROM(from_image.base)).strip()


def destroy_working_container(container: model.Container) -> None:
    BB_BUILDAH_RM(container.container_id)


def commit_working_container(container: model.Container) -> None:
    image = container.image
    BB_BUILDAH_COMMIT(container.container_id, image.name)


def spawn_add_layer(container: model.Container, layer: model.AddLayer) -> None:
    with local.cwd(container.context):
        sources = [
            os.path.join(container.context, source) for source in layer.sources
        ]
        cmd = BB_BUILDAH_ADD[container.container_id][sources][layer.destination]
        cmd()


def spawn_copy_layer(container: model.Container, layer: model.AddLayer) -> None:
    spawn_add_layer(container, layer)


def spawn_run_layer(container: model.Container, layer: model.RunLayer) -> None:
    kws = []
    for name, value in dict(layer.kwargs).items():
        kws.append(f'--{name}')
        kws.append(f'{str(value)}')

    cmd = BB_BUILDAH_RUN[kws][container.container_id, '--',
                              layer.command][layer.args]
    cmd()


def spawn_in_context(
    container: model.Container, layer: model.ContextLayer
) -> None:
    with local.cwd(container.context):
        layer.func()


def update_env_layer(
    container: model.Container, layer: model.UpdateEnv
) -> None:
    cmd = BB_BUILDAH_CONFIG
    for key, value in layer.env.items():
        cmd = cmd['-e', f'{key}={value}']
    cmd(container.container_id)


def set_entry_point(
    container: model.Container, layer: model.EntryPoint
) -> None:
    cmd = BB_BUILDAH_CONFIG['--entrypoint', json.dumps(list(layer.command))]
    cmd(container.container_id)


def set_command(container: model.Container, layer: model.SetCommand) -> None:
    cmd = BB_BUILDAH_CONFIG['--cmd', json.dumps(list(layer.command))]
    cmd(container.container_id)


def set_working_directory(
    container: model.Container, layer: model.WorkingDirectory
) -> None:
    BB_BUILDAH_CONFIG('--workingdir', layer.directory, container.container_id)


def find_image(tag: str) -> model.MaybeImage:
    results = BB_BUILDAH_IMAGES('--json', tag, retcode=[0, 125])
    if results:
        json_results = json.loads(results)
        if json_results:
            #json_image = json_results.pop(0)
            return model.Image(tag, model.FromLayer(tag), [])
    return None


LayerHandlerT = tp.Callable[[model.Container, model.Layer], None]

LAYER_HANDLERS = {
    model.AddLayer: spawn_add_layer,
    model.ContextLayer: spawn_in_context,
    model.CopyLayer: spawn_copy_layer,
    model.RunLayer: spawn_run_layer,
    model.UpdateEnv: update_env_layer,
    model.EntryPoint: set_entry_point,
    model.WorkingDirectory: set_working_directory,
    model.SetCommand: set_command
}


def spawn_layer(container: model.Container, layer: model.Layer) -> None:
    handler: LayerHandlerT = tp.cast(LayerHandlerT, LAYER_HANDLERS[type(layer)])
    handler(container, layer)
