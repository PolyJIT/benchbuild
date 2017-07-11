import benchbuild.project as prj
import benchbuild.utils.compiler as compiler
import benchbuild.utils.run as run
import benchbuild.utils.wrapping as wrapping

class TestProject(prj.Project):
    """Test project that does nothing."""
    NAME = "test"
    DOMAIN = "test"
    GROUP = "test"
    VERSION = "1.0"
    SRC_FILE = "test.cpp"

    def prepare(self):
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

    def configure(self):
        pass

    def build(self):
        clang = compiler.lt_clang_cxx(self.cflags, self.ldflags,
                                      self.compiler_extension)
        run.run(clang[self.src_file, "-o", self.src_file + ".out"])

    def run_tests(self, experiment, run):
        exp = wrapping.wrap(self.src_file + ".out", experiment)
        run(exp)

class TestProjectRuntimeFail(prj.Project):
    """Test project that _always_ fails at runtime."""

    NAME = "test-fail"
    DOMAIN = "test"
    GROUP = "test"
    VERSION = "1.0"
    SRC_FILE = "test.cpp"

    def prepare(self):
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

    def configure(self):
        pass

    def build(self):
        clang = compiler.lt_clang_cxx(self.cflags, self.ldflags,
                                      self.compiler_extension)
        run.run(clang[self.src_file, "-o", self.src_file + ".out"])

    def run_tests(self, experiment, run):
        exp = wrapping.wrap(self.src_file + ".out", experiment)
        run(exp)