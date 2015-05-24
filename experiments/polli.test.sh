#!/bin/bash
#
# Timed calling of a binary, appending timing info to <bin-name>.time.
#
OPT_FLAGS="@OPT_FLAGS@"
POLLI_FLAGS="@POLLI_FLAGS@"

LIKWID="@LIKWID_BINARY@"
LIKWID_FILTER="@LIKWID_FILTER@"
EXPERIMENT="@EXPERIMENT@"

PROG=$0
INPUT_FILE="${PROG}.bin"
LINKER_INFO="$(basename ${PROG}).pprof"
RUN_ENV="$(basename ${PROG}).env"

REAL_PROG_WO_FILE="polli -fake-argv0=${PROG}-${EXPERIMENT} ${POLLI_FLAGS}"

if [ -f ${RUN_ENV} ]; then
  source ${RUN_ENV}
fi

if [ -f ${LINKER_INFO} ]; then
  REAL_PROG_WO_FILE="${REAL_PROG_WO_FILE} `cat ${LINKER_INFO}`"
fi

REAL_PROG="${REAL_PROG_WO_FILE} ${INPUT_FILE}"
TIME="${PROG}.time"
LIKWID_OUTPUT="${PROG}.likwid"

cmd="/usr/bin/time -f '%U,%S,%e' -a -o ${TIME} ${REAL_PROG} $*"
cmd="${REAL_PROG_WO_FILE} -lpprof"

if [[ ${REAL_PROG_WO_FILE} != *-no-recompilation* ]] ; then
  cmd="${cmd} -no-recompilation"
fi
cmd="${cmd} ${INPUT_FILE} $*"

echo ${cmd}
${cmd}
touch ${LIKWID_OUTPUT}
