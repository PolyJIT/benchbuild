"""
BenchBuild supports containerized execution of all experiments. This gives you
full control about the environment your [projects](/concepts/projects/) and
[experiments](/concepts/experiments/) may run in.

The following example uses the latest ``alpine:latest``:

.. code-block:: python

    ContainerImage().from_('alpine:latest')
        .run('apk', 'update')
        .run('apk', 'add', 'python3')

"""

import logging
import typing as tp

from benchbuild.environments.adapters.common import buildah_version
from benchbuild.settings import CFG

from . import model

LOG = logging.getLogger(__name__)


class ContainerImage(list):
    """
    Define a container image declaratively.

    Start a new image using the ``.from_`` method and provide a base image.
    Each method creates a new layer in the container image.
    """

    def __str__(self) -> str:
        return "\n".join([str(elt) for elt in self])

    @property
    def base(self) -> str:
        layers = [l for l in self if isinstance(l, model.FromLayer)]
        if layers:
            return layers.pop(0).base
        return ''

    def env(self, **kwargs: str) -> 'ContainerImage':
        """
        Create an environment layer in this image.

        Dockerfile syntax: ENV

        Args:
            kwargs (str): a dictionary containing name/value pairings to be
                set as environment variables.
        """
        self.append(model.UpdateEnv(kwargs))
        return self

    def from_(self, base_image: str) -> 'ContainerImage':
        """
        Specify a new base layer for this image.

        Dockerfile syntax: FROM <image>

        Args:
            base_image (str): The base image for our new container image.
        """
        self.append(model.FromLayer(base_image))
        return self

    def context(self, func: tp.Callable[[], None]) -> 'ContainerImage':
        """
        Interact with the build context of the container.

        Sometimes you have to interact with the build context of a container
        image. For example, you need to add artifacts to the build context
        before you can add the to the container image.
        BenchBuild uses this to add the sources to the container image
        automatically.

        Args:
            func (tp.Callable[[], None]): A callable that is executed in the
                build-context directory.
        """
        self.append(model.ContextLayer(func))
        return self

    def add(self, sources: tp.Iterable[str], tgt: str) -> 'ContainerImage':
        """
        Add given files from the source to the container image.

        Dockerfile syntax: ADD <source> [<source>...] <target>

        Args:
            sources (tp.Iterable[str]): Source path to add to the target
            tgt (str): Absolute target path.
        """
        self.append(model.AddLayer(tuple(sources), tgt))
        return self

    def copy_(self, sources: tp.Iterable[str], tgt: str) -> 'ContainerImage':
        """
        Copy given files from the source to the container image.

        Dockerfile syntax: COPY <source> [<source>...] <target>

        Args:
            sources (tp.Iterable[str]): Source path to add to the target
            tgt (str): Absolute target path.
        """
        self.append(model.CopyLayer(tuple(sources), tgt))
        return self

    def run(self, command: str, *args: str, **kwargs: str) -> 'ContainerImage':
        """
        Run a command in the container image.

        Dockerfile syntax: RUN <command>

        Args:
            command (str): The binary to execute in the container.
            *args (str): Arguments that will be passed to the container.
            **kwargs (str): Additional options that will be passed to the
                backend run command.
        """
        self.append(model.RunLayer(command, args, kwargs))
        return self

    def workingdir(self, directory: str) -> 'ContainerImage':
        """
        Change the working directory in the container.

        Dockerfile syntax: WORKINGDIR <absolute-path>

        All layers that follow this layer will be run with their working
        directory set to ``directory``.

        Args:
            directory (str): The target directory to set our cwd to.
        """
        self.append(model.WorkingDirectory(directory))
        return self

    def entrypoint(self, *args: str) -> 'ContainerImage':
        """
        Set the entrypoint of the container.

        Dockerfile syntax: ENTRYPOINT <command>

        This sets the default binary to run to the given command.

        Args:
            *args (str): A list of command components.
        """
        self.append(model.EntryPoint(args))
        return self

    def command(self, *args: str) -> 'ContainerImage':
        """
        Set the default command the container runs.

        Dockerfile syntax: CMD <command>

        Args:
            *args (str): A list of command components.
        """
        self.append(model.SetCommand(args))
        return self


DEFAULT_BASES: tp.Dict[str, ContainerImage] = {
    'benchbuild:alpine': ContainerImage() \
            .from_("docker.io/alpine:3.17") \
            .run('apk', 'update') \
            .run('apk', 'add', 'python3', 'python3-dev', 'postgresql-dev',
                 'linux-headers', 'musl-dev', 'git', 'gcc', 'g++',
                 'sqlite-libs', 'libgit2-dev', 'libffi-dev', 'py3-pip')
}


def add_benchbuild_layers(layers: ContainerImage) -> ContainerImage:
    """
    Add benchbuild into the given container image.

    This assumes all necessary depenencies are available in the image already.
    The installation is done, either using pip from a remote mirror, or using
    the source checkout of benchbuild.

    A source installation requires your buildah/podman installation to be
    able to complete a bind-mount as the user that runs benchbuild.

    Args:
        layers: a container image we will add our install layers to.

    Returns:
        the modified container image.
    """
    crun = str(CFG['container']['runtime'])
    src_dir = str(CFG['container']['source'])
    tgt_dir = '/benchbuild'

    def from_source(image: ContainerImage) -> None:
        LOG.debug('BenchBuild will be installed from  source.')

        mount = f'type=bind,src={src_dir},target={tgt_dir}'
        if buildah_version() >= (1, 24, 0):
            mount += ',rw'

        # The image requires git, pip and a working python3.7 or better.
        image.run('mkdir', f'{tgt_dir}', runtime=crun)
        image.run('pip3', 'install', 'setuptools', runtime=crun)
        image.run(
            'pip3',
            'install',
            '--ignore-installed',
            tgt_dir,
            mount=mount,
            runtime=crun
        )

    def from_pip(image: ContainerImage) -> None:
        LOG.debug('installing benchbuild from pip release.')
        image.run('pip3', 'install', 'benchbuild', runtime=crun)

    if bool(CFG['container']['from_source']):
        from_source(layers)
    else:
        from_pip(layers)
    return layers
