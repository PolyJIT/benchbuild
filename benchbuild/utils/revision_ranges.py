"""
Revision ranges model a sub-graph of the git history by various means and can be
used to modify project behaviour on a per-revision basis.
"""

import abc
import typing as tp
from enum import IntFlag

from plumbum.machines import LocalCommand

from benchbuild.source import Git
from benchbuild.utils.cmd import git as local_git

if tp.TYPE_CHECKING:
    import pygit2


def _get_git_for_path(repo_path: str) -> LocalCommand:
    """
    Enhance the ``local["git"]`` command to use the ``-C`` parameter to run in
    a specific directory.

    Args:
         repo_path: The path of the git repository the returned git command will
                    run in.

    Returns:
        The git command with an added ``-C`` parameter.
    """
    return local_git["-C", repo_path]


def _get_all_revisions_between(c_start: str, c_end: str,
                               git: LocalCommand) -> tp.List[str]:
    """
    Returns a list of all revisions that are both descendants of c_start, and
    ancestors of c_end.
    """
    result = [c_start]
    result.extend(
        git("log", "--pretty=%H", "--ancestry-path",
            f"{c_start}..{c_end}").strip().split()
    )
    return result


class AbstractRevisionRange(abc.ABC):
    """
    Revision ranges represent a set of revisions, i.e., a sub-graph of the
    history of a git repository.
    """

    def __init__(self, comment: tp.Optional[str] = None):
        self.__comment = comment

    @property
    def comment(self) -> tp.Optional[str]:
        """
        A comment associated with this revision range.
        """
        return self.__comment

    @abc.abstractmethod
    def init_cache(self, repo_path: str) -> None:
        """
        Subclasses relying on complex functionality for determining their set
        of revisions can use this method to initialize a cache.

        Args:
            repo_path: The path to the git repository this range is defined for.
        """

    @abc.abstractmethod
    def __iter__(self) -> tp.Iterator[str]:
        """
        Allows iterating over the revisions contained in this revision range in
        no particular order.

        Returns:
            An iterator over the revisions contained in this revision range.
        """


class SingleRevision(AbstractRevisionRange):
    """
    A single revision.

    Args:
        rev_id: The commit hash of the single revision.
        comment: See :func:`AbstractRevisionRange.comment()`.
    """

    def __init__(self, rev_id: str, comment: tp.Optional[str] = None):
        super().__init__(comment)
        self.__id = rev_id

    @property
    def rev_id(self) -> str:
        return self.__id

    def init_cache(self, repo_path: str) -> None:
        pass

    def __iter__(self) -> tp.Iterator[str]:
        return [self.__id].__iter__()

    def __str__(self) -> str:
        return self.rev_id


class RevisionRange(AbstractRevisionRange):
    """
    The range of revisions between two commits `start` and `end`, i.e., all
    revisions that are both descendants of `start`, and ancestors of `end`.

    Args:
        id_start: The commit hash of `start` (exclusive).
        id_end: The commit hash of `end` (inclusive).
        comment: See :func:`AbstractRevisionRange.comment()`.
    """

    def __init__(
        self, id_start: str, id_end: str, comment: tp.Optional[str] = None
    ):
        super().__init__(comment)
        self.__id_start = id_start
        self.__id_end = id_end
        # cache for commit hashes
        self.__revision_list: tp.Optional[tp.List[str]] = None

    @property
    def id_start(self) -> str:
        return self.__id_start

    @property
    def id_end(self) -> str:
        return self.__id_end

    def init_cache(self, repo_path: str) -> None:
        git = _get_git_for_path(repo_path)
        self.__revision_list = _get_all_revisions_between(
            self.__id_start, self.__id_end, git
        )

    def __iter__(self) -> tp.Iterator[str]:
        if self.__revision_list is None:
            raise AssertionError
        return self.__revision_list.__iter__()

    def __str__(self) -> str:
        return f"{self.id_start}:{self.id_end}"


class CommitState(IntFlag):
    BOT = 0
    GOOD = 1
    BAD = 2
    UNKNOWN = GOOD | BAD


