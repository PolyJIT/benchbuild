"""
Test declarative API
"""
from typing import Hashable

from benchbuild.environments.domain import declarative as decl
from benchbuild.environments.domain import model as m


def test_container_image_default_is_false():
    img = decl.ContainerImage()
    assert not bool(img)


def test_container_image_layer_is_true():
    img = decl.ContainerImage()
    img.from_('base')
    assert bool(img)


def test_container_image_can_model_from():
    img = decl.ContainerImage()
    img.from_('base')

    assert img == [m.FromLayer('base')]


def test_container_image_can_model_add():
    img = decl.ContainerImage()
    img.add(('a',), 'c')

    assert img == [m.AddLayer(('a',), 'c')]


def test_container_image_can_model_copy():
    img = decl.ContainerImage()
    img.copy_(('a',), 'c')

    assert img == [m.CopyLayer(('a',), 'c')]


def test_container_image_can_model_run():
    img = decl.ContainerImage()
    img.run('cmd', 'arg0', 'arg1')

    assert img == [m.RunLayer('cmd', (
        'arg0',
        'arg1',
    ), {})]


def test_container_image_can_model_context():
    img = decl.ContainerImage()
    img.context('test')

    assert img == [m.ContextLayer('test')]


def test_container_image_can_model_env():
    img = decl.ContainerImage()
    img.env(a='test')

    assert img == [m.UpdateEnv({'a': 'test'})]


def test_container_image_can_model_workingdir():
    img = decl.ContainerImage()
    img.workingdir('test')

    assert img == [m.WorkingDirectory('test')]


def test_container_image_can_model_entrypoint():
    img = decl.ContainerImage()
    img.entrypoint('cmd', 'arg0', 'arg1')

    assert img == [m.EntryPoint((
        'cmd',
        'arg0',
        'arg1',
    ))]


def test_container_image_can_model_command():
    img = decl.ContainerImage()
    img.command('cmd', 'arg0', 'arg1')

    assert img == [m.SetCommand((
        'cmd',
        'arg0',
        'arg1',
    ))]


def test_container_image_is_hashable():
    layers = decl.ContainerImage() \
        .from_('a') \
        .add(['a', 'b', 'c'], 'd') \
        .add(('a', 'b', 'c'), 'd') \
        .copy_(['a', 'b', 'c'], 'd') \
        .copy_(('a', 'b', 'c'), 'd') \
        .run('cmd', 'a', 'b', 'c', a='a', b='b', c='c') \
        .context(lambda: None).env(a='a', b='b', c='c') \
        .workingdir('a') \
        .entrypoint('a', 'b', 'c') \
        .command('a', 'b', 'c')

    img = m.Image('a', layers.base, layers)

    assert isinstance(img, Hashable)
