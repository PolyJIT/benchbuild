"""
Downloading helper functions for benchbuild.

The helpers defined in this module provide access to some common Downloading
methods for the source code of benchbuild projects.
All downloads will be cached in BB_TMP_DIR and locked down with a hash that
is generated after the first download. If the hash matches the file/folder
found in BB_TMP_DIR, nothing will be downloaded at all.

Supported methods:
        Copy, CopyNoFail, Wget, Git, Svn, Rsync
"""
from benchbuild.settings import CFG


def get_hash_of_dirs(directory):
    """
    Recursively hash the contents of the given directory.

    Args:
        directory (str): The root directory we want to hash.

    Returns:
        A hash of all the contents in the directory.
    """
    import hashlib
    import os
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
    from os import path

    # Check if we need to do something
    src_dir = path.join(src_root, src_file)
    hash_file = path.join(src_root, src_file + ".hash")

    required = True
    if path.exists(src_dir) and path.exists(hash_file):
        new_hash = get_hash_of_dirs(src_dir)
        with open(hash_file, 'r') as h_file:
            old_hash = h_file.readline()
        required = not new_hash == old_hash
        if required:
            from benchbuild.utils.cmd import rm
            rm("-r", src_dir)
            rm(hash_file)
    return required


def update_hash(src, root):
    """
    Update the hash for the given file.

    Args:
        src: The file name.
        root: The path of the given file.
    """
    from os import path

    hash_file = path.join(root, src + ".hash")
    new_hash = 0
    with open(hash_file, 'w') as h_file:
        src_path = path.join(root, src)
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
    from os import path
    if root is None:
        root = CFG["tmp_dir"].value()
    src_url = path.join(root, src)

    if path.exists(src_url):
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
        tgt_root = CFG["tmp_dir"].value()

    from os import path
    from benchbuild.utils.cmd import wget

    src_path = path.join(tgt_root, tgt_name)
    if not source_required(tgt_name, tgt_root):
        Copy(src_path, ".")
        return

    wget(src_url, "-O", src_path)
    update_hash(tgt_name, tgt_root)
    Copy(src_path, ".")


def Git(src_url, tgt_name, tgt_root=None):
    """
    Get a shallow clone of the given repo

    Args:
        src_url (str): Git URL of the SOURCE repo.
        tgt_name (str): Name of the repo folder on disk.
        tgt_root (str): TARGET folder for the git repo.
            Defaults to ``CFG["tmpdir"]``
    """
    if tgt_root is None:
        tgt_root = CFG["tmp_dir"].value()

    from os import path
    from benchbuild.utils.cmd import git

    src_dir = path.join(tgt_root, tgt_name)
    if not source_required(tgt_name, tgt_root):
        Copy(src_dir, ".")
        return

    git("clone", "--depth", "1", src_url, src_dir)
    update_hash(tgt_name, tgt_root)
    Copy(src_dir, ".")


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

    from os import path

    src_dir = path.join(to, fname)
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

    from os import path
    from benchbuild.utils.cmd import rsync

    src_dir = path.join(tgt_root, tgt_name)
    if not source_required(tgt_name, tgt_root):
        Copy(src_dir, ".")
        return

    rsync("-a", url, src_dir)
    update_hash(tgt_name, tgt_root)
    Copy(src_dir, ".")
