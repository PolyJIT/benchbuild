"""
# Downloading helper functions for benchbuild.

The helpers defined in this module provide access to some common Downloading
methods for the source code of benchbuild projects.
All downloads will be cached in BB_TMP_DIR and locked down with a hash that
is generated after the first download. If the hash matches the file/folder
found in BB_TMP_DIR, nothing will be downloaded at all.

Supported methods:
        Copy, CopyNoFail, Wget, Git, Svn, Rsync
"""
import logging
import os

from benchbuild.settings import CFG

LOG = logging.getLogger(__name__)


def get_hash_of_dirs(directory):
    """
    Recursively hash the contents of the given directory.

    Args:
        directory (str): The root directory we want to hash.

    Returns:
        A hash of all the contents in the directory.
    """
    import hashlib
    sha = hashlib.sha512()
    if not os.path.exists(directory):
        return -1

    for root, _, files in os.walk(directory):
        for names in files:
            filepath = os.path.join(root, names)
            if os.path.exists(filepath):
                with open(filepath, 'rb') as next_file:
                    for line in next_file:
                        sha.update(line)
    return sha.hexdigest()


def source_required(src_file, src_root):
    """
    Check, if a download is required.

    Args:
        src_file: The filename to check for.
        src_root: The path we find the file in.

    Returns:
        True, if we need to download something, False otherwise.
    """
    # Check if we need to do something
    src_dir = os.path.join(src_root, src_file)
    hash_file = os.path.join(src_root, src_file + ".hash")

    required = True
    src_exists = os.path.exists(src_dir)
    hash_exists = os.path.exists(hash_file)
    if src_exists and hash_exists:
        new_hash = get_hash_of_dirs(src_dir)
        with open(hash_file, 'r') as h_file:
            old_hash = h_file.readline()
        required = not new_hash == old_hash
        if required:
            from benchbuild.utils.cmd import rm
            rm("-r", src_dir)
            rm(hash_file)
    if required:
        LOG.info("Source required for: %s in %s", src_file, src_dir)
        LOG.info("Reason: src-exists: %s hash-exists: %s", src_exists,
                 hash_exists)
    return required


def update_hash(src, root):
    """
    Update the hash for the given file.

    Args:
        src: The file name.
        root: The path of the given file.
    """
    hash_file = os.path.join(root, src + ".hash")
    new_hash = 0
    with open(hash_file, 'w') as h_file:
        src_path = os.path.join(root, src)
        new_hash = get_hash_of_dirs(src_path)
        h_file.write(str(new_hash))
    return new_hash


def Copy(From, To):
    """
    Small copy wrapper.

    Args:
        From (str): Path to the SOURCE.
        To (str): Path to the TARGET.
    """
    from benchbuild.utils.cmd import cp
    cp("-ar", "--reflink=auto", From, To)


def CopyNoFail(src, root=None):
    """
    Just copy fName into the current working directory, if it exists.

    No action is executed, if fName does not exist. No Hash is checked.

    Args:
        src: The filename we want to copy to '.'.
        root: The optional source dir we should pull fName from. Defaults
            to benchbuild.settings.CFG["tmpdir"].

    Returns:
        True, if we copied something.
    """
    if root is None:
        root = str(CFG["tmp_dir"])
    src_url = os.path.join(root, src)

    if os.path.exists(src_url):
        Copy(src_url, '.')
        return True
    return False


def Wget(src_url, tgt_name, tgt_root=None):
    """
    Download url, if required.

    Args:
        src_url (str): Our SOURCE url.
        tgt_name (str): The filename we want to have on disk.
        tgt_root (str): The TARGET directory for the download.
            Defaults to ``CFG["tmpdir"]``.
    """
    if tgt_root is None:
        tgt_root = str(CFG["tmp_dir"])

    from benchbuild.utils.cmd import wget

    src_path = os.path.join(tgt_root, tgt_name)
    if not source_required(tgt_name, tgt_root):
        Copy(src_path, ".")
        return

    wget(src_url, "-O", src_path)
    update_hash(tgt_name, tgt_root)
    Copy(src_path, ".")


def Git(repository, directory, rev=None, prefix=None, shallow_clone=True):
    """
    Get a clone of the given repo

    Args:
        repository (str): Git URL of the SOURCE repo.
        directory (str): Name of the repo folder on disk.
        tgt_root (str): TARGET folder for the git repo.
            Defaults to ``CFG["tmpdir"]``
        shallow_clone (bool): Only clone the repository shallow
            Defaults to true
    """
    repository_loc = str(prefix)
    if prefix is None:
        repository_loc = str(CFG["tmp_dir"])

    from benchbuild.utils.cmd import git

    src_dir = os.path.join(repository_loc, directory)
    if not source_required(directory, repository_loc):
        Copy(src_dir, ".")
        return

    extra_param = []
    if shallow_clone:
        extra_param.append("--depth")
        extra_param.append("1")

    git("clone", extra_param, repository, src_dir)    if not rev:
    if rev:
        git("checkout", rev)

    update_hash(directory, repository_loc)
    Copy(src_dir, ".")
    return repository_loc


def with_git(repo,
             target_dir=None,
             limit=None,
             refspec="HEAD",
             clone=True,
             rev_list_args=[]):
    def git_decorator(cls):
        from benchbuild.utils.cmd import git

        @staticmethod
        def versions_impl():
            from plumbum import local

            directory = cls.SRC_FILE if target_dir is None else target_dir
            repo_prefix = os.path.join(str(CFG["tmp_dir"]))
            repo_loc = os.path.join(repo_prefix, directory)
            if source_required(directory, repo_prefix):
                if not clone:
                    return []
                git("clone", repo, repo_loc)
                update_hash(directory, repo_prefix)

            with local.cwd(repo_loc):
                rev_list = git("rev-list", "--abbrev-commit", refspec,
                               *rev_list_args).strip().split('\n')
                latest = git("rev-parse", "--short=8",
                             refspec).strip().split('\n')
                cls.VERSION = latest[0]
                return rev_list[:limit] if limit else rev_list

        cls.versions = versions_impl
        cls.repository = repo
        return cls

    return git_decorator


def Svn(url, fname, to=None):
    """
    Checkout the SVN repo.

    Args:
        url (str): The SVN SOURCE repo.
        fname (str): The name of the repo on disk.
        to (str): The name of the TARGET folder on disk.
            Defaults to ``CFG["tmpdir"]``
    """
    if to is None:
        to = CFG["tmp_dir"].value()

    src_dir = os.path.join(to, fname)
    if not source_required(fname, to):
        Copy(src_dir, ".")
        return

    from benchbuild.utils.cmd import svn
    svn("co", url, src_dir)
    update_hash(fname, to)
    Copy(src_dir, ".")


def Rsync(url, tgt_name, tgt_root=None):
    """
    RSync a folder.

    Args:
        url (str): The url of the SOURCE location.
        fname (str): The name of the TARGET.
        to (str): Path of the target location.
            Defaults to ``CFG["tmpdir"]``.
    """
    if tgt_root is None:
        tgt_root = CFG["tmp_dir"].value()

    from benchbuild.utils.cmd import rsync

    src_dir = os.path.join(tgt_root, tgt_name)
    if not source_required(tgt_name, tgt_root):
        Copy(src_dir, ".")
        return

    rsync("-a", url, src_dir)
    update_hash(tgt_name, tgt_root)
    Copy(src_dir, ".")
