"""Tests for the schedule_tree parser."""
import benchbuild.utils.schedule_tree as st

def test_domain_1():
    res = st._DOMAIN.parseString('domain: ""')
    assert res != None

def test_domain_2():
    res = st._DOMAIN.parseString('domain: "{ Stmt2[i1, i1] : 0 <= i0 <= 254 and 0 <= i1 <= 255 }"')
    assert res != None

def test_schedule_1():
    res = st._SCHEDULE.parseString('schedule: ""')
    assert res != None

def test_schedule_2():
    res = st._SCHEDULE.parseString('schedule: "[{ Stmt2[i0, i1] -> [(i0)] }]"')
    assert res != None

def test_filter_1():
    res = st._FILTER_NODE.parseString('filter: ""')
    assert res != None

def test_mark_1():
    res = st._MARK.parseString('mark: ""')
    assert res != None

def test_permutable_1():
    res = st._PERMUTABLE.parseString('permutable: 1')
    assert res != None

def test_permutable_2():
    res = st._PERMUTABLE.parseString('permutable: 0')
    assert res != None

def test_coincident_1():
    res = st._COINCIDENT.parseString('coincident: [0]')
    assert res != None

def test_coincident_2():
    res = st._COINCIDENT.parseString('coincident: [0, 1]')
    assert res != None

def test_sequence_1():
    res = st._SEQUENCE.parseString('sequence: [ { filter: "" } ]')
    assert res != None

def test_sequence_2():
    res = st._SEQUENCE.parseString('sequence: [ { filter: "", child: { permutable: 1 } } ]')
    assert res != None

def test_schedule_tree_1():
    test_1 = \
'{ domain: "{ Stmt2[i1, i1] : 0 <= i0 <= 254 and 0 <= i1 <= 255 }", child: { schedule: "[{ Stmt2[i0, i1] -> [(i0)] }]", child: { schedule: "[{ Stmt2[i0, i1] -> [(i1)] }]" } } }'
    res = st.parse_schedule_tree(test_1)
    assert res != None

def test_schedule_tree_2():
    test_2 = \
'{ domain: " ", child: { schedule: "", child: { sequence: [ { filter: "", child: { schedule: "" } } ] } } }'
    res = st.parse_schedule_tree(test_2)
    assert res != None

def test_schedule_tree_3():
    test_3 = \
'{ domain: "", child: { schedule: "", child: { sequence: [ { filter: "", child: { schedule: "", permutable: 1, coincident: [ 1 ] } }, { filter: "", child: { mark: "", child: { schedule: "", permutable: 1, coincident: [ 1, 1 ], child: { mark: "", child: { schedule: "", permutable: 1, coincident: [ 1, 1 ] } } } } }, { filter: "", child: { mark: "", child: { schedule: "", permutable: 1, coincident: [ 1, 1 ], child: { mark: "", child: { schedule: "", permutable: 1, coincident: [ 1, 1 ] } } } } }, { filter: "", child: { mark: "", child: { schedule: "", permutable: 1, coincident: [ 1, 1 ], child: { mark: "", child: { schedule: "", permutable: 1, coincident: [ 1, 1 ] } } } } } ] } } }'
    res = st.parse_schedule_tree(test_3)
    assert res != None