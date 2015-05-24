#!/bin/sh
#
# Timed calling of a binary, appending timing info to <bin-name>.time.
#
PROG=$0
REAL_PROG="${PROG}.bin"
REAL_PROG="polli -debug-only="polyjit" -no-recompilation -lpapi -lpprof -mcjit -jitable -polly-detect-keep-going -polly-detect-track-failures ${PROG} $*"
TIME="${PROG}.time"

# Format: UserTime,SystemTime,WallClock

# Paper Study: FIFO and Affinity
#exec /usr/bin/time -f "%U,%S,%e" -a -o ${TIME} taskset 0x00000004 chrt -f 20 ${REAL_PROG} $*

# Debug
#exec /usr/bin/time -f "%U,%S,%e" -a -o ${TIME} taskset 0x00000008 ${REAL_PROG} $*
exec /usr/bin/time -f "%U,%S,%e" -a -o ${TIME} ${REAL_PROG} $*
