"""
Declare a http source.
"""
import typing as tp

import plumbum as pb

from benchbuild.source import base
from benchbuild.utils.cmd import cp, ln, wget, tar, mkdir, mv

VarRemotes = tp.Union[str, tp.Dict[str, str]]
Remotes = tp.Dict[str, str]


class HTTP(base.FetchableSource):
    """
    Fetch the downloadable source via http.
    """

    @property
    def default(self) -> base.Variant:
        return self.versions()[0]

    def fetch(self) -> pb.LocalPath:
        """
        Fetch via http using default version string.
        """
        return self.fetch_version(self.default.version)

    def fetch_version(self, version: str) -> pb.LocalPath:
        """
        Fetch via http using given version string.

        Args:
            version: the version string to pull via http.

        Returns:
            local path to fetched version.
        """
        prefix = base.target_prefix()
        remotes = normalize_remotes(self.remote)

        url = remotes[version]
        target_name = versioned_target_name(self.local, version)
        cache_path = pb.local.path(prefix) / target_name
        download_single_version(url, cache_path)

        return cache_path

    def version(self, target_dir: str, version: str) -> pb.LocalPath:
        target_name = versioned_target_name(self.local, version)
        cache_path = self.fetch_version(version)

        target_path = pb.local.path(target_dir) / target_name
        active_loc = pb.local.path(target_dir) / self.local

        cp('-ar', cache_path, target_path)
        ln('-sf', target_name, active_loc)

        return target_path

    def versions(self) -> tp.List[base.Variant]:
        remotes = normalize_remotes(self.remote)
        return [base.Variant(version=rev, owner=self) for rev in remotes]


class HTTPUntar(HTTP):
    """
    Fetch and download source via http and auto-unpack using GNU tar
    """

    def version(self, target_dir: str, version: str) -> pb.LocalPath:
        """
        Setup the given version of this HTTPUntar source.

        This will fetch the given version from the remote source and unpack the
        archive into the build directory using tar.

        The location matches the behavior of other sources. However, you need
        to consider that benchbuild will return a directory instead of a file path.

        When using workloads, you can refer to a directory with the SourceRootRenderer using
        ``benchbuild.command.source_root``.

        Example:
            You specify a remote version 1.0 of an archive compression.tar.gz and
            a local name of "compression.tar.gz".
            The build directory will look as follows:

            <builddir>/1.0-compression.dir/
            <builddir>/1.0-compression.tar.gz
            <builddir>/compression.tar.gz -> ./1.0-compression.tar.dir

            The content of the archive is found in the directory compression.tar.gz.
            Your workloads need to make sure to reference this directory (e.g. using tokens),
            e.g., ``source_root("compression.tar.gz")``
        """
        archive_path = super().version(target_dir, version)

        target_name = str(pb.local.path(archive_path).with_suffix(".dir"))
        target_path = pb.local.path(target_dir) / target_name
        active_loc = pb.local.path(target_dir) / self.local

        mkdir(target_path)
        tar("-x", "-C", target_path, "-f", archive_path)

        ln('-sf', target_path, active_loc)

        return target_path


class HTTPMultiple(HTTP):
    """
    Fetch and download multiple files via HTTP.
    """

    def __init__(
        self,
        local: str,
        remote: tp.Union[str, tp.Dict[str, str]],
        files: tp.List[str]
    ):
        super().__init__(local, remote)
        self._files = files

    def fetch_version(self, version: str) -> pb.LocalPath:
        prefix = base.target_prefix()
        remotes = normalize_remotes(self.remote)

        url = remotes[version]
        target_name = versioned_target_name(self.local, version)

        cache_path = pb.local.path(prefix) / target_name
        mkdir('-p', cache_path)

        for file in self._files:
            download_single_version(f'{url}/{file}', cache_path / file)

        return cache_path


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
