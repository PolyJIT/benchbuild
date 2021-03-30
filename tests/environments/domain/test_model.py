"""
Describe usage of our default container/image domain.
"""
from collections.abc import Hashable

from benchbuild.environments.domain import model


def describe_layers():

    def from_is_hashable():
        layer = model.FromLayer('a')
        assert isinstance(layer, Hashable)

    def add_is_hashable():
        layer = model.AddLayer(('a', 'b', 'c'), 'd')
        assert isinstance(layer, Hashable)

    def copy_is_hashable():
        layer = model.CopyLayer(('a', 'b', 'c'), 'd')
        assert isinstance(layer, Hashable)

    def run_is_hashable():
        layer = model.RunLayer(
            'cmd', ('a', 'b', 'c'), dict(a='a', b='b', c='c')
        )
        assert isinstance(layer, Hashable)

    def context_is_hashable():
        layer = model.ContextLayer(lambda: None)
        assert isinstance(layer, Hashable)

    def env_is_hashable():
        layer = model.UpdateEnv(dict(a='a', b='b', c='c'))
        assert isinstance(layer, Hashable)

    def workdir_is_hashable():
        layer = model.WorkingDirectory('a')
        assert isinstance(layer, Hashable)

    def entrypoint_is_hashable():
        layer = model.EntryPoint(('a', 'b', 'c'))
        assert isinstance(layer, Hashable)

    def cmd_is_hashable():
        layer = model.SetCommand(('a', 'b', 'c'))
        assert isinstance(layer, Hashable)


def describe_image():

    def image_requires_name_and_base():
        img = model.Image('name', model.FromLayer('base'), [])
        assert img.name == 'name'
        assert img.from_ == model.FromLayer('base')
        assert len(img.layers) == 0

    def can_append_layers_to_image():
        img = model.Image('-', model.FromLayer('-'), [model.FromLayer('base')])
        img.append(model.WorkingDirectory('abc'))

        assert img.layers == [
            model.FromLayer('base'),
            model.WorkingDirectory('abc')
        ]

    def can_prepend_layers_to_image():
        img = model.Image(
            '-', model.FromLayer('-'), [model.WorkingDirectory('abc')]
        )
        img.prepend(model.FromLayer('base'))

        assert img.layers == [
            model.FromLayer('base'),
            model.WorkingDirectory('abc')
        ]

    def is_hashable():
        layers = [
            model.FromLayer('a'),
            model.AddLayer(('a', 'b', 'c'), 'd'),
            model.CopyLayer(('a', 'b', 'c'), 'd'),
            model.RunLayer('cmd', ('a', 'b', 'c'), dict(a='a', b='b', c='c')),
            model.ContextLayer(lambda: None),
            model.UpdateEnv(dict(a='a', b='b', c='c')),
            model.WorkingDirectory('a'),
            model.EntryPoint(('a', 'b', 'c')),
            model.SetCommand(('a', 'b', 'c'))
        ]
        img = model.Image('-', model.FromLayer('-'), layers)
        assert isinstance(img, Hashable)
