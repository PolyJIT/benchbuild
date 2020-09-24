import logging
import typing as tp

from benchbuild.settings import CFG

from . import model

LOG = logging.getLogger(__name__)


class ContainerImage(list):

    @property
    def base(self) -> str:
        layers = [l for l in self if isinstance(l, model.FromLayer)]
        if layers:
            return layers.pop(0).base
        return ''

    @property
    def layers(self) -> tp.List[model.Layer]:
        pass

    def env(self, **kwargs: str) -> 'ContainerImage':
        self.append(model.UpdateEnv(kwargs))
        return self

    def from_(self, base_image: str) -> 'ContainerImage':
        self.append(model.FromLayer(base_image))
        return self

    def context(self, func: tp.Callable[[], None]) -> 'ContainerImage':
        self.append(model.ContextLayer(func))
        return self

    def add(self, sources: tp.Iterable[str], tgt: str) -> 'ContainerImage':
        self.append(model.AddLayer(sources, tgt))
        return self

    def copy_(self, sources: tp.Iterable[str], tgt: str) -> 'ContainerImage':
        self.append(model.CopyLayer(sources, tgt))
        return self

    def run(self, command: str, *args: str, **kwargs: str) -> 'ContainerImage':
        self.append(model.RunLayer(command, args, kwargs))
        return self

    def workingdir(self, directory: str) -> 'ContainerImage':
        self.append(model.WorkingDirectory(directory))
        return self

    def entrypoint(self, *args: str) -> 'ContainerImage':
        self.append(model.EntryPoint(args))
        return self

    def command(self, *args: str) -> 'ContainerImage':
        self.append(model.SetCommand(args))
        return self


DEFAULT_BASES: tp.Dict[str, ContainerImage] = {
    'benchbuild:alpine': ContainerImage() \
            .from_("alpine:latest") \
            .run('apk', 'update') \
            .run('apk', 'add', 'python3', 'python3-dev', 'postgresql-dev',
                 'linux-headers', 'musl-dev', 'git', 'gcc', 'sqlite-libs',
                 'libgit2-dev', 'libffi-dev', 'py3-pip')
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
        LOG.debug('installing benchbuild from source.')
        LOG.debug('src_dir: %s tgt_dir: %s', src_dir, tgt_dir)

        # The image requires git, pip and a working python3.7 or better.
        image.run('mkdir', f'{tgt_dir}', runtime=crun)
        image.run('pip3', 'install', 'setuptools', runtime=crun)
        image.run(
            'pip3',
            'install',
            '--ignore-installed',
            tgt_dir,
            mount=f'type=bind,src={src_dir},target={tgt_dir}',
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
