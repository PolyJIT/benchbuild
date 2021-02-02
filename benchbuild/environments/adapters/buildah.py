import json
import os
import typing as tp

from plumbum import local
from plumbum.commands.base import BaseCommand
from plumbum.path.utils import delete

from benchbuild.environments.domain import model
from benchbuild.settings import CFG
from benchbuild.utils.cmd import buildah, mktemp


def bb_buildah(*args: str) -> BaseCommand:
    opts = [
        '--root',
        os.path.abspath(str(CFG['container']['root'])), '--runroot',
        os.path.abspath(str(CFG['container']['runroot']))
    ]
    cmd = buildah[opts]
    return cmd[args]


def create_build_context() -> local.path:
    return local.path(mktemp('-dt', '-p', str(CFG['build_dir'])).strip())


def destroy_build_context(context: local.path) -> None:
    if context.exists():
        delete(context)


def create_working_container(from_image: model.FromLayer) -> str:
    return str(bb_buildah('from')(from_image.base)).strip()


def destroy_working_container(container: model.Container) -> None:
    bb_buildah('rm')(container.container_id)


def commit_working_container(container: model.Container) -> None:
    image = container.image
    bb_buildah('commit')(container.container_id, image.name.lower())


def spawn_add_layer(container: model.Container, layer: model.AddLayer) -> None:
    with local.cwd(container.context):
        sources = [
            os.path.join(container.context, source) for source in layer.sources
        ]
        buildah_add = bb_buildah('add', '--add-history')
        buildah_add = buildah_add[container.container_id][sources][
            layer.destination]
        buildah_add()


def spawn_copy_layer(container: model.Container, layer: model.AddLayer) -> None:
    spawn_add_layer(container, layer)


def spawn_run_layer(container: model.Container, layer: model.RunLayer) -> None:
    kws = []
    for name, value in dict(layer.kwargs).items():
        kws.append(f'--{name}')
        kws.append(f'{str(value)}')

    buildah_run = bb_buildah('run', '--add-history')
    buildah_run = buildah_run[kws][container.container_id, '--',
                                   layer.command][layer.args]
    buildah_run()


def spawn_in_context(
    container: model.Container, layer: model.ContextLayer
) -> None:
    with local.cwd(container.context):
        layer.func()


def update_env_layer(
    container: model.Container, layer: model.UpdateEnv
) -> None:
    buildah_config = bb_buildah('config')
    for key, value in layer.env.items():
        buildah_config = buildah_config['-e', f'{key}={value}']
    buildah_config(container.container_id)


def fetch_image_env(image: model.Image) -> None:
    """
    Fetch the configured environment vars for this image.

    Reconstructs an environment dictionary from the configured container
    image enviornment. The image will be updated in-place. Existing values
    will be overwritten.

    Args:
        image: The image to fetch the env for.
    """
    buildah_inspect = bb_buildah('inspect')
    results = json.loads(buildah_inspect(image.name))
    oci_config = {}

    try:
        if results:
            oci_config = results['OCIv1']['config']

        if oci_config:
            env_list = oci_config.get('Env')
            if env_list:
                for env_item in env_list:
                    k, v = env_item.split('=')
                    image.env[k] = v

    except KeyError:
        return


def set_entry_point(
    container: model.Container, layer: model.EntryPoint
) -> None:
    cmd = bb_buildah('config')['--entrypoint', json.dumps(list(layer.command))]
    cmd(container.container_id)


def set_command(container: model.Container, layer: model.SetCommand) -> None:
    cmd = bb_buildah('config')['--cmd', json.dumps(list(layer.command))]
    cmd(container.container_id)


def set_working_directory(
    container: model.Container, layer: model.WorkingDirectory
) -> None:
    bb_buildah('config'
              )('--workingdir', layer.directory, container.container_id)


def find_image(tag: str) -> model.MaybeImage:
    results = bb_buildah('images')('--json', tag.lower(), retcode=[0, 125])
    if results:
        json_results = json.loads(results)
        if json_results:
            #json_image = json_results.pop(0)
            image = model.Image(tag, model.FromLayer(tag), [])
            fetch_image_env(image)
            return image
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