def _find_blocked_commits(
    commit: 'pygit2.Commit', good: tp.List['pygit2.Commit'],
    bad: tp.List['pygit2.Commit']
) -> tp.List['pygit2.Commit']:
    """
    Find all commits affected by a bad commit and not yet "fixed" by a
    good commit. This is done by performing a backwards search starting
    at ``commit``.

    Args:
        commit: The head commit.
        good:   Good commits (or fixes).
        bad:    Bad commits (or bugs).

    Returns:
        All transitive parents of commit that have an ancestor from bad
        that is not fixed by some commit from good.
    """
    stack: tp.List['pygit2.Commit'] = [commit]
    blocked: tp.Dict['pygit2.Commit', CommitState] = {}

    while stack:
        current_commit = stack.pop()

        if current_commit in good:
            blocked[current_commit] = CommitState.GOOD
        if current_commit in bad:
            blocked[current_commit] = CommitState.BAD

        # must be deeper in the stack than its parents
        if current_commit not in blocked.keys():
            stack.append(current_commit)

        for parent in current_commit.parents:
            if parent not in blocked.keys():
                stack.append(parent)

        # if all parents are already handled, determine whether
        # the current commit is blocked or not.
        if current_commit not in blocked.keys() and all(
            parent in blocked.keys() for parent in current_commit.parents
        ):
            blocked[current_commit] = CommitState.BOT
            for parent in current_commit.parents:
                if blocked[parent] & CommitState.GOOD:
                    blocked[current_commit] |= CommitState.GOOD
                if blocked[parent] & CommitState.BAD:
                    blocked[current_commit] |= CommitState.BAD

    return [
        commit for commit in blocked
        # for more aggressive blocking use:
        # if blocked[commit] & CommitState.BUGGY
        if blocked[commit] == CommitState.BAD
    ]


class GoodBadSubgraph(AbstractRevisionRange):
    """
    A range of revisions containing all revisions that contain some `bad`
    commit, but no `good` commit, e.g., all revisions that are affected by some
    bug, but that do not contain the fix for the bug.

    Args:
        bad_commits: A list of `bad` commits.
        good_commits: A list of `good` commits.
        comment: See :func:`AbstractRevisionRange.comment()`.
    """

    def __init__(
        self,
        bad_commits: tp.List[str],
        good_commits: tp.List[str],
        comment: tp.Optional[str] = None
    ):
        super().__init__(comment)
        self.__bad_commit_ids = bad_commits
        self.__good_commit_ids = good_commits
        # cache for commit hashes
        self.__revision_list: tp.Optional[tp.List[str]] = None

    def init_cache(self, repo_path: str) -> None:
        import pygit2  # pylint: disable=import-outside-toplevel
        self.__revision_list = []
        repo = pygit2.Repository(repo_path)
        git = _get_git_for_path(repo_path)

        bad_commits = [repo.get(bug_id) for bug_id in self.__bad_commit_ids]
        good_commits = [repo.get(fix_id) for fix_id in self.__good_commit_ids]

        # start search from all branch heads
        heads = git("show-ref", "--heads", "-s").strip().split("\n")
        for head in heads:
            self.__revision_list.extend([
                str(commit.id) for commit in _find_blocked_commits(
                    repo.get(head), good_commits, bad_commits
                )
            ])

    @property
    def good_commits(self) -> tp.List[str]:
        return self.__good_commit_ids

    @property
    def bad_commits(self) -> tp.List[str]:
        return self.__bad_commit_ids

    def __iter__(self) -> tp.Iterator[str]:
        if self.__revision_list is None:
            raise AssertionError
        return self.__revision_list.__iter__()

    def __str__(self) -> str:
        # the separator "\" should resemble a setminus, because we include all
        # commits that have a bad ancestor, but no good one.
        return f"{','.join(self.bad_commits)}\\{','.join(self.good_commits)}"


class block_revisions():  # pylint: disable=invalid-name
    """
    Decorator for git sources for blacklisting/blocking revisions.

    This decorator can be added to :class:`benchbuild.source.git.Git` objects.
    It adds a new static method ``is_blocked_revision`` that checks
    whether a given revision id is marked as blocked.

    Args:
        blocks: A list of :class:`AbstractRevisionRange` s.
    """

    def __init__(self, blocks: tp.List[AbstractRevisionRange]) -> None:
        self.__blocks = blocks

    def __call__(self, git_source: Git) -> Git:

        def is_blocked_revision_impl(
            rev_id: str
        ) -> tp.Tuple[bool, tp.Optional[str]]:
            """
            Checks whether a revision is blocked or not. Also returns the
            reason for the block if available.
            """
            if not hasattr(git_source, "blocked_revisions_initialized"):
                raise AssertionError

            # trigger caching for BlockedRevisionRanges
            if not git_source.blocked_revisions_initialized:
                cache_path = git_source.fetch()
                git_source.blocked_revisions_initialized = True
                for block in self.__blocks:
                    block.init_cache(str(cache_path))

            for b_entry in self.__blocks:
                for b_item in b_entry:
                    if b_item.startswith(rev_id):
                        return True, b_entry.comment
            return False, None

        git_source.blocked_revisions_initialized = False
        git_source.is_blocked_revision = is_blocked_revision_impl
        return git_source
