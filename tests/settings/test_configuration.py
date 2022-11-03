import uuid

import pytest

from benchbuild.utils.settings import (
    Configuration,
    _INNER_NODE_SCHEMA,
    _INNER_NODE_VALUE,
)


@pytest.fixture
def bb():
    yield Configuration('bb')


def test_inner_nodes_dict_can_be_inner_node():
    assert _INNER_NODE_VALUE.is_valid({'default': 0, 'desc': 'a'})


def test_inner_nodes_dict_can_be_nested_once():
    assert _INNER_NODE_SCHEMA.is_valid({'a': {'default': 0, 'desc': 'a'}})


def test_inner_nodes_inner_node_value_can_be_assigned(bb):
    bb['a'] = {'default': 0, 'desc': 'a'}
    assert _INNER_NODE_SCHEMA.is_valid(bb.node)


def test_inner_nodes_inner_node_needs_to_be_initialized():
    cfg = Configuration('fresh')
    cfg['a'] = {'default': 0, 'desc': 'a'}

    assert not hasattr(cfg['a'].node, 'value')

    cfg.init_from_env()
    assert hasattr(cfg['a'], 'value')


def test_simple_construction(bb):
    """Test simple construction."""

    bb['test'] = 42
    assert repr(bb['test']) == 'BB_TEST=42'
    assert str(bb['test']) == '42'
    assert type(bb['test']) == Configuration


def test_value(bb):
    """Test value retrieval."""
    bb['x'] = {"y": {"value": None}, "z": {"value": 2}}
    assert bb['x']['y'].value == None
    assert bb['x']['z'].value == 2
    assert repr(bb['x'].value) == "BB_X_Y=null\nBB_X_Z=2"


def test_append_to_list(bb):
    bb['t'] = []
    assert repr(bb['t']) == 'BB_T="[]"'

    bb['t'] += 'a'
    assert repr(bb['t']) == 'BB_T="[a]"'


def test_append_to_scalar(bb):
    bb['t'] = 0
    assert repr(bb['t']) == "BB_T=0"

    with pytest.raises(TypeError):
        bb['t'] += 2


def test_conversion_to_int(bb):
    bb['i'] = 1
    assert int(bb['i']) == 1

    bb['d'] = []
    with pytest.raises(TypeError):
        int(bb['d'])


def test_conversion_to_bool(bb):
    bb['b'] = True
    assert bool(bb['b']) == True

    bb['b'] = []
    assert bool(bb['b']) == False


def test_representation(bb):
    bb['int'] = {'default': 3}
    assert repr(bb['int']) == 'BB_INT=3'

    bb['str'] = {'default': 'test'}
    assert repr(bb['str']) == 'BB_STR=test'

    bb['bool'] = {'default': True}
    assert repr(bb['bool']) == 'BB_BOOL=true'

    bb['dict'] = {'default': {'test': True}}
    assert repr(bb['dict']) == 'BB_DICT="{test: true}"'

    bb['uuid'] = {'default': uuid.UUID('cc3702ca-699a-4aa6-8226-4c938f294d9b')}
    assert repr(bb['uuid']) == 'BB_UUID=cc3702ca-699a-4aa6-8226-4c938f294d9b'

    bb['nested_uuid'] = {
        'A': {
            'default': {
                'a': uuid.UUID('cc3702ca-699a-4aa6-8226-4c938f294d9b')
            }
        }
    }
    assert repr(bb['nested_uuid']['A'].value) == \
        'BB_NESTED_UUID_A="{a: cc3702ca-699a-4aa6-8226-4c938f294d9b}"'
