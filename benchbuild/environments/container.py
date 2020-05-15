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
from benchbuild.typing import CallChain, CommandFunc, Project, ProjectT
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

        def from__(tool: 'Buildah'):
            tool.current = __BH_FROM__(base_img).strip()
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

        def context_sandbox(tool: 'Buildah'):
            tmpdir = tool.context_dir
            if tmpdir is None or (not local.path(tmpdir).exists()):
                tmpdir = mktemp('-dt', '-p', str(CFG['build_dir'])).strip()
                tool.context_dir = tmpdir

            with local.cwd(tmpdir):
                func()
            return f'context in {tmpdir}'

        self.chain.append(context_sandbox)
        return self

    def clear_context(self) -> 'Buildah':

        def clear(tool: 'Buildah'):
            tmpdir = tool.context_dir
            if tmpdir and local.path(tmpdir).exists():
                LOG.debug('wiping %s', tmpdir)
            return f'clear context in {tool.context_dir}'

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

        def bud_(_: 'Buildah'):
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

        def add_(tool: 'Buildah'):
            tmpdir = tool.context_dir
            if tmpdir is None or (not local.path(tmpdir).exists()):
                LOG.error(
                    'No build context, cannot add. Try using context(...)')
                raise ValueError()

            with local.cwd(tmpdir):
                __BH_ADD__(tool.current, src, dest)
            return f'buildah add {tool.current} {src} {dest}'

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

        def commit_(tool: 'Buildah'):
            __BH_COMMIT__(tool.current, tag)
            return f'buildah commit {tool.current} {tag}'

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

        def copy_(tool: 'Buildah'):
            __BH_COPY__(tool.current, src, dest)
            return f'buildah copy {tool.current} {src} {dest}'

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

        def run_(tool: 'Buildah'):
            kws = []
            for name, value in dict(kwargs).items():
                kws.append(f'--{name}')
                kws.append(f'{str(value)}')

            __BH_RUN__(*kws, tool.current, '--', *args)
            return f"buildah run {tool.current} -- {' '.join(args)}"

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


def mktag(prj: Project) -> str:
    """Generate a container tag."""
    version_str = "-".join([str(var) for var in prj.variant.values()])
    return f"{prj.name}/{prj.group}:{version_str}"


def by_project(project: Union[Project, ProjectT]) -> Any:
    """
    Find a container image by project.

    Args:
        project: The project to search an image for.

    Returns:

    """
    for res in by_tag(mktag(project)):
        yield res


def identity() -> rx.Observable:
    return rx.pipe(rx.operators.map(lambda o: o))


def is_cached(disabled: bool = False) -> rx.Observable:

    def is_cached_(project: Project) -> bool:
        for _ in by_project(project):
            return True
        return False

    if not disabled:
        return rx.pipe(rx.operators.filter(lambda prj: not is_cached_(prj)))
    return identity()


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


def add_benchbuild(prj: Project) -> Project:
    src_dir = str(CFG['container']['source'])
    tgt_dir = '/benchbuild'
    crun = '/usr/bin/crun'

    def from_source(image):
        # The image requires git, pip and a working python3.7 or better.
        image.run('mkdir', f'{tgt_dir}', runtime=crun)
        image.run('pip3', 'install', '-U', 'setuptools', runtime=crun)
        image.run('pip3',
                  'install',
                  tgt_dir,
                  mount=f'type=bind,src={src_dir},target={tgt_dir}',
                  runtime=crun)

    def from_pip(image):
        image.run('pip', 'install', 'benchbuild', runtime=crun)

    if bool(CFG['container']['from_source']):
        from_source(prj.container)
    else:
        from_pip(prj.container)
    return prj


def add_project_sources(prj: Project) -> Project:

    def setup_context() -> 'None':
        for version in prj.variant.values():
            src = version.owner
            src.version(local.cwd, str(version))

    prj.container.context(setup_context)
    prj.container.add('.', "/app/")

    return prj


def commit(prj: Project) -> Project:
    tag = mktag(prj)
    prj.container.commit(tag)
    prj.container.clear_context()

    return prj


def materialize(prj: Project) -> rx.Observable:
    return rx.combine_latest(rx.return_value(prj), from_tool(prj.container))
