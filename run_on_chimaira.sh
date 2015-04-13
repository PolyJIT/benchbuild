#!/bin/sh
builddir="$(date -I)"
pip install driver/ --user --upgrade
pprof build -j 4 -B /scratch/simbuerg/pprof -I /home/simbuerg/opt/isl -L \
  /home/simbuerg/opt/likwid -P /home/simbuerg/opt/papi
mkdir /scratch/simbuerg/pprof/${builddir}
./chimaira.py \
  --resultsdir /scratch/simbuerg/pprof/${builddir} \
  -I /home/simbuerg/opt/isl \
  -P /home/simbuerg/opt/papi \
  -L /usr \
  --llvm-prefix /scratch/simbuerg/pprof/install \
  --cpus-per-task 10 \
  $*
