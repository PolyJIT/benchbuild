"""
Environment API.

TODO
"""
import attr

@attr.s
class Environment:
    def cmd(self, *args):
        """
        Fetch a command mapped inside the environment.

        Depending on the environment, it might be necessary to wrap all command
        requests in a environment-specific command to be able to access it properly.

        Examples: uchroot, podman, chroot/bash
        """
        pass

    def setup(self, *args):
        """
        Setup the environment.

        Run the given build strategy on this environment.

        Args:
            TODO
        """
        pass


    def wrap(self, wrapper_func, path):
        """
        Wrap a given path with a wrapper inside the environment.

        Apply the wrapper to the binary inside the environment.

        Args:
            wrapper_func: TODO
            path: TODO

        Returns:
            TODO
        """
        pass

    def target(self):
        """
        Access the 'target' machine behind this environment.

        This corresponds to a plumbum machine object, e.g., 'local', if called
        from the local host os.

        Args:

        """
        pass

def compatible(env, project_or_experiment):
    pass
