"""
Declare a git source.
"""
import os
import typing as tp
import logging
from pathlib import Path

import plumbum as pb
from plumbum.commands.base import BoundCommand

from benchbuild.utils.cmd import git, ln, mkdir

from . import base

LOG = logging.getLogger(__name__)

VarRemotes = tp.Union[str, tp.Dict[str, str]]
Remotes = tp.Dict[str, str]


class Git(base.FetchableSource):
    """
    Fetch the downloadable source via git.
    """

    def __init__(
        self,
        remote: str,
        local: str,
        clone: bool = True,
        limit: tp.Optional[int] = 10,
        refspec: str = 'HEAD',
        shallow: bool = True,
        version_filter: tp.Callable[[str], bool] = lambda version: True
    ):
        super().__init__(local, remote)

        self.clone = clone
        self.limit = limit
        self.refspec = refspec
        self.shallow = shallow
        self.version_filter = version_filter

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
        clone = maybe_shallow(
            git['clone', '--recurse-submodules'], self.shallow
        )
        fetch = git['fetch', '--update-shallow', '--all']
        flat_local = self.local.replace(os.sep, '-')
        cache_path = pb.local.path(prefix) / flat_local

        if clone_needed(self.remote, cache_path):
            clone(self.remote, cache_path)
        else:
            with pb.local.cwd(cache_path):
                fetch()

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
        active_loc = pb.local.path(target_dir) / self.local
        tgt_subdir = f'{self.local}-{version}'
        tgt_loc = pb.local.path(target_dir) / tgt_subdir

        clone = git['clone']
        pull = git['pull']
        rev_parse = git['rev-parse']
        checkout = git['checkout']

        with pb.local.cwd(src_loc):
            is_shallow = rev_parse('--is-shallow-repository').strip()
            if is_shallow == 'true':
                pull('--unshallow')

        if Path(tgt_loc).exists():
            LOG.info(
                'Found target location %s. Going to skip creation and '
                'repository cloning.', str(tgt_loc)
            )
        else:
            mkdir('-p', tgt_loc)
            with pb.local.cwd(tgt_loc):
                clone(
                    '--dissociate', '--recurse-submodules', '--reference',
                    src_loc, self.remote, '.'
                )
                checkout('--detach', version)

        ln('-nsf', tgt_subdir, active_loc)
        return tgt_loc

    def versions(self) -> tp.List[base.Variant]:
        cache_path = self.fetch()
        git_rev_list = git['rev-list', '--abbrev-commit', '--abbrev=10']

        rev_list: tp.List[str] = []
        with pb.local.cwd(cache_path):
            rev_list = list(git_rev_list(self.refspec).strip().split('\n'))

        rev_list = list(filter(self.version_filter, rev_list))
        rev_list = rev_list[:self.limit] if self.limit else rev_list
        revs = [base.Variant(version=rev, owner=self) for rev in rev_list]
        return revs


class GitSubmodule(Git):

    @property
    def is_expandable(self) -> bool:
        """Submodules will not participate in version expansion."""
        return False


def maybe_shallow(cmd: BoundCommand, enable: bool) -> BoundCommand:
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
