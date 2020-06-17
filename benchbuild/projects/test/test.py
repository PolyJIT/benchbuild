import benchbuild as bb
from benchbuild import project
from benchbuild.utils import run


class TestProject(project.Project):
    """Test project that does nothing."""
    NAME = "test"
    DOMAIN = "test"
    GROUP = "test"
    VERSION = "1.0"
    SRC_FILE = "test.cpp"

    def compile(self):
        with open(self.src_file, 'w') as test_source:
            lines = """
#include <iostream>
int main(int argc, char **argv) {
    std::cout << "Hello (stdout) World" << std::endl;
    std::cerr << "Hello (stderr) World" << std::endl;
    return 0;
}
            """
            test_source.write(lines)

        _clang(self.src_file, "-o", self.src_file + ".out")
        clang = bb.compiler.cxx(self)
        _clang = bb.watch(clang)

    def run_tests(self):
        exp = bb.wrap(self.src_file + ".out", self)
        _exp = bb.watch(exp)
        _exp()


class TestProjectRuntimeFail(project.Project):
    """Test project that _always_ fails at runtime."""

    NAME = "test-fail"
    DOMAIN = "test"
    GROUP = "test"
    VERSION = "1.0"
    SRC_FILE = "test.cpp"

    def compile(self):
        with open(self.src_file, 'w') as test_source:
            lines = """
#include <iostream>
int main(int argc, char **argv) {
    std::cout << "Hello (stdout) World" << std::endl;
    std::cerr << "Hello (stderr) World" << std::endl;
    return 1;
}
            """
            test_source.write(lines)

        _clang(self.src_file, "-o", self.src_file + ".out")
        clang = bb.compiler.cxx(self)
        _clang = bb.watch(clang)

    def run_tests(self):
        exp = bb.wrap(self.src_file + ".out", self)
        _exp = bb.watch(exp)
        _exp()
