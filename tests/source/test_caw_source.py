import typing as tp

from benchbuild.project import Project
from benchbuild.source import (
    enumerate_revisions,
    Variant,
    SingleVersionFilter,
    FetchableSource,
)


class TestProject(Project):
    """Test project that does nothing."""
    NAME = "test"
    DOMAIN = "test"
    GROUP = "test"
    SOURCE: tp.ClassVar[tp.List[FetchableSource]] = []

    def compile(self):
        pass

    def run_tests(self):
        pass


def test_enumerate_output(make_source, caw_src_0, caw_src_1):
    """
    Test conditional-expansion with cross-product.
    """

    src_primary = make_source([0, 1])
    TestProject.SOURCE = [src_primary, caw_src_0, caw_src_1]

    expected_variants = [
        [Variant(src_primary, "0"),
         Variant(caw_src_0, "v0.1")],
        [Variant(src_primary, "0"),
         Variant(caw_src_0, "v0.2")],
        [Variant(src_primary, "1"),
         Variant(caw_src_1, "v1.1")],
        [Variant(src_primary, "1"),
         Variant(caw_src_1, "v1.2")],
    ]

    revs = enumerate_revisions(TestProject)
    test = [rev.variants for rev in revs]
    assert test == expected_variants


def test_caw_filter(make_source, caw_src_0):
    """
    Test filtering on caw sources.
    """
    src_primary = make_source([0, 1])
    v_filter = SingleVersionFilter(caw_src_0, "v0.2")

    TestProject.SOURCE = [src_primary, v_filter]
    revs = enumerate_revisions(TestProject)

    assert v_filter.is_context_free() is False, \
           "is_context_free needs to be delegated to child."

    expected_variants = [
        [Variant(src_primary, "0"),
         Variant(v_filter, "v0.2")],
        [Variant(src_primary, "1")],
    ]

    test = [rev.variants for rev in revs]
    assert test == expected_variants
