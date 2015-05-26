#!/bin/sh
builddir="$(date -I)"
pip install . --user --upgrade
pprof build -j 4 -B /scratch/simbuerg/pprof -L /home/simbuerg/opt/likwid -P /home/simbuerg/opt/papi

export PPROF_TMP_DIR=/scratch/simbuerg/pprof/src
PPROF_OBJ_DIR=/scratch/simbuerg/pprof/obj/${builddir}
mkdir $PPROF_OBJ_DIR
./chimaira.py \
  --resultsdir $PPROF_OBJ_DIR \
  -P /home/simbuerg/opt/papi \
  -L /usr \
  --llvm-prefix /scratch/simbuerg/pprof/install \
  --cpus-per-task 10 \
  $*
