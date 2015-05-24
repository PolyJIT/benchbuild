#!/bin/sh
builddir="$(date -I)"
mkdir /scratch/simbuerg/pprof/${builddir}
./chimaira.py \
  --resultsdir /scratch/simbuerg/pprof/${builddir} \
  -I /home/simbuerg/opt/isl \
  -P /home/simbuerg/opt/papi \
  -L /usr \
  --llvm-prefix /scratch/simbuerg/pprof/install \
  --cpus-per-task 10 \
  $*
