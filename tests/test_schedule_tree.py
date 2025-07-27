"""Tests for the schedule_tree parser."""

import benchbuild.utils.schedule_tree as st


def test_domain_1():
    res = st.DOMAIN.parseString('domain: ""')
    assert res != None


def test_domain_2():
    res = st.DOMAIN.parseString(
        'domain: "{ Stmt2[i1, i1] : 0 <= i0 <= 254 and 0 <= i1 <= 255 }"'
    )
    assert res != None


def test_schedule_1():
    res = st.SCHEDULE.parseString('schedule: ""')
    assert res != None


def test_schedule_2():
    res = st.SCHEDULE.parseString('schedule: "[{ Stmt2[i0, i1] -> [(i0)] }]"')
    assert res != None


def test_filter_1():
    res = st.FILTER.parseString('filter: ""')
    assert res != None


def test_mark_1():
    res = st.MARK.parseString('mark: ""')
    assert res != None


def test_permutable_1():
    res = st.PERMUTABLE.parseString("permutable: 1")
    assert res != None


def test_permutable_2():
    res = st.PERMUTABLE.parseString("permutable: 0")
    assert res != None


def test_coincident_1():
    res = st.COINCIDENT.parseString("coincident: [0]")
    assert res != None


def test_coincident_2():
    res = st.COINCIDENT.parseString("coincident: [0, 1]")
    assert res != None


def test_sequence_1():
    res = st.SEQUENCE.parseString('sequence: [ { filter: "" } ]')
    assert res != None


def test_sequence_2():
    res = st.SEQUENCE.parseString(
        'sequence: [ { filter: "", child: { permutable: 1 }}]'
    )
    assert res != None


def test_schedule_tree_1():
    test_1 = (
        '{ domain: "{ Stmt2[i1, i1] : 0 <= i0 <= 254 and 0 <= i1 <= 255 }", '
        "child: { "
        'schedule: "[{ Stmt2[i0, i1] -> [(i0)] }]", '
        "child: { "
        'schedule: "[{ Stmt2[i0, i1] -> [(i1)] }]" '
        "} "
        "} "
        "}"
    )
    res = st.parse_schedule_tree(test_1)
    assert res != None


def test_schedule_tree_2():
    test_2 = (
        '{ domain: " ", '
        'child: { schedule: "", '
        'child: { sequence: [ { filter: "", '
        'child: { schedule: "" } } ] } } }'
    )
    res = st.parse_schedule_tree(test_2)
    assert res != None


def test_schedule_tree_3():
    test_3 = '{ domain: "", child: { schedule: "", child: { sequence: [ { filter: "", child: { schedule: "", permutable: 1, coincident: [ 1 ] } }, { filter: "", child: { mark: "", child: { schedule: "", permutable: 1, coincident: [ 1, 1 ], child: { mark: "", child: { schedule: "", permutable: 1, coincident: [ 1, 1 ] } } } } }, { filter: "", child: { mark: "", child: { schedule: "", permutable: 1, coincident: [ 1, 1 ], child: { mark: "", child: { schedule: "", permutable: 1, coincident: [ 1, 1 ] } } } } }, { filter: "", child: { mark: "", child: { schedule: "", permutable: 1, coincident: [ 1, 1 ], child: { mark: "", child: { schedule: "", permutable: 1, coincident: [ 1, 1 ] } } } } } ] } } }'
    res = st.parse_schedule_tree(test_3)
    assert res != None


