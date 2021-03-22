"""
Describe usage of our default container/image domain.
"""
from benchbuild.environments.domain import model


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
