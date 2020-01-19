"""
"""
import json
import logging
import textwrap
from typing import Any

import attr
import defer

from benchbuild.project import Project
from benchbuild.settings import CFG
from benchbuild.utils.cmd import buildah

# Image declaration.
LOG = logging.getLogger(__name__)

__BUILDAH_DEFAULT_OPTS__ = [
    '--root',
    str(CFG['tmp_dir']), '--runroot',
    str(CFG['build_dir'])
]
__BUILDAH__ = buildah[__BUILDAH_DEFAULT_OPTS__]


def __buildah_cmd__(image_id: str, sub_command: str):
    cmd = __BUILDAH__[sub_command, image_id]
    return cmd


@attr.s
class Buildah:
    commands: defer.Deferred = attr.ib(
        default=attr.Factory(lambda: defer.Deferred()))
    in_progress: str = attr.ib(default='')
    image: str = attr.ib(default='')

    def finalize(self, tag: str):
        self.commit(tag)
        self.commands.callback()
        self.clean()
        self.in_progress = ''
        return self.commands.result

    def from_(self, base_img: str):
        def from__(_, from_img: str):
            self.in_progress = __BUILDAH__('from', from_img).strip()
            return self.in_progress

        self.commands.add_callback(from__, from_img=base_img)
        return self

    def bud(self, dockerfile: str):
        def bud_(_, dockerfile: str):
            return (
                __BUILDAH__['bud'] << textwrap.dedent(dockerfile))().strip()

        self.commands.add_callback(bud_, dockerfile=dockerfile)
        return self

    def add(self, src: str, dest: str):
        def add_(build_id: str, src: str, dest: str):
            __BUILDAH__('add', build_id, src, dest)
            return build_id

        self.commands.add_callback(add_, src, dest)
        return self

    def commit(self, tag: str):
        def commit_(build_id: str, tag: str):
            image_id = __BUILDAH__('commit', build_id, tag).strip()
            return image_id

        self.commands.add_callback(commit_, tag)
        return self

    def copy(self, src: str, dest: str):
        def copy_(build_id: str, src: str, dest: str):
            __BUILDAH__('copy', build_id, src, dest)
            return build_id

        self.commands.add_callback(copy_, src, dest)
        return self

    def run(self, *args):
        def run_(build_id: str, *args):
            __BUILDAH__('run', build_id, '--', *args)
            return build_id

        self.commands.add_callback(run_, *args)
        return self

    def clean(self):
        """Remove the intermediate container."""
        if self.in_progress:
            __BUILDAH__('rm', self.in_progress)


def instanciate_project_container(project: Project,
                                  env: Buildah,
                                  tag: str = 'latest'):
    """Instanciate a project container.
    """
    return env.finalize(f"{project.group}/{project.name}:{tag}")


def tag(project: Project) -> str:
    """Generate a container tag."""
    version_str = "-".join([str(var) for var in project.variant.values()])
    return f"{project.group}/{project.name}:{version_str}"


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
    results = __BUILDAH__('images', '--json', tag, retcode=[0, 1])
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
