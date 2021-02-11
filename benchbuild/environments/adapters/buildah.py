import abc
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


class ImageRegistry(abc.ABC):
    images: tp.Dict[str, model.Image]
    containers: tp.Set[model.Container]

    def find(self, tag: str) -> model.MaybeImage:
        if tag in self.images:
            return self.images[tag]

        image = self._find(tag)
        if image:
            self.images[tag] = image
            return image

        return None

    @abc.abstractmethod
    def _find(self, tag: str) -> model.MaybeImage:
        return NotImplementedError

    def create(self, tag: str, layers: tp.List[model.Layer]) -> model.Container:
        from_ = [l for l in layers if isinstance(l, model.FromLayer)].pop(0)
        image = model.Image(tag, from_, [])
        container = self._create(tag, image)

        self.containers.add(container)

        return container

    @abc.abstractmethod
    def _create(
        self, tag: str, layers: tp.List[model.Layer]
    ) -> model.Container:
        return NotImplementedError


class BuildahImageRegistry:

    def __init__(self):
        self.images = {}
        self.containers: {}

    def _create(self, image: model.Image) -> model.Container:
        container_id = str(bb_buildah('from')(image.from_.base)).strip()
        context = local.path(mktemp('-dt', '-p', str(CFG['build_dir'])).strip())

        return model.Container(container_id, image, context)

    def destroy(self, container: model.Container) -> None:
        bb_buildah('rm')(container.container_id)
        context_path = local.path(container.context)
        if context_path.exists():
            delete(context_path)

    def _find(self, tag: str) -> model.MaybeImage:
        results = bb_buildah('images')('--json', tag.lower(), retcode=[0, 125])
        if results:
            json_results = json.loads(results)
            if json_results:
                #json_image = json_results.pop(0)
                image = model.Image(tag, model.FromLayer(tag), [])
                fetch_image_env(image)
                return image
        return None

    def commit(self, container: model.Container) -> None:
        image = container.image
        bb_buildah('commit')(container.container_id, image.name.lower())
