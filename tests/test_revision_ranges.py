"""Test the revision_ranges module."""

from pathlib import Path
import unittest
from unittest import mock

import benchbuild.utils.revision_ranges as ranges


class TestRevisionRanges(unittest.TestCase):
    """Test the revision range classes."""

    def test_single_revision(self):
        revision_range = ranges.SingleRevision("1234abc")
        self.assertIn("1234abc", revision_range)

    @mock.patch("benchbuild.utils.revision_ranges._get_all_revisions_between")
    def test_revision_range(self, get_all_revs_between_mock):
        commits = ["1111112", "1111113", "1111114"]
        get_all_revs_between_mock.return_value = commits

        revision_range = ranges.RevisionRange("1111111", "1111114")
        revision_range.init_cache(Path("not/relevant/for/test"))
        for commit in commits:
            self.assertIn(commit, revision_range)

    @mock.patch("pygit2.Commit")
    @mock.patch("pygit2.Commit")
    @mock.patch("pygit2.Commit")
    @mock.patch("pygit2.Commit")
    @mock.patch("pygit2.Commit")
    @mock.patch("pygit2.Commit")
    @mock.patch("pygit2.Commit")
    def test_find_blocked_commits(
        self,
        commit_head,
        commit_good,
        commit_bad,
        commit_r,
        commit_s,
        commit_x,
        commit_y,
    ):
        """
        X---R---G---HEAD
        \\ /   /   /
          B---S   Y

        GoodBadSubgraph([A], [B]) = [R, S, B] (order unspecified)
        """
        commit_head.parents = [commit_good, commit_y]
        commit_good.parents = [commit_r, commit_s]
        commit_bad.parents = [commit_x]
        commit_r.parents = [commit_x, commit_bad]
        commit_s.parents = [commit_bad]
        commit_x.parents = []
        commit_y.parents = []

        result = ranges._find_blocked_commits(commit_head, [commit_good], [commit_bad])
        self.assertIn(commit_r, result)
        self.assertIn(commit_s, result)
        self.assertIn(commit_bad, result)
