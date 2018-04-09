#!/bin/bash
set oux
revision_path=$(dirname $(realpath $0))
version_path="${revision_path}/benchbuild/__version__.py"
git_rev=$(git describe --tags)
echo "VERSION = \"$git_rev\"" > $version_path
