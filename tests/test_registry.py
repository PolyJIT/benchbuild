# pylint: disable=redefined-outer-name
import copy
import typing as tp

import pytest

from benchbuild import Experiment, Project
from benchbuild.experiment import ExperimentRegistry
from benchbuild.project import ProjectRegistry
from benchbuild.utils import actions


def empty_afp(exp: Experiment, prj: Project) -> tp.List[actions.Step]:
    del exp, prj
    return []


def empty_run_tests(prj: Project) -> None:
    del prj


def empty_compile(prj: Project) -> None:
    del prj


@pytest.fixture
def registry():
    restore = copy.deepcopy(ExperimentRegistry.experiments)
    ExperimentRegistry.experiments.clear()
    yield ExperimentRegistry
    ExperimentRegistry.experiments = restore


@pytest.fixture
def project_registry():
    ProjectRegistry.projects.clear()
    return ProjectRegistry


def make_experiment(
    cls_name: str,
    name: tp.Optional[str] = None,
    bases: tp.Tuple[type, ...] = (Experiment,),
    always_set: bool = True,
) -> tp.Type[Experiment]:
    """
    Dynamically create a subclass of Experiment to test registration.
    """
    if name or always_set:
        return type(cls_name, bases, {"actions_for_project": empty_afp, "NAME": name})

    return type(
        cls_name,
        bases,
        {
            "actions_for_project": empty_afp,
        },
    )


def make_project(
    cls_name: str,
    bases: tp.Tuple[type, ...] = (Project,),
    always_set: bool = True,
    **attrs: str,
) -> tp.Type[Project]:
    """
    Dynamically create a subclass of Project to test registration
    """

    interface = {"run_tests": empty_run_tests, "compile": empty_compile}

    if attrs or always_set:
        interface.update(attrs)
        return type(cls_name, bases, interface)

    return type(cls_name, bases, interface)


def test_experiment_registry_named(registry: ExperimentRegistry):
    """
    An experiment must have a NAME to be registered.
    """
    cls = make_experiment("Child", "Child")
    assert "Child" in registry.experiments
    assert registry.experiments["Child"] == cls


def test_project_registry_named(project_registry: ProjectRegistry):
    """
    A project must have a NAME, GROUP and DOMAIN registered.
    """
    cls = make_project("Child", NAME="C", DOMAIN="CD", GROUP="CG")

    assert "C/CG" in project_registry.projects
    assert project_registry.projects["C/CG"] == cls
    assert project_registry.projects["C/CG"].NAME == "C"
    assert project_registry.projects["C/CG"].DOMAIN == "CD"
    assert project_registry.projects["C/CG"].GROUP == "CG"


def test_registry_unnamed(registry: ExperimentRegistry):
    """
    An experiment must not lack a NAME attribute to be registered.
    """
    cls = make_experiment("UnnamedChild", always_set=False)
    assert cls not in registry.experiments.values()


def test_project_registry_unnamed(project_registry: ProjectRegistry):
    """
    A project must not lack a NAME, DOMAIN, or GROUP attribute to be
    registered.
    """
    cls = make_project("UnnamedChild", always_set=False)
    assert cls not in project_registry.projects.values()


def test_registry_named_from_unnamed(registry: ExperimentRegistry):
    """
    Derive an experiment from an incomplete (e.g., abstract) experiment.

    This is allowed, and should work. The partial experiment is not allowed
    to be included in the registry.
    """
    unnamed = make_experiment("UnnamedChild", always_set=False)
    named = make_experiment("NamedFromUnnamed", "Named", (unnamed,))
    assert "Named" in registry.experiments
    assert registry.experiments["Named"] == named
    assert unnamed not in registry.experiments.values()


def test_project_registry_named_from_unnamed(project_registry: ProjectRegistry):
    """
    Derive an project from an incomplete (e.g., abstract) project.

    This is allowed, and should work. The partial project is not allowed
    to be included in the registry.
    """
    unnamed = make_project("UnnamedChild", always_set=False)
    named = make_project(
        "NamedFromUnnamed", (unnamed,), NAME="NC", GROUP="NCG", DOMAIN="NCD"
    )
    assert "NC/NCG" in project_registry.projects
    assert project_registry.projects["NC/NCG"] == named
    assert project_registry.projects["NC/NCG"].NAME == "NC"
    assert project_registry.projects["NC/NCG"].DOMAIN == "NCD"
    assert project_registry.projects["NC/NCG"].GROUP == "NCG"
    assert unnamed not in project_registry.projects.values()


def test_registry_unnamed_from_named(registry: ExperimentRegistry):
    """
    Derive from an existing valid experiment and forget to set a NAME attr.

    This would overwrite an existing experiment in the registry and is
    forbidden.
    """
    named = make_experiment("Child", "Child")
    unnamed = make_experiment(
        "UnnamedFromNamed", name=None, bases=(named,), always_set=False
    )

    assert unnamed not in registry.experiments.values()


def test_project_registry_unnamed_from_named(project_registry: ProjectRegistry):
    """
    Derive from an existing valid project and forget to set all attr.

    This would overwrite an existing project in the registry and is forbidden.
    """
    named = make_project("Child", NAME="C", DOMAIN="CD", GROUP="CG")
    unnamed = make_project(
        "UnnamedFromNamed",
        (named,),
        NAME=None,
        DOMAIN=None,
        GROUP=None,
        always_set=False,
    )

    assert unnamed not in project_registry.projects.values()
