"""
Declare a git source.
"""
import typing as tp

import attr
import plumbum as pb
from plumbum import local

from benchbuild.utils.cmd import git, mkdir
from benchbuild.utils.path import flocked

from . import base

Command = pb.commands.base.BaseCommand
VarRemotes = tp.Union[str, tp.Dict[str, str]]
Remotes = tp.Dict[str, str]


@attr.s
class Git(base.BaseSource):
    """
    Fetch the downloadable source via git.
    """

    clone: bool = attr.ib(default=True)
    limit: tp.Optional[int] = attr.ib(default=10)
    refspec: str = attr.ib(default='HEAD')
    shallow: bool = attr.ib(default=True)
    version_filter: tp.Callable[[str],
                                bool] = attr.ib(default=lambda version: True)

    @property
    def default(self) -> base.Variant:
        """
        Return current HEAD as default version for this Git project.
        """
        return self.versions()[0]

    def fetch(self) -> pb.LocalPath:
        """
        Clone the repository, if needed.

        This will create a git clone inside the global cache directory.

        Args:
            version (Optional[str], optional): [description]. Defaults to None.

        Returns:
            str: [description]
        """
        prefix = base.target_prefix()
        clone = maybe_shallow(git['clone'], self.shallow)
        cache_path = local.path(prefix) / self.local

        if clone_needed(self.remote, cache_path):
            clone(self.remote, cache_path)
        return cache_path

    def version(self, target_dir: str, version: str = 'HEAD') -> pb.LocalPath:
        """
        Create a new git worktree pointing to the requested version.

        Args:
            target_dir (str):
                The filesystem path where the new worktree should live.
            version (str):
                The desired version the new worktree needs to point to.
                Defaults to 'HEAD'.

        Returns:
            str: [description]
        """
        src_loc = self.fetch()
        tgt_loc = local.path(target_dir) / self.local
        lock_file = local.path(target_dir) / self.local + '.lock'

        worktree = git['worktree']
        with local.cwd(src_loc):
            mkdir('-p', tgt_loc)
            with flocked(lock_file):
                worktree('prune')
                worktree('add', '--detach', tgt_loc, version)
        return tgt_loc

    def versions(self) -> tp.List[base.Variant]:
        cache_path = self.fetch()
        git_rev_list = git['rev-list', '--abbrev-commit', '--abbrev=10']

        rev_list: tp.List[str] = []
        with local.cwd(cache_path):
            rev_list = list(git_rev_list(self.refspec).strip().split('\n'))

        rev_list = list(filter(self.version_filter, rev_list))
        rev_list = rev_list[:self.limit] if self.limit else rev_list
        revs = [base.Variant(version=rev, owner=self) for rev in rev_list]
        return revs


def maybe_shallow(cmd: Command, enable: bool) -> Command:
    """
    Conditionally add the shallow clone to the given git command.

    Args:
        cmd (Any):
            A git clone command (shallow doesn't make sense anywhere else.
        shallow (bool):
            Should we add the shallow options?

    Returns:
        Any: A new git clone command, with shallow clone enabled, if selected.
    """
    if enable:
        return cmd['--depth', '1']
    return cmd


def clone_needed(repository: VarRemotes, repo_loc: str) -> bool:
    from benchbuild.utils.download import __clone_needed__

    if not isinstance(repository, str):
        raise TypeError('\'remote\' needs to be a git repo string')

    return __clone_needed__(repository, repo_loc)
