"""
"""
import logging
import textwrap

import attr
import defer
from plumbum import FG
from plumbum.commands.base import BaseCommand

from benchbuild.settings import CFG
from benchbuild.utils.cmd import buildah

LOG = logging.getLogger(__name__)

__BUILDAH_DEFAULT_OPTS__ = [
    '--root', str(CFG['tmp_dir']),
    '--runroot', str(CFG['build_dir'])
]
__BUILDAH__ = buildah[__BUILDAH_DEFAULT_OPTS__]

def __buildah_cmd__(image_id: str, sub_command: str):
    cmd = __BUILDAH__[sub_command, image_id]
    return cmd

@attr.s
class Image:
    commands: defer.Deferred = attr.ib(
        default=attr.Factory(lambda: defer.Deferred()))
    build_image: str = attr.ib(default='')
    image: str = attr.ib(default='')

    def finalize(self, tag: str):
        self.commit(tag)
        self.commands.callback()
        self.clean()
        return self.commands.result

    def from_(self, base_img: str):
        def from__(_, from_img: str):
            self.build_image = __BUILDAH__('from', from_img).strip()
            return self.build_image
        self.commands.add_callback(from__, from_img=base_img)
        return self

    def bud(self, dockerfile: str):    
        def bud_(_, dockerfile: str):
            return (__BUILDAH__['bud'] << textwrap.dedent(dockerfile))().strip()
        self.commands.add_callback(bud_, dockerfile=dockerfile)

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
        if self.build_image:
            __BUILDAH__('rm', self.build_image)
