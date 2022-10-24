"""
Describe usage of our default container/image domain.
"""
from typing import Hashable

from benchbuild.environments.domain import model


def test_layers_from_is_hashable():
    layer = model.FromLayer('a')
    assert isinstance(layer, Hashable)


def test_layers_add_is_hashable():
    layer = model.AddLayer(('a', 'b', 'c'), 'd')
    assert isinstance(layer, Hashable)


def test_layers_copy_is_hashable():
    layer = model.CopyLayer(('a', 'b', 'c'), 'd')
    assert isinstance(layer, Hashable)


def test_layers_run_is_hashable():
    layer = model.RunLayer('cmd', ('a', 'b', 'c'), dict(a='a', b='b', c='c'))
    assert isinstance(layer, Hashable)


def test_layers_context_is_hashable():
    layer = model.ContextLayer(lambda: None)
    assert isinstance(layer, Hashable)


def test_layers_env_is_hashable():
    layer = model.UpdateEnv(dict(a='a', b='b', c='c'))
    assert isinstance(layer, Hashable)


def test_layers_workdir_is_hashable():
    layer = model.WorkingDirectory('a')
    assert isinstance(layer, Hashable)


def test_layers_entrypoint_is_hashable():
    layer = model.EntryPoint(('a', 'b', 'c'))
    assert isinstance(layer, Hashable)


def test_layers_cmd_is_hashable():
    layer = model.SetCommand(('a', 'b', 'c'))
    assert isinstance(layer, Hashable)


def test_image_image_requires_name_and_base():
    img = model.Image('name', model.FromLayer('base'), [])
    assert img.name == 'name'
    assert img.from_ == model.FromLayer('base')
    assert len(img.layers) == 0


def test_image_can_append_layers_to_image():
    img = model.Image('-', model.FromLayer('-'), [model.FromLayer('base')])
    img.append(model.WorkingDirectory('abc'))

    assert img.layers == [
        model.FromLayer('base'),
        model.WorkingDirectory('abc')
    ]


def test_image_can_prepend_layers_to_image():
    img = model.Image(
        '-', model.FromLayer('-'), [model.WorkingDirectory('abc')]
    )
    img.prepend(model.FromLayer('base'))

    assert img.layers == [
        model.FromLayer('base'),
        model.WorkingDirectory('abc')
    ]


def test_image_is_hashable():
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
