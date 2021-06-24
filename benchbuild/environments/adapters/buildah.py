import abc
import json
import logging
import os
import typing as tp

from plumbum import local

from benchbuild.environments.adapters.common import (
    run,
    bb_buildah,
    MaybeCommandError,
    CommandError,
    ImageCreateError,
)
from benchbuild.environments.domain import model, events
from benchbuild.settings import CFG
from benchbuild.utils.cmd import mktemp

LOG = logging.getLogger(__name__)


def commit_working_container(container: model.Container) -> MaybeCommandError:
    image = container.image
    commit = bb_buildah('commit')[container.container_id, image.name.lower()]
    _, err = run(commit)
    return err


def _spawn_add_layer(
    container: model.Container, layer: model.AddLayer
) -> MaybeCommandError:
    with local.cwd(container.context):
        sources = [
            os.path.join(container.context, source) for source in layer.sources
        ]
        buildah_add = bb_buildah('add', '--add-history')
        buildah_add = buildah_add[container.container_id][sources][
            layer.destination]
        _, err = run(buildah_add)
        return err


def _spawn_copy_layer(
    container: model.Container, layer: model.AddLayer
) -> MaybeCommandError:
    return _spawn_add_layer(container, layer)


def _spawn_run_layer(
    container: model.Container, layer: model.RunLayer
) -> MaybeCommandError:
    kws = []
    for name, value in layer.kwargs:
        kws.append(f'--{name}')
        kws.append(f'{str(value)}')

    buildah_run = bb_buildah('run', '--add-history')
    buildah_run = buildah_run[kws][container.container_id, '--',
                                   layer.command][layer.args]
    _, err = run(buildah_run)
    return err


def _spawn_in_context( # pylint: disable=useless-return
    container: model.Container, layer: model.ContextLayer
) -> MaybeCommandError:
    with local.cwd(container.context):
        layer.func()
    return None


def _update_env_layer(
    container: model.Container, layer: model.UpdateEnv
) -> MaybeCommandError:
    buildah_config = bb_buildah('config')
    for key, value in layer.env:
        buildah_config = buildah_config['-e', f'{key}={value}']
    _, err = run(buildah_config[container.container_id])
    return err


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


def _set_entry_point(
    container: model.Container, layer: model.EntryPoint
) -> MaybeCommandError:
    cmd = bb_buildah('config')['--entrypoint', json.dumps(list(layer.command))]
    _, err = run(cmd[container.container_id])
    return err


def _set_command(
    container: model.Container, layer: model.SetCommand
) -> MaybeCommandError:
    cmd = bb_buildah('config')['--cmd', json.dumps(list(layer.command))]
    _, err = run(cmd[container.container_id])
    return err


def _set_working_directory(
    container: model.Container, layer: model.WorkingDirectory
) -> MaybeCommandError:
    _, err = run(
        bb_buildah('config')['--workingdir', layer.directory,
                             container.container_id]
    )
    return err


LayerHandlerT = tp.Callable[[model.Container, model.Layer], MaybeCommandError]

_LAYER_HANDLERS = {
    model.AddLayer: _spawn_add_layer,
    model.ContextLayer: _spawn_in_context,
    model.CopyLayer: _spawn_copy_layer,
    model.RunLayer: _spawn_run_layer,
    model.UpdateEnv: _update_env_layer,
    model.EntryPoint: _set_entry_point,
    model.WorkingDirectory: _set_working_directory,
    model.SetCommand: _set_command
}


def spawn_layer(
    container: model.Container, layer: model.Layer
) -> MaybeCommandError:
    if layer == container.image.from_:
        return None

    handler: LayerHandlerT = tp.cast(
        LayerHandlerT, _LAYER_HANDLERS[type(layer)]
    )
    return handler(container, layer)


def handle_layer_error(
    err: CommandError, container: model.Container, layer: model.Layer
) -> None:
    """
    Process a layer error gracefully.

    Annotate the image with an event that signals a failed layer.
    Persist the current build container for later debugging, if necessary.

    Args:
        err: the command error that contains details about the error.
        container: the container we are working on.
        layer: the layer we tried to build.
    """
    image = container.image
    image.events.append(
        events.LayerCreationFailed(str(layer), image.name, str(err))
    )

    def can_keep(layer: model.Layer) -> bool:
        keep = bool(CFG['container']['keep'])
        return keep and not isinstance(layer, model.FromLayer)

    if can_keep(layer):
        failed_tag, keep_err = store_failed_build(
            image.name, container.container_id
        )
        if keep_err:
            raise keep_err

        image.events.append(
            events.DebugImageKept(image.name, failed_tag, str(layer))
        )


def store_failed_build(tag: str,
                       container_id: str) -> tp.Tuple[str, MaybeCommandError]:
    """
    Store a failed build container.

    Args:
        tag: the original image tag name.
        container_id: the failed build container.

    Returns:
        A tuple of the new image tag and the command error state
    """
    suffix = str(CFG['container']['keep_suffix'])
    failed_tag = f'{tag}-{suffix}'

    commit = bb_buildah('commit')[container_id, failed_tag.lower()]
    _, err = run(commit)
    return failed_tag, err


