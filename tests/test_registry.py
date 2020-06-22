# pylint: disable=redefined-outer-name
import typing as tp

import pytest

from benchbuild import Experiment, Project
from benchbuild.experiment import ExperimentRegistry
from benchbuild.utils import actions


def empty_afp(exp: Experiment, prj: Project) -> tp.List[actions.Step]:
    del exp, prj
    return []


@pytest.fixture
def registry():
    ExperimentRegistry.experiments.clear()
    return ExperimentRegistry


def make_experiment(cls_name: str,
                    name: tp.Optional[str] = None,
                    bases: tp.Tuple[type, ...] = (Experiment,),
                    always_set: bool = True) -> tp.Type[Experiment]:
    """
    Dynamically create a subclass of Experiment to test registration.
    """
    print(cls_name, name, bases, always_set)
    if name or always_set:
        print('1')
        return type(cls_name, bases, {
            'actions_for_project': empty_afp,
            'NAME': name
        })

    print('2')
    return type(cls_name, bases, {
        'actions_for_project': empty_afp,
    })


def test_registry_named(registry: ExperimentRegistry):
    """
    An experiment must have a NAME to be registered.
    """
    cls = make_experiment('Child', 'Child')
    assert 'Child' in registry.experiments
    assert registry.experiments['Child'] == cls


def test_registry_unnamed(registry: ExperimentRegistry):
    """
    An experiment must not lack a NAME attribute to be registered.
    """
    cls = make_experiment('UnnamedChild', always_set=False)
    assert cls not in registry.experiments.values()


def test_registry_named_from_unnamed(registry: ExperimentRegistry):
    """
    Derive an experiment from an incomplete (e.g., abstract) experiment.

    This is allowed, and should work. The partial experiment is not allowed
    to be included in the registry.
    """
    unnamed = make_experiment('UnnamedChild', always_set=False)
    named = make_experiment('NamedFromUnnamed', 'Named', (unnamed,))
    assert 'Named' in registry.experiments
    assert registry.experiments['Named'] == named
    assert unnamed not in registry.experiments.values()


def test_registry_unnamed_from_named(registry: ExperimentRegistry):
    """
    Derive from an existing valid experiment and forget to set a NAME attr.

    This would overwrite an existing experiment in the registry and is
    forbidden.
    """
    named = make_experiment('Child', 'Child')
    unnamed = make_experiment('UnnamedFromNamed',
                              name=None,
                              bases=(named,),
                              always_set=False)

    assert unnamed not in registry.experiments.values()
