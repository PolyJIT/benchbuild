from benchbuild.projects.test.test import TestProject
from benchbuild.source import (
    FetchableSource,
    ContextAwareSource,
    enumerate,
    Variant,
)


def test_fetchablesource_protocols():
    assert issubclass(FetchableSource, ContextAwareSource)


def test_enumerate_output(make_source, caw_src_0, caw_src_1):
    """
    Test conditional-expansion with cross-product.
    """
    prj = TestProject()
    src_primary = make_source([0, 1])

    expected_variants = [
        [Variant(src_primary, "0"),
         Variant(caw_src_0, "v0.1")],
        [Variant(src_primary, "0"),
         Variant(caw_src_0, "v0.2")],
        [Variant(src_primary, "1"),
         Variant(caw_src_0, "v1.2")],
        [Variant(src_primary, "1"),
         Variant(caw_src_0, "v1.2")],
    ]

    revs = enumerate(prj, src_primary, caw_src_0, caw_src_1)
    assert [rev.variants for rev in revs] == expected_variants
