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
from typing import Any, Callable, Dict, List, Optional, Union

import attr
import rx
import rx.operators as ops
from rx.core.typing import Observable

from benchbuild.project import Project
from benchbuild.settings import CFG
from benchbuild.utils.cmd import buildah

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

CommandFunc = Callable[[str], Union[str, None]]
CallChain = List[CommandFunc]


@attr.s
class DeclarativeTool:
    chain: CallChain = attr.ib(default=attr.Factory(list))

    def __len__(self) -> int:
        return len(self.chain)


def create_observable_callchain(tool: DeclarativeTool) -> Observable:
    return rx.from_iterable(tool.chain).pipe(
        ops.scan(lambda acc, f: f(acc), None))


@attr.s
class Buildah(DeclarativeTool):
    image: str = attr.ib(default='')

    def from_(self, base_img: str) -> 'Buildah':
        """
        Add a 'buildah from' command into the chain.

        Args:
            base_img: The base image to start building from.

        Returns:
            self
        """

        def from__(_):
            return __BH_FROM__(base_img).strip()

        self.chain.append(from__)
        return self

    def bud(self, dockerfile: str) -> 'Buildah':
        """
        Add a 'buildah bud' command into the chain.

        Args:
            dockerfile: The Dockerfile as input string.

        Returns:
            self
        """

        def bud_(_):
            return (__BH_BUD__ << textwrap.dedent(dockerfile))().strip()

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

        def add_(build_id: str):
            __BH_ADD__(build_id, src, dest)
            return build_id

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

        def commit_(build_id: str):
            return __BH_COMMIT__(build_id, tag).strip()

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

        def copy_(build_id: str):
            __BH_COPY__(build_id, src, dest)
            return build_id

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

        def run_(build_id: str):
            kws = []
            for name, value in dict(kwargs).items():
                kws.append(f'--{name}')
                kws.append(f'{str(value)}')

            __BH_RUN__(*kws, build_id, '--', *args)
            return build_id

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


def by_project(project: Project) -> Any:
    """
    Find a container image by project.

    Args:
        project: The project to search an image for.

    Returns:

    """

    def mktag(project: Project) -> str:
        """Generate a container tag."""
        version_str = "-".join([str(var) for var in project.variant.values()])
        return f"{project.name}/{project.group}:{version_str}"

    image_tag = mktag(project)
    for res in by_tag(image_tag):
        yield res


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
