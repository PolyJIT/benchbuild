import benchbuild as bb
from benchbuild import project
from benchbuild.environments.domain.declarative import ContainerImage
from benchbuild.source import nosource


class TestProject(project.Project):
    """Test project that does nothing."""
    NAME = "test"
    DOMAIN = "test"
    GROUP = "test"
    SOURCE = [nosource()]
    CONTAINER = ContainerImage().from_('benchbuild:alpine')

    def compile(self):
        with open('test.cpp', 'w') as test_source:
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
