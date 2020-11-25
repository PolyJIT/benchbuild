"""
Declare a http source.
"""
import typing as tp

import plumbum as pb

from benchbuild.source import base
from benchbuild.utils.cmd import cp, wget

VarRemotes = tp.Union[str, tp.Dict[str, str]]
Remotes = tp.Dict[str, str]


class HTTP(base.FetchableSource):
    """
    Fetch the downloadable source via http.
    """

    @property
    def default(self) -> base.Variant:
        return self.versions()[0]

    def version(self, target_dir: str, version: str) -> pb.LocalPath:
        prefix = base.target_prefix()
        remotes = normalize_remotes(self.remote)

        url = remotes[version]
        target_name = versioned_target_name(self.local, version)
        cache_path = pb.local.path(prefix) / target_name
        download_single_version(url, cache_path)

        # FIXME: Belongs to environment code.

        target_path = pb.local.path(target_dir) / self.local
        cp('-ar', cache_path, target_path)
        return target_path

    def versions(self) -> tp.List[base.Variant]:
        remotes = normalize_remotes(self.remote)
        return [base.Variant(version=rev, owner=self) for rev in remotes]


def normalize_remotes(remote: VarRemotes) -> Remotes:
    if isinstance(remote, str):
        raise TypeError('\'remote\' needs to be a mapping type')

    # FIXME: What the hell?
    _remotes: Remotes = {}
    _remotes.update(remote)
    return _remotes


def versioned_target_name(target_name: str, version: str) -> str:
    return "{}-{}".format(version, target_name)


def download_single_version(url: str, target_path: str) -> str:
    if not download_required(target_path):
        return target_path

    wget(url, '-O', target_path)
    from benchbuild.utils.download import update_hash
    update_hash(target_path)
    return target_path


def download_required(target_path: str) -> bool:
    from benchbuild.utils.download import source_required
    return source_required(target_path)
