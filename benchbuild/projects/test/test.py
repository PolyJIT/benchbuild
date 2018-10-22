from benchbuild import project
from benchbuild.utils import compiler
from benchbuild.utils import run
from benchbuild.utils import wrapping


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

        clang = compiler.cxx(self)
        run.run(clang[self.src_file, "-o", self.src_file + ".out"])

    def run_tests(self, runner):
        exp = wrapping.wrap(self.src_file + ".out", self)
        runner(exp)


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

        clang = compiler.cxx(self)
        run.run(clang[self.src_file, "-o", self.src_file + ".out"])

    def run_tests(self, runner):
        exp = wrapping.wrap(self.src_file + ".out", self)
        runner(exp)