def test_schedule_tree_4():
    test_4 = (
        '{ domain: "[p_0, p_1, p_2] -> { Stmt6[i0, i1] : 0 <= i0 < p_0 and 0 <= i1 < p_1; Stmt14[i0, i1, i2] : 0 <= i0 < p_0 and 0 <= i1 < p_2 and 0 <= i2 < p_1 }", '
        'child: { sequence: [ { filter: "[p_0, p_1, p_2] -> { Stmt6[i0, i1] }", '
        'child: { mark: "1st level tiling - Tiles", child: { schedule: "[p_0, p_1, p_2] -> [{ Stmt6[i0, i1] -> [(floor((i0)/32))] }, { Stmt6[i0, i1] -> [(floor((i1)/32))] }]", '
        "permutable: 1, "
        "coincident: [ 1, 1 ], "
        'child: { mark: "1st level tiling - Points", '
        'child: { mark: "Register tiling - Tiles", '
        'child: { schedule: "[p_0, p_1, p_2] -> [{ Stmt6[i0, i1] -> [(floor((i0)/2) - 16*floor((i0)/32))] }, { Stmt6[i0, i1] -> [(floor((i1)/2) - 16*floor((i1)/32))] }]", '
        "permutable: 1, "
        "coincident: [ 1, 1 ], "
        'child: { mark: "Register tiling - Points", child: { schedule: "[p_0, p_1, p_2] -> [{ Stmt6[i0, i1] -> [(i0 - 2*floor((i0)/2))] }, { Stmt6[i0, i1] -> [(i1 - 2*floor((i1)/2))] }]", permutable: 1, coincident: [ 1, 1 ], options: "{ unroll[i0] : 0 <= i0 <= 1 }" } } } } } } } }, { filter: "[p_0, p_1, p_2] -> { Stmt14[i0, i1, i2] }", child: { mark: "Inter iteration alias-free", child: { mark: "1st level tiling - Tiles", child: { schedule: "[p_0, p_1, p_2] -> [{ Stmt14[i0, i1, i2] -> [(floor((i2)/1024))] }, { Stmt14[i0, i1, i2] -> [(floor((i1)/384))] }]", child: { extension: "[p_0, p_1, p_2] -> { [i0, i1] -> CopyStmt_0[0, o1, o2] : p_0 > 0 and o1 >= 384i1 and 0 <= o1 <= 383 + 384i1 and o1 < p_2 and o2 >= 1024i0 and 0 <= o2 <= 1023 + 1024i0 and o2 < p_1 }", child: { sequence: [ { filter: "[p_0, p_1, p_2] -> { CopyStmt_0[i0, i1, i2] }" }, { filter: "[p_0, p_1, p_2] -> { Stmt14[i0, i1, i2] }", child: { schedule: "[p_0, p_1, p_2] -> [{ Stmt14[i0, i1, i2] -> [(floor((i0)/64))] }]", child: { extension: "[p_0, p_1, p_2] -> { [0, i1, i2] -> CopyStmt_1[o0, o1, 0] : p_1 > 0 and o0 >= 64i2 and 0 <= o0 <= 63 + 64i2 and o0 < p_0 and o1 >= 384i1 and 0 <= o1 <= 383 + 384i1 and o1 < p_2 }", child: { sequence: [ { filter: "[p_0, p_1, p_2] -> { CopyStmt_1[i0, i1, i2] }" }, { filter: "[p_0, p_1, p_2] -> { Stmt14[i0, i1, i2] }", child: { mark: "1st level tiling - Points", child: { mark: "Register tiling - Tiles", child: { schedule: "[p_0, p_1, p_2] -> [{ Stmt14[i0, i1, i2] -> [(floor((i2)/4) - 256*floor((i2)/1024))] }, { Stmt14[i0, i1, i2] -> [(floor((i0)/4) - 16*floor((i0)/64))] }, { Stmt14[i0, i1, i2] -> [(i1 - 384*floor((i1)/384))] }]", options: "[p_0, p_1, p_2] -> { isolate[[i0, i1, i2] -> [i3, i4, i5]] : i3 >= 0 and -256i0 <= i3 <= 255 and 4i3 <= -4 + p_1 - 1024i0 and i4 >= 0 and -16i2 <= i4 <= 15 and 4i4 <= -4 + p_0 - 64i2 and i5 >= 0 and -384i1 <= i5 <= 383 and i5 < p_2 - 384i1; separate[i0] : 0 <= i0 <= 2 }", child: { mark: "Loop Vectorizer Disabled", child: { mark: "Register tiling - Points", child: { schedule: "[p_0, p_1, p_2] -> [{ Stmt14[i0, i1, i2] -> [(i0 - 4*floor((i0)/4))] }, { Stmt14[i0, i1, i2] -> [(i2 - 4*floor((i2)/4))] }, { Stmt14[i0, i1, i2] -> [(0)] }]", options: "[p_0, p_1, p_2] -> { isolate[[i0, i1, i2, i3, i4, i5] -> [i6, i7, i8]] : i3 >= 0 and -256i0 <= i3 <= 255 and 4i3 <= -4 + p_1 - 1024i0 and i4 >= 0 and -16i2 <= i4 <= 15 and 4i4 <= -4 + p_0 - 64i2 and i5 >= 0 and -384i1 <= i5 <= 383 and i5 < p_2 - 384i1; unroll[i0] : 0 <= i0 <= 2; [isolate[] -> unroll[i0]] : 0 <= i0 <= 2 }" } } } } } } } ] } } } } ] } } } } } } ] } }'
    )
    res = st.parse_schedule_tree(test_4)
    assert res != None


