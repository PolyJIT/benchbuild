#!/usr/bin/env python
from pprof.settings import config


def GetHashofDirs(directory):
    import hashlib
    import os
    SHAhash = hashlib.sha512()
    if not os.path.exists(directory):
        return -1

    try:
        for root, dirs, files in os.walk(directory):
            for names in files:
                filepath = os.path.join(root, names)
                try:
                    f1 = open(filepath, 'rb')
                except:
                    # You can't open the file for some reason
                    f1.close()
                    continue

                while 1:
                    # Read file in as little chunks
                    buf = f1.read(4096)
                    if not buf:
                        break
                    SHAhash.update(hashlib.sha512(buf).hexdigest())
            f1.close()
    except:
        import traceback
        # Print the stack traceback
        traceback.print_exc()
        return -2
    return SHAhash.hexdigest()


def source_required(fname, to):
    """
    Check, if a download is required.

    :fname: TODO
    :to: TODO
    :returns: TODO

    """
    from os import path

    # Check if we need to do something
    src_dir = path.join(to, fname)
    hash_file = path.join(to, fname + ".hash")

    required = True
    if path.exists(src_dir) and path.exists(hash_file):
        new_hash = GetHashofDirs(src_dir)
        with open(hash_file, 'r') as hf:
            old_hash = hf.readline()
        required = not new_hash == old_hash
        if required:
            from plumbum.cmd import rm
            rm("-r", src_dir)
            rm(hash_file)
    return required


def update_hash(fname, to):
    from os import path

    hash_file = path.join(to, fname + ".hash")
    with open(hash_file, 'w') as hf:
        src_path = path.join(to, fname)
        new_hash = GetHashofDirs(src_path)
        hf.write(new_hash)


def Copy(From, To):
    """
    Small copy wrapper.

    :From: TODO
    :To: TODO

    """
    from plumbum.cmd import cp
    cp("-ar", "--reflink=auto", From, To)


def CopyNoFail(fName, srcDir=None):
    """
    Just copy :fname from the into the current working directory, if it exists.

    No action is executed, if :fName does not exist. No Hash is checked.

    Args:
        fName: The filename we want to copy to '.'.
        srcDir: The optional source dir we should pull fName from. Defaults
            to pprof.settings.config["tmpdir"].
    Returns:
        True, if we copied something.
    """
    from os import path
    if srcDir is None:
        srcDir = config["tmpdir"]
    src_url = path.join(srcDir, fName)

    if path.exists(src_url):
        Copy(src_url, '.')
        return True
    return False


def Wget(url, fname, to=None):
    """
    Download :src: to :to: if required.

    :src: TODO
    :to: TODO
    :returns: TODO

    """
    if to is None:
        to = config["tmpdir"]

    from os import path
    from plumbum.cmd import wget

    src_dir = path.join(to, fname)
    if not source_required(fname, to):
        Copy(src_dir, ".")
        return

    wget(url, "-P", to)
    update_hash(fname, to)
    Copy(src_dir, ".")


def Git(url, fname, to=None):
    """
    Get a shallow clone from :src: to :to:.

    :src: TODO
    :to: TODO
    :returns: TODO

    """
    if to is None:
        to = config["tmpdir"]

    from os import path
    from plumbum.cmd import git

    src_dir = path.join(to, fname)
    if not source_required(fname, to):
        Copy(src_dir, ".")
        return

    git("clone", "--depth", "1", url, src_dir)
    update_hash(fname, to)
    Copy(src_dir, ".")


def Svn(url, fname, to=None):
    """get a shallow clone from :src to :to.

    :src: TODO
    :to: TODO
    :returns: TODO

    """
    if to is None:
        to = config["tmpdir"]

    from os import path
    from plumbum.cmd import svn

    src_dir = path.join(to, fname)
    if not source_required(fname, to):
        Copy(src_dir, ".")
        return

    svn("co", url, src_dir)
    update_hash(fname, to)
    Copy(src_dir, ".")


def Rsync(url, fname, to=None):
    """rsync :src to :to.

    :src: TODO
    :to: TODO
    :returns: TODO

    """
    if to is None:
        to = config["tmpdir"]

    from os import path
    from plumbum.cmd import rsync

    src_dir = path.join(to, fname)
    if not source_required(fname, to):
        Copy(src_dir, ".")
        return

    rsync("-a", url, src_dir)
    update_hash(fname, to)
    Copy(src_dir, ".")
