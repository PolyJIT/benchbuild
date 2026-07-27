"""
The user has to provide at least a compiler_extension.

This enables compilation experiments by default. Runtime experiments
can remain fully optional. These typically require external assets as
test input and are more complicated to design.

However, projects are not responsible for the configuration of an extension.
This has to be done by an experirment. We could have opted for a mandatory
initialization argument to each project. This would break all existing
setups and require a more complicated initialization sequence for projects
inside an experiment.

Given that we have to provide documentation about this anyway, we might
as well fail dynamically, if the user forgets to configure it. We won't
make any assumptions about the quality/types of the 'extensions'. This
can be enforced on the project level using attr's validators.
"""

import pytest

from benchbuild import extensions, project, source
from benchbuild.environments.domain.declarative import ContainerImage


class DummyPrj(project.Project):
    NAME: str = "TestMissingExtension"
    GROUP: str = "TestMissingExtension"
    DOMAIN: str = "TestMissingExtension"
    SOURCE = [source.nosource()]
    CONTAINER: ContainerImage = ContainerImage().from_("benchbuild:alpine")

    def run_tests(self):
        raise NotImplementedError()


def test_extensions_missing_compiler_extension_fails():
    """
    If the user forgets to configure the runtime extension, we fail hard.
    """
    prj = DummyPrj()
    ext = prj.compiler_extension

    with pytest.raises(extensions.base.ExtensionRequired):
        ext()


def test_extensions_any_user_configured_extension_does_not_fail():
    """
    As long as the user sets *anything* we are fine for now.

    This, obviously, won't do anything useful.
    """
    prj = DummyPrj()
    prj.compiler_extension = lambda: True
    ext = prj.compiler_extension

    assert ext()
