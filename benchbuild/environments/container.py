"""
Support for building container environments.

This adds declarative options for building OCI compliant container images.
We let the tool 'buildah' do the heavy lifting of building the images.

You need to have buildah installed on your system before this module can
help you.
"""
import json
import logging
import textwrap
from typing import Any, Dict, Optional, Union

import attr
import rx
from plumbum import local
from rx.core.typing import Observable

from benchbuild.settings import CFG
from benchbuild.typing import (CallChain, CommandFunc, Project, ProjectT,
                               VariantContext)
from benchbuild.utils.cmd import buildah, mktemp

# Image declaration.
LOG = logging.getLogger(__name__)

__CONTAINER_ROOT__ = str(CFG['container']['root'])
__CONTAINER_RUNROOT__ = str(CFG['container']['runroot'])
__BUILDAH_DEFAULT_OPTS__ = [
    '--root', __CONTAINER_ROOT__, '--runroot', __CONTAINER_RUNROOT__
]


def __buildah__():
    return buildah[__BUILDAH_DEFAULT_OPTS__]


__BH_FROM__ = __buildah__()['from']
__BH_BUD__ = __buildah__()['bud']
__BH_ADD__ = __buildah__()['add']
__BH_COMMIT__ = __buildah__()['commit', '--rm']
__BH_COPY__ = __buildah__()['copy']
__BH_RUN__ = __buildah__()['run']
__BH_CLEAN__ = __buildah__()['clean']
__BH_INSPECT__ = __buildah__()['inspect']


@attr.s
class DeclarativeTool:
    chain: CallChain = attr.ib(default=attr.Factory(list))

    def __len__(self) -> int:
        return len(self.chain)


def from_tool(tool: DeclarativeTool) -> Observable:
    return rx.from_iterable(tool.chain)


@attr.s
class Buildah(DeclarativeTool):
    image: str = attr.ib(default='')
    context_dir: Optional[str] = attr.ib(default=None)
    current: str = attr.ib(init=False)

    def from_(self, base_img: str) -> 'Buildah':
        """
        Add a 'buildah from' command into the chain.

        Args:
            base_img: The base image to start building from.

        Returns:
            self
        """

        def from__():
            self.current = __BH_FROM__(base_img).strip()
            return f'buildah from {base_img}'

        self.chain.append(from__)
        return self

    def context(self, func: CommandFunc) -> 'Buildah':
        """
        Add a custom command function to the chain.

        This may be used to setup a build context on demand.

        Args:
            func: The CommandFunc to call during chain execution.

        Returns:
            self
        """

        def context_sandbox():
            tmpdir = self.context_dir
            if tmpdir is None or (not local.path(tmpdir).exists()):
                tmpdir = mktemp('-dt', '-p', str(CFG['build_dir'])).strip()
                self.context_dir = tmpdir

            with local.cwd(tmpdir):
                func()
            return f'context in {tmpdir}'

        self.chain.append(context_sandbox)
        return self

    def clear_context(self) -> 'Buildah':

        def clear():
            tmpdir = self.context_dir
            if tmpdir and local.path(tmpdir).exists():
                LOG.debug('wiping %s', tmpdir)
            return f'clear context in {self.context_dir}'

        self.chain.append(clear)
        return self

    def bud(self, dockerfile: str) -> 'Buildah':
        """
        Add a 'buildah bud' command into the chain.

        Args:
            dockerfile: The Dockerfile as input string.

        Returns:
            self
        """

        def bud_():
            (__BH_BUD__ << textwrap.dedent(dockerfile))()
            return f'buildah bud ...'

        self.chain.append(bud_)
        return self

    def add(self, src: str, dest: str) -> 'Buildah':
        """
        Add a 'buildah add' command into the chain.

        Args:
            src: Source path to copy into the image.
            dest: Destination path inside the image.
        Returns:
            self
        """

        def add_():
            tmpdir = self.context_dir
            if tmpdir is None or (not local.path(tmpdir).exists()):
                LOG.error(
                    'No build context, cannot add. Try using context(...)')
                return self.current

            with local.cwd(tmpdir):
                __BH_ADD__(self.current, src, dest)
            return f'buildah add {self.current} {src} {dest}'

        self.chain.append(add_)
        return self

    def commit(self, tag: str) -> 'Buildah':
        """
        Add a 'buildah commit' command into the chain.

        Args:
            tag: The tag for the committed image.
        Returns:
            self
        """

        def commit_():
            __BH_COMMIT__(self.current, tag)
            return f'buildah commit {self.current} {tag}'

        self.chain.append(commit_)
        return self

    def copy(self, src: str, dest: str) -> 'Buildah':
        """
        Add a 'buildah copy' command into the chain.

        Args:
            src: Source path to copy into the image.
            dest: Destination path inside the image.
        Returns:
            self
        """

        def copy_():
            __BH_COPY__(self.current, src, dest)
            return self.current

        self.chain.append(copy_)
        return self

    def run(self, *args, **kwargs) -> 'Buildah':
        """
        Add a 'buildah run' command into the chain.

        Args:
            *args: the arguments that will be passed as command to run.
            **kwargs: the flags that will be passed to 'buildah run'.

        Returns:
            self
        """

        def run_():
            kws = []
            for name, value in dict(kwargs).items():
                kws.append(f'--{name}')
                kws.append(f'{str(value)}')

            __BH_RUN__(*kws, self.current, '--', *args)
            return f"buildah run {self.current} -- {' '.join(args)}"

        self.chain.append(run_)
        return self


