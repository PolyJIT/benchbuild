#!/bin/bash
set -eu

die() { echo "ERROR: $*" >&2; exit 1; }

ROOT="$(dirname "$(readlink -f "$0")")"
BUILDROOT="$ROOT/build"

echo
echo 'Build documentation'
echo

mkdir -p "$BUILDROOT"
[ -d "$BUILDROOT" ] || die "could not create BUILDROOT"

pdoc3 --html -c show_type_annotations=True -o "$BUILDROOT" benchbuild

echo
echo "Documentation built in: $BUILDROOT"
echo
