import typing as tp

import attr

from benchbuild.settings import CFG

from . import model


@attr.s
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

    def from_(self, base_image: str) -> 'Environment':
        self.append(model.FromLayer(base_image))
        return self

    def context(self, func: tp.Callable[[], None]) -> 'ContainerImage':
        self.append(model.ContextLayer(func))
        return self

    def clear_context(self, func: tp.Callable[[], None]) -> 'ContainerImage':
        self.append(model.ClearContextLayer(func))
        return self

    def add(self, sources: tp.Iterable[str], tgt: str) -> 'ContainerImage':
        self.append(model.AddLayer(sources, tgt))
        return self

    def copy(self, sources: tp.Iterable[str], tgt: str) -> 'ContainerImage':
        self.append(model.CopyLayer(sources, tgt))
        return self

    def run(self, command: str, *args: str, **kwargs: str) -> 'ContainerImage':
        self.append(model.RunLayer(command, args, kwargs))
        return self


DEFAULT_BASES = {
    'benchbuild:alpine': ContainerImage() \
            .from_("alpine:latest") \
            .run('apk', 'update') \
            .run('apk', 'add', 'python3', 'python3-dev', 'linux-headers',
                 'musl-dev', 'git', 'gcc', 'sqlite-libs', 'py3-pip')
}


def add_benchbuild_layers(layers: ContainerImage) -> ContainerImage:
    crun = str(CFG['container']['runtime'])
    src_dir = str(CFG['container']['source'])
    tgt_dir = '/benchbuild'

    def from_source(image: ContainerImage):
        # The image requires git, pip and a working python3.7 or better.
        image.run('mkdir', f'{tgt_dir}', runtime=crun)
        image.run('pip3', 'install', 'setuptools', runtime=crun)
        image.run('pip3',
                  'install',
                  tgt_dir,
                  mount=f'type=bind,src={src_dir},target={tgt_dir}',
                  runtime=crun)

    def from_pip(image: ContainerImage):
        image.run('pip', 'install', 'benchbuild', runtime=crun)

    if bool(CFG['container']['from_source']):
        from_source(layers)
    else:
        from_pip(layers)
    return layers
