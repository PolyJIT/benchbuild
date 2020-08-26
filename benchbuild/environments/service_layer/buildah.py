import json

from plumbum import TEE, local
from plumbum.path.utils import delete

from benchbuild.environments.domain import model
from benchbuild.settings import CFG
from benchbuild.utils.cmd import buildah, mktemp

BUILDAH_DEFAULT_OPTS = [
    '--root',
    str(CFG['container']['root']), '--runroot',
    str(CFG['container']['runroot'])
]

BUILDAH_DEFAULT_COMMAND_OPTS = ['--add-history']


def bb_buildah():
    return buildah[BUILDAH_DEFAULT_OPTS]


BB_BUILDAH_FROM = bb_buildah()['from']
BB_BUILDAH_BUD = bb_buildah()['bud']
BB_BUILDAH_ADD = bb_buildah()['add'][BUILDAH_DEFAULT_COMMAND_OPTS]
BB_BUILDAH_COMMIT = bb_buildah()['commit']
BB_BUILDAH_CONFIG = bb_buildah()['config']
BB_BUILDAH_COPY = bb_buildah()['copy'][BUILDAH_DEFAULT_COMMAND_OPTS]
BB_BUILDAH_IMAGES = bb_buildah()['images']
BB_BUILDAH_RUN = bb_buildah()['run'][BUILDAH_DEFAULT_COMMAND_OPTS]
BB_BUILDAH_RM = bb_buildah()['rm']
BB_BUILDAH_CLEAN = bb_buildah()['clean']
BB_BUILDAH_INSPECT = bb_buildah()['inspect']


def create_build_context() -> local.path:
    return local.path(mktemp('-dt', '-p', str(CFG['build_dir'])).strip())


def destroy_build_context(context: local.path) -> None:
    if context.exists():
        delete(context)


def create_working_container(from_image: model.FromLayer) -> str:
    return BB_BUILDAH_FROM(from_image.base).strip()


def destroy_working_container(container: model.Container) -> None:
    BB_BUILDAH_RM[container.container_id] & TEE


def commit_working_container(container: model.Container) -> None:
    image = container.image
    BB_BUILDAH_COMMIT[container.container_id, image.name] & TEE


def spawn_add_layer(container: model.Container, layer: model.AddLayer) -> None:
    with local.cwd(container.context):
        cmd = BB_BUILDAH_ADD[container.container_id][layer.sources][
            layer.destination]
        cmd & TEE


def spawn_copy_layer(container: model.Container, layer: model.AddLayer) -> None:
    spawn_add_layer(container, layer)


def spawn_run_layer(container: model.Container, layer: model.RunLayer) -> None:
    kws = []
    for name, value in dict(layer.kwargs).items():
        kws.append(f'--{name}')
        kws.append(f'{str(value)}')

    cmd = BB_BUILDAH_RUN[kws][container.container_id, '--',
                              layer.command][layer.args]
    cmd & TEE


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
    cmd[container.container_id] & TEE


def set_entry_point(
    container: model.Container, layer: model.EntryPoint
) -> None:
    cmd = BB_BUILDAH_CONFIG['--entrypoint', json.dumps(list(layer.command))]
    cmd(container.container_id)


def set_command(container: model.Container, layer: model.SetCommand) -> None:
    cmd = BB_BUILDAH_CONFIG['--command', json.dumps(list(layer.command))]
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
    handler = LAYER_HANDLERS[type(layer)]
    handler(container, layer)
