import typing as tp

import plumbum as pb
import pytest

from benchbuild.source import Variant, Revision, FetchableSource


class VersionSource(FetchableSource):
    known_versions: tp.List[str]

    def __init__(
        self,
        local: str,
        remote: tp.Union[str, tp.Dict[str, str]],
        known_versions: tp.List[str],
    ):
        super().__init__(local, remote)

        self.known_versions = known_versions

    def fetch(self) -> pb.LocalPath:
        return NotImplementedError()

    @property
    def default(self) -> Variant:
        return Variant(owner=self, version="1")

    def version(self, target_dir: str, version: str) -> pb.LocalPath:
        return "."

    def versions(self) -> tp.List[Variant]:
        return [Variant(self, str(v)) for v in self.known_versions]


@pytest.fixture
def make_source():
    """
    Make a basic context-free source generator.

    The generator allows to set the returned versions.
    """

    def _make_version_source(versions: tp.List[int]):
        str_versions = [str(v) for v in versions]
        return VersionSource("ls", "rs", str_versions)

    return _make_version_source


class CAWSource(FetchableSource):
    """
    Base for context aware test sources
    """

    def version(self, target_dir: str, version: str) -> pb.LocalPath:
        raise NotImplementedError()

    def versions(self) -> tp.List[Variant]:
        raise NotImplementedError()

    def fetch(self) -> pb.LocalPath:
        return NotImplementedError()

    @property
    def default(self) -> Variant:
        raise NotImplementedError()

    @property
    def is_expandable(self) -> bool:
        return True

    def is_context_free(self) -> bool:
        return False


class Config0(CAWSource):
    """
    Context-sensitive source.

    This returns 2 variants, only if our primary version is '0'.
    """

    def versions_with_context(self, ctx: Revision) -> tp.Sequence[Variant]:
        if ctx.primary.version == "0":
            ret = [Variant(self, "v0.1"), Variant(self, "v0.2")]
            return ret
        return []


class Config1(CAWSource):
    """
    Context-sensitive source.

    This returns 2 variants, only if our primary version is '1'.
    """

    def versions_with_context(self, ctx: Revision) -> tp.Sequence[Variant]:
        if ctx.primary.version == "1":
            ret = [Variant(self, "v1.1"), Variant(self, "v1.2")]
            return ret
        return []


@pytest.fixture
def caw_src_0() -> FetchableSource:
    return Config0(local="local", remote="remote")


@pytest.fixture
def caw_src_1() -> FetchableSource:
    return Config1(local="local", remote="remote")
