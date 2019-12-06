from benchbuild import project
from benchbuild.utils import compiler, run, wrapping


class TestProject(project.Project):
    """Test project that does nothing."""
    NAME = "test"
    DOMAIN = "test"
    GROUP = "test"

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

        clang = compiler.cxx(self)
        clang = run.watch(clang)
        clang('test.cpp', "-o", 'test.cpp.out')

    def run_tests(self):
        exp = wrapping.wrap('test.cpp.out', self)
        exp = run.watch(exp)
        exp()


class TestProjectRuntimeFail(project.Project):
    """Test project that _always_ fails at runtime."""

    NAME = "test-fail"
    DOMAIN = "test"
    GROUP = "test"
    SRC_FILE = "test.cpp"

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

        clang = compiler.cxx(self)
        clang = run.watch(clang)
        clang('test.cpp', "-o", 'test.cpp.out')

    def run_tests(self):
        exp = wrapping.wrap('test.cpp.ou', self)
        exp = run.watch(exp)
        exp()