def find_entrypoint(tag: str) -> str:
    """
    Find and return the entrypoint of a container image.

    This assumes an image tag configured by benchbuild as input.

    Args:
        tag: the image tage.

    Returns:
        A tuple of the configured entrypoint joined with whitespace and the
        command's error state.
    """
    inspect_str = bb_buildah('inspect')(tag)
    json_output = json.loads(inspect_str)

    config = json_output['OCIv1']['config']
    if not config:
        raise ValueError("Could not find the container image config")

    return ' '.join(config['Entrypoint'])


class ImageRegistry(abc.ABC):
    images: tp.Dict[str, model.Image]
    containers: tp.Dict[str, model.Container]

    def __init__(self) -> None:
        self.images = dict()
        self.containers = dict()

    def create(self, tag: str, from_: model.FromLayer) -> model.MaybeContainer:
        """
        Create prepares an empty image hull for further customization.

        Args:
            tag: The new image's name tag.
            from_: A base layer to start our build container from.

        Returns:
            A build container to further customize our image.

        Raises:
            ImageCreateError: If there was an error during initial construction
                of a working container.
        """
        container = self._create(tag, from_)
        if container:
            image = container.image

            self.images[image.name] = image
            self.containers[image.name] = container

        return container

    @abc.abstractmethod
    def _create(self, tag: str, from_: model.FromLayer) -> model.MaybeContainer:
        """
        Implementation hook for subclasses.

        See `ImageRegistry.create` .

        Args:
            tag: The image tag to look for.
            from_: A base layer to start our build container from.
        """
        raise NotImplementedError

    def find(self, tag: str) -> model.MaybeImage:
        """
        Find tries to retreive an image from its storage.

        Args:
            tag: The image tag to look for.

        Returns:
            `model.Image`, if we can find an image, else None.
        """
        if tag in self.images:
            return self.images[tag]

        image = self._find(tag)
        if image:
            self.images[tag] = image
            return image

        return None

    @abc.abstractmethod
    def _find(self, tag: str) -> model.MaybeImage:
        """
        Implementation hook for subclasses.

        See `ImageRegistry.find` .

        Args:
            tag: The image tag to look for.
        """
        raise NotImplementedError

    def add(self, image: model.Image) -> bool:
        """
        Add registers an image for storage in the repository.

        Any layers not present in the registry will have to be spawned.

        Args:
            image: An image to be stored in the registry.

        Returns:
            True, if the image was added successfully.
        """
        success = self._add(image)
        if image.name not in self.images:
            self.images[image.name] = image

        return success

    @abc.abstractmethod
    def _add(self, image: model.Image) -> bool:
        """
        Implementation hook for subclasses.

        See `ImageRegistry.add`.

        Args:
            image: An image to be stored in the registry.
        """
        raise NotImplementedError

    def remove(self, image: model.Image) -> None:
        """
        Remove an image from this registry.

        This will delete the image from the storage.

        Args:
           image: An image to be removed from the repository.
        """
        if image.name in self.images:
            self._remove(image)

        del self.images[image.name]

        # What to do with open build containers? Delete as well?

    @abc.abstractmethod
    def _remove(self, image: model.Image) -> None:
        """
        Implementation hook for subclasses.

        See `ImageRegistry.remove`.

        Args:
            image: An image to be removed from the repository.
        """
        raise NotImplementedError

    def env(self, tag: str, name: str) -> tp.Optional[str]:
        return self._env(tag, name)

    @abc.abstractmethod
    def _env(self, tag: str, name: str) -> tp.Optional[str]:
        raise NotImplementedError

    def temporary_mount(self, tag: str, source: str, target: str) -> None:
        image = self.find(tag)
        if image:
            image.mounts.append(model.Mount(source, target))


class BuildahImageRegistry(ImageRegistry):

    def _create(self, tag: str, from_: model.FromLayer) -> model.MaybeContainer:
        image = model.Image(tag, from_, [])

        container_id, err = run(bb_buildah('from')[from_.base])

        if err:
            raise ImageCreateError(tag, message=str(err))

        context = local.path(mktemp('-dt', '-p', str(CFG['build_dir'])).strip())
        container = model.Container(container_id, image, context, image.name)

        return container

    def _add(self, image: model.Image) -> bool:
        required_layers = [l for l in image.layers if not image.is_present(l)]
        required_layers.reverse()
        if image.name not in self.containers and required_layers:
            # Recreate build container from image tag
            raise ValueError("No build container found. Create one first.")

        err: MaybeCommandError = None
        while required_layers and err is None:
            layer = required_layers.pop()
            LOG.info(layer)
            container = self.containers[image.name]
            err = spawn_layer(container, layer)
            if err:
                handle_layer_error(err, container, layer)
            else:
                image.events.append(
                    events.LayerCreated(
                        str(layer), container.container_id, image.name
                    )
                )
                image.present(layer)

        return err is None

    def _find(self, tag: str) -> model.MaybeImage:
        results, _ = run(
            bb_buildah('images')['--json', tag.lower()], retcode=[0, 125]
        )
        if results:
            json_results = json.loads(results)
            if json_results:
                #json_image = json_results.pop(0)
                image = model.Image(tag, model.FromLayer(tag), [])
                fetch_image_env(image)
                return image
        return None

    def _env(self, tag: str, name: str) -> tp.Optional[str]:
        image = self.find(tag)
        if image:
            return image.env.get(name)
        return None

    def _remove(self, image: model.Image) -> None:
        pass
