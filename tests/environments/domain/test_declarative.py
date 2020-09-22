"""
Test declarative API
"""
from benchbuild.environments.domain import declarative as decl
from benchbuild.environments.domain import model as m


def describe_container_image():

    def can_model_from():
        img = decl.ContainerImage()
        img.from_('base')

        assert img == [m.FromLayer('base')]

    def can_model_add():
        img = decl.ContainerImage()
        img.add(('a',), 'c')

        assert img == [m.AddLayer(('a',), 'c')]

    def can_model_copy():
        img = decl.ContainerImage()
        img.copy_(('a',), 'c')

        assert img == [m.CopyLayer(('a',), 'c')]

    def can_model_run():
        img = decl.ContainerImage()
        img.run('cmd', 'arg0', 'arg1')

        assert img == [m.RunLayer('cmd', (
            'arg0',
            'arg1',
        ), {})]

    def can_model_context():
        img = decl.ContainerImage()
        img.context('test')

        assert img == [m.ContextLayer('test')]

    def can_model_env():
        img = decl.ContainerImage()
        img.env(a='test')

        assert img == [m.UpdateEnv({'a': 'test'})]

    def can_model_workingdir():
        img = decl.ContainerImage()
        img.workingdir('test')

        assert img == [m.WorkingDirectory('test')]

    def can_model_entrypoint():
        img = decl.ContainerImage()
        img.entrypoint('cmd', 'arg0', 'arg1')

        assert img == [m.EntryPoint((
            'cmd',
            'arg0',
            'arg1',
        ))]

    def can_model_command():
        img = decl.ContainerImage()
        img.command('cmd', 'arg0', 'arg1')

        assert img == [m.SetCommand((
            'cmd',
            'arg0',
            'arg1',
        ))]