#@attr.s
#class Podman(DeclarativeTool):
#    pass


def by_tag(tag: str) -> Optional[Any]:
    """
    Find a container image by tag.

    Args:
        tag: The image tag to search for

    Returns:

    """
    results = __buildah__()('images', '--json', tag, retcode=[0, 1])
    if results:
        results = json.loads(results)
        for res in results:
            yield res


def mktag(name: str, group: str, variant: VariantContext) -> str:
    """Generate a container tag."""
    version_str = "-".join([str(var) for var in variant.values()])
    return f"{name}/{group}:{version_str}"


def by_project(project: Union[Project, ProjectT],
               variant: Optional[VariantContext] = None) -> Any:
    """
    Find a container image by project.

    Args:
        project: The project to search an image for.

    Returns:

    """

    name = project.NAME
    group = project.GROUP
    variant = variant if variant else project.variant

    image_tag = mktag(name, group, variant)
    for res in by_tag(image_tag):
        yield res


def is_cached(project: Union[Project, ProjectT],
              variant: Optional[VariantContext] = None) -> bool:
    for _ in by_project(project, variant):
        return True
    return False


def by_id(imageid: str) -> Optional[Dict[str, Any]]:
    """
    Find information about an image via its' ID.

    Args:
        imageid: The image id to search for.

    Returns:
        A dictionary of parsed JSON entries, generated by buildah inspect.
    """
    results = __buildah__()('inspect',
                            '--type',
                            'image',
                            imageid,
                            retcode=[0, 1])
    if results:
        results = json.loads(results)
    return results


def add_benchbuild(image: Buildah) -> None:
    src_dir = str(CFG['container']['source'])
    tgt_dir = '/benchbuild'
    crun = '/usr/bin/crun'

    def from_source(image):
        image.run('mkdir', f'{tgt_dir}', runtime=crun)
        # The image requires git, pip and a working python3.7 or better.
        image.run('pip3', 'install', '-U', 'setuptools', runtime=crun)
        image.run('pip3',
                  'install',
                  f'{tgt_dir}',
                  mount=f'type=bind,src={src_dir},target={tgt_dir}',
                  runtime=crun)

    def from_pip(image):
        image.run('pip', 'install', 'benchbuild', runtime=crun)

    if bool(CFG['container']['from_source']):
        from_source(image)
    else:
        from_pip(image)


def add_project_sources(var: VariantContext, image: Buildah) -> None:

    def setup_context() -> 'None':
        for version in var.values():
            src = version.owner
            src.version(local.cwd, str(version))

    image.context(setup_context)
    image.add('.', "/app/")


def commit(prj: ProjectT, var: VariantContext) -> None:
    tag = mktag(prj.NAME, prj.GROUP, var)
    image = prj.CONTAINER
    image.commit(tag)
    image.clear_context()


def materialize(prj: ProjectT, var: VariantContext) -> rx.Observable:
    return rx.combine_latest(rx.return_value(prj), rx.return_value(var),
                             from_tool(prj.CONTAINER))