def test_schedule_tree_5():
    test_5 = '{ domain: "{ Stmt14[i0, i1, i2] : 0 <= i0 <= 1999 and 0 <= i1 <= 2599 and 0 <= i2 <= 2299; Stmt6[i0, i1] : 0 <= i0 <= 1999 and 0 <= i1 <= 2299 }", child: { sequence: [ { filter: "{ Stmt6[i0, i1] }", child: { mark: "1st level tiling - Tiles", child: { schedule: "[{ Stmt6[i0, i1] -> [(floor((i0)/32))] }, { Stmt6[i0, i1] -> [(floor((i1)/32))] }]", permutable: 1, coincident: [ 1, 1 ], child: { mark: "1st level tiling - Points", child: { mark: "Register tiling - Tiles", child: { schedule: "[{ Stmt6[i0, i1] -> [(floor((i0)/2) - 16*floor((i0)/32))] }, { Stmt6[i0, i1] -> [(floor((i1)/2) - 16*floor((i1)/32))] }]", permutable: 1, coincident: [ 1, 1 ], child: { mark: "Register tiling - Points", child: { schedule: "[{ Stmt6[i0, i1] -> [(i0 - 2*floor((i0)/2))] }, { Stmt6[i0, i1] -> [(i1 - 2*floor((i1)/2))] }]", permutable: 1, coincident: [ 1, 1 ], options: "{ unroll[i0] : 0 <= i0 <= 1 }" } } } } } } } }, { filter: "{ Stmt14[i0, i1, i2] }", child: { mark: "1st level tiling - Tiles", child: { schedule: "[{ Stmt14[i0, i1, i2] -> [(floor((i0)/32))] }, { Stmt14[i0, i1, i2] -> [(floor((i2)/32))] }, { Stmt14[i0, i1, i2] -> [(floor((i1)/32))] }]", permutable: 1, coincident: [ 1, 1, 0 ], child: { mark: "1st level tiling - Points", child: { mark: "Register tiling - Tiles", child: { schedule: "[{ Stmt14[i0, i1, i2] -> [(floor((i0)/2) - 16*floor((i0)/32))] }, { Stmt14[i0, i1, i2] -> [(floor((i2)/2) - 16*floor((i2)/32))] }, { Stmt14[i0, i1, i2] -> [(floor((i1)/2) - 16*floor((i1)/32))] }]", permutable: 1, coincident: [ 1, 1, 0 ], child: { mark: "Register tiling - Points", child: { schedule: "[{ Stmt14[i0, i1, i2] -> [(i0 - 2*floor((i0)/2))] }, { Stmt14[i0, i1, i2] -> [(i2 - 2*floor((i2)/2))] }, { Stmt14[i0, i1, i2] -> [(i1 - 2*floor((i1)/2))] }]", permutable: 1, coincident: [ 1, 1, 0 ], options: "{ unroll[i0] : 0 <= i0 <= 2 }" } } } } } } } } ] } }'
    res = st.parse_schedule_tree(test_5)
    assert res != None
