#!/bin/bash
#
# Timed calling of a binary, appending timing info to <bin-name>.time.
#
PROG=$0
REAL_PROG="${PROG}.bin"

LIKWID="@LIKWID_BINARY@"
LIKWID_FILTER="@LIKWID_FILTER@"
LIKWID_OPTS="-O -C -L:0-1"

TIME="${PROG}.time"
LIKWID_OUTPUT="${PROG}.likwid"
command="/usr/bin/time -f '%U,%S,%e' -a -o ${TIME} ${LIKWID} ${LIKWID_OPTS}"

run=(
  "${command} -g CLOCK ${REAL_PROG} $*"
  "${command} -g CLOCK ${REAL_PROG} $*"
  )
#  "${command} -g DATA ${REAL_PROG} $*"
#  "${command} -g DATA ${REAL_PROG} $*"

echo
echo "$0: Executing tests..."
echo
for cmd in "${run[@]}" ; do
  echo "${cmd}"
  ${cmd} 2>&1 >> ${LIKWID_OUTPUT}
done
echo
echo "$0: Executing tests... finished"
