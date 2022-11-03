import typing as tp

import plumbum as pb

import benchbuild as bb
from benchbuild import project
from benchbuild.environments.domain.declarative import ContainerImage
from benchbuild.source import nosource, Variant, FetchableSource, Revision


class TestSource(FetchableSource):

    _versions: tp.Tuple[Variant, ...]

    def __init__(self, *versions: str):
        super().__init__("test.local", "test.remote")

        self._local = "test.local"
        self._remote = "test.remote"

        versions_w_default = ("default",) + versions

        self._versions = tuple(
            Variant(self, version) for version in versions_w_default
        )

    @property
    def default(self) -> Variant:
        return self._versions[0]

    def version(self, target_dir: str, version: str) -> pb.LocalPath:
        return 'None'

    def versions(self) -> tp.List[Variant]:
        return list(self._versions)

    def fetch(self) -> pb.LocalPath:
        return 'None'


class CAWTestSource(FetchableSource):

    _versions: tp.Dict[Variant, tp.List[Variant]]

    def __init__(
        self,
        *versions: tp.Tuple[str, str],
    ):
        super().__init__("test.caw.local", "test.caw.remote")

        self._local = "test.caw.local"
        self._remote = "test.caw.remote"

        versions_w_default = \
            (("default", "caw_default"),) + versions

        self._versions = {
            Variant(self, lhs): [] for lhs, _ in versions_w_default
        }
        for lhs, rhs in versions_w_default:
            self._versions[Variant(self, lhs)].append(Variant(self, rhs))

    @property
    def default(self) -> Variant:
        """
        Default makes sense in general, but not in this test source.
        """
        for v in self._versions.values():
            if len(v) > 0:
                return v[0]

        raise ValueError("No default version for this context-aware source")

    def version(self, target_dir: str, version: str) -> pb.LocalPath:
        """
        Do not return anything useful for a test here.
        """
        return 'None'

    def fetch(self) -> pb.LocalPath:
        """
        Do not return anything useful for a test here.
        """
        return 'None'

    def versions(self) -> tp.List[Variant]:
        raise ValueError("Context-Aware sources must not use versions()!")

    def is_context_free(self) -> bool:
        return False

    def versions_with_context(self, ctx: Revision) -> tp.Sequence[Variant]:
        if ctx.primary in self._versions:
            return self._versions[ctx.primary]
        return []


class TestProject(project.Project):
    """Test project that does nothing."""
    NAME = "test"
    DOMAIN = "test"
    GROUP = "test"
    SOURCE = [TestSource("1", "2")]

    CONTAINER = ContainerImage().from_('benchbuild:alpine')

    def compile(self):
        with open('test.cpp', 'w', encoding="utf-8") as test_source:
            lines = """
#include <iostream>
int main(int argc, char **argv) {
    std::cout << "Hello (stdout) World" << std::endl;
    std::cerr << "Hello (stderr) World" << std::endl;
    return 0;
}
            """
            test_source.write(lines)

        clang = bb.compiler.cxx(self)
        _clang = bb.watch(clang)
        _clang('test.cpp', "-o", 'test.cpp.out')

    def run_tests(self):
        exp = bb.wrap('test.cpp.out', self)
        _exp = bb.watch(exp)
        _exp()


class TestProjectRuntimeFail(project.Project):
    """Test project that _always_ fails at runtime."""

    NAME = "test-fail"
    DOMAIN = "test"
    GROUP = "test"
    SRC_FILE = "test.cpp"
    SOURCE = [nosource()]
    CONTAINER = ContainerImage().from_('benchbuild:alpine')

    def compile(self):
        with open('test.cpp', 'w') as test_source:
            lines = """
#include <iostream>
int main(int argc, char **argv) {
    std::cout << "Hello (stdout) World" << std::endl;
    std::cerr << "Hello (stderr) World" << std::endl;
    return 1;
}
            """
            test_source.write(lines)

        clang = bb.compiler.cxx(self)
        _clang = bb.watch(clang)
        _clang('test.cpp', "-o", 'test.cpp.out')

    def run_tests(self):
        exp = bb.wrap('test.cpp.ou', self)
        _exp = bb.watch(exp)
        _exp()


class CAWTestProject(project.Project):
    """A context-aware test project that does nothing."""

    NAME = "test-caw"
    DOMAIN = "test"
    GROUP = "test"
    SOURCE = [
        TestSource("1", "2", "3"),
        CAWTestSource(("1", "caw_0"), ("3", "caw_0"))
    ]

    CONTAINER = ContainerImage().from_('benchbuild:alpine')

    def compile(self):
        with open('test.cpp', 'w', encoding="utf-8") as test_source:
            lines = """
#include <iostream>
int main(int argc, char **argv) {
    std::cout << "Hello (stdout) World" << std::endl;
    std::cerr << "Hello (stderr) World" << std::endl;
    return 0;
}
            """
            test_source.write(lines)

        clang = bb.compiler.cxx(self)
        _clang = bb.watch(clang)
        _clang('test.cpp', "-o", 'test.cpp.out')

    def run_tests(self):
        exp = bb.wrap('test.cpp.out', self)
        _exp = bb.watch(exp)
        _exp()
