"""
Declare a http source.
"""
from typing import List, Mapping, Union

import attr
from plumbum import local

from benchbuild import variants
from benchbuild.downloads import base
from benchbuild.utils.cmd import wget, cp, tar


@attr.s
class HTTP(base.BaseSource):
    """
    Fetch the downloadable source via http.
    """
    def version(self, target_dir: str, version: str) -> str:
        prefix = base.target_prefix()
        remotes = normalize_remotes(self.remote)

        url = remotes[version]
        target_name = versioned_target_name(self.local, version)
        cache_path = local.path(prefix) / target_name
        download_single_version(url, cache_path)

        # FIXME: Belongs to environment code.

        target_path = local.path(target_dir) / self.local
        cp('-ar', cache_path, target_path)
        return target_path

    def versions(self) -> List[variants.Variant]:
        remotes = normalize_remotes(self.remote)
        for rev in list(remotes.keys()):
            yield variants.Variant(version=rev, owner=self)


def normalize_remotes(remote: Union[str, Mapping[str, str]]
                      ) -> Mapping[str, str]:
    if not isinstance(remote, Mapping):
        raise TypeError('\'remote\' needs to be a mapping type')
    _remotes = {}
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


def download_required(target_path) -> bool:
    from benchbuild.utils.download import source_required
    return source_required(target_path)
