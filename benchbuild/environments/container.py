"""
"""
import json
import logging
import textwrap
from typing import Any, Callable, List, Union

import attr
import defer

from benchbuild.project import Project
from benchbuild.settings import CFG

# Image declaration.
LOG = logging.getLogger(__name__)

__CONTAINER_ROOT__ = str(CFG['container']['root'])
__CONTAINER_RUNROOT__ = str(CFG['container']['runroot'])
__BUILDAH_DEFAULT_OPTS__ = [
    '--root', __CONTAINER_ROOT__, '--runroot', __CONTAINER_RUNROOT__
]


def __buildah__():
    from benchbuild.utils.cmd import buildah
    return buildah[__BUILDAH_DEFAULT_OPTS__]


CommandFunc = Callable[[str], Union[str, None]]


@attr.s
class DeclarativeTool:
    commands: List[CommandFunc] = attr.ib(default=attr.Factory(list))


@attr.s
class Podman(DeclarativeTool):
    pass


@attr.s
class Buildah(DeclarativeTool):
    in_progress: str = attr.ib(default='')
    image: str = attr.ib(default='')

    def finalize(self, tag: str):
        self.commit(tag)

        chain = defer.Deferred()
        for cmd in self.commands:
            chain.add_callback(cmd)
        chain.callback()

        self.clean()
        self.in_progress = ''
        return chain.result

    def from_(self, base_img: str):

        def from__(_):
            self.in_progress = __buildah__()('from', base_img).strip()
            return self.in_progress

        self.commands.append(from__)
        return self

    def bud(self, dockerfile: str):

        def bud_(_):
            return (
                __buildah__()['bud'] << textwrap.dedent(dockerfile))().strip()

        self.commands.append(bud_)
        return self

    def add(self, src: str, dest: str):

        def add_(build_id: str):
            __buildah__()('add', build_id, src, dest)
            return build_id

        self.commands.append(add_)
        return self

    def commit(self, tag: str):

        def commit_(build_id: str):
            image_id = __buildah__()('commit', build_id, tag).strip()
            return image_id

        self.commands.append(commit_)
        return self

    def copy(self, src: str, dest: str):

        def copy_(build_id: str):
            __buildah__()('copy', build_id, src, dest)
            return build_id

        self.commands.append(copy_)
        return self

    def run(self, *args, **kwargs):

        def run_(build_id: str):
            kws = []
            for name, value in dict(kwargs).items():
                kws.append(f'--{name}')
                kws.append(f'{str(value)}')

            __buildah__()('run', *kws, build_id, '--', *args)
            return build_id

        self.commands.append(run_)
        return self

    def clean(self):
        """Remove the intermediate container."""
        if self.in_progress:
            __buildah__()('rm', self.in_progress)


def instanciate_project_container(project: Project,
                                  env: Buildah,
                                  tag: str = 'latest'):
    """Instanciate a project container.
    """
    return env.finalize(f"{project.group}/{project.name}:{tag}")


def tag(project: Project) -> str:
    """Generate a container tag."""
    version_str = "-".join([str(var) for var in project.variant.values()])
    return f"{project.name}/{project.group}:{version_str}"


def finalize_project_container(project: Project, env: Buildah):
    """
    [summary]

    Args:
        project (Project): [description]
        env (Buildah): [description]
    """
    return env.finalize(tag(project))


def by_tag(tag: str) -> Any:
    """Find a container image by tag."""
    results = __buildah__()('images', '--json', tag, retcode=[0, 1])
    if results:
        results = json.loads(results)
    for res in results:
        yield res


def by_project(project: Project) -> Any:
    """Find a container image by project."""
    image_tag = tag(project)
    for res in by_tag(image_tag):
        yield res


# Environment definition.
