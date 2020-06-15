#!/bin/bash
set -eu

ROOT="$(dirname "$(readlink -f "$0")")"
BUILDROOT="$ROOT/build"

echo
echo 'Build documentation'
echo

portray as_html -o "$BUILDROOT"

echo
echo "Documentation built in: $BUILDROOT"
echo
