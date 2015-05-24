#!/bin/bash
#
# Timed calling of a binary, appending timing info to <bin-name>.time.
#
OPT_FLAGS="@OPT_FLAGS@"
POLLI_FLAGS="@POLLI_FLAGS@"

LIKWID="@LIKWID_BINARY@"
LIKWID_FILTER="@LIKWID_FILTER@"

EXPERIMENT="@EXPERIMENT@"

LIKWID_CPUs=$(cat /proc/self/status | grep Cpus_allowed_list | awk '{print $2}')
#LIKWID_OPTS="-O -m -C ${LIKWID_CPUs}"
LIKWID_OPTS="-O -m -C -L:0"

# Likwid: Predefined sets
#
# BRANCH: Branch prediction miss rate/ratio
# CLOCK: Power and Energy consumption
# DATA: Load to store ratio
# ENERGY: Power and Energy consumption
# FLOPS_AVX: Packed AVX MFlops/s
# FLOPS_DP: Double Precision MFlops/s
# FLOPS_SP: Single Precision MFlops/s
# L2: L2 cache bandwidth in MBytes/s
# L2CACHE: L2 cache miss rate/ratio
# L3: L3 cache bandwidth in MBytes/s
# TLB: TLB miss rate/ratio


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

# Format: UserTime,SystemTime,WallClock
command="/usr/bin/time -f '%U,%S,%e' -a -o ${TIME} ${LIKWID} ${LIKWID_OPTS}"

run=(
  "${command} -g CLOCK ${REAL_PROG} $*"
  "${command} -g DATA ${REAL_PROG} $*"
  )
#  "${command} -g FLOPS_AVX ${REAL_PROG} $*"
#  "${command} -g FLOPS_DP ${REAL_PROG} $*"
#  "${command} -g FLOPS_SP ${REAL_PROG} $*"
#  "${command} -g L2 ${REAL_PROG} $*"
#  "${command} -g L2CACHE ${REAL_PROG} $*"
#  "${command} -g L3 ${REAL_PROG} $*"

function check_likwid {
  msr_files=$(find /dev/cpu -user "likwidd" | wc -l)
  cores=$(cat /proc/cpuinfo | grep processor | wc -l)

  if [[ "${msr_files}" != "${cores}" ]] ; then
    echo
    echo "Likwid configuration is possibly broken."
    echo "/dev/cpu/*/msr files with correct permissions: ${msr_files}"
    echo "Cores on host: ${cores}"
    echo
  fi
}

echo
echo "Checking for likwid..."
check_likwid

echo "Running benchmarks..."
for cmd in "${run[@]}" ; do
  echo "${cmd}"
  ${cmd} | tee -a ${LIKWID_OUTPUT}
done

cmd="${REAL_PROG_WO_FILE} -instrument -lpprof"
if [[ ${REAL_PROG_WO_FILE} != *-no-recompilation* ]] ; then
  cmd="${cmd} -no-recompilation"
fi
cmd="${cmd} ${INPUT_FILE} $*"

echo $cmd
${cmd} | tee -a ${LIKWID_OUTPUT}

# FIXME: SCoP coverage measurement breaks when we perform recompilation.
# We need to instrument the extracted SCoPs rather than the unfinished
# main module.
