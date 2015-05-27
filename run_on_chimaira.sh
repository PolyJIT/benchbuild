#!/bin/sh
INSTALL_LLVM_TO=/scratch/simbuerg/pprof/install
BUILD_LLVM_IN=/scratch/simbuerg/pprof
PAPI_DIR=${HOME}/opt/papi
LIKWID_DIR=${HOME}/opt/likwid

# Adjust these, if necessary
export PPROF_DB_PASS=pprof
export PPROF_USE_DATABASE=1
export PPROF_DB_PORT=32768
export PPROF_DB_HOST=132.231.65.195
export PPROF_TMP_DIR=/scratch/simbuerg/pprof/src
export LD_LIBRARY_PATH=$PAPI_DIR/lib:$LD_LIBRARY_PATH

# Setup
git pull
pip install . --user --upgrade
pprof build -j 4 -B "$BUILD_LLVM_IN" -L "$LIKWID_DIR" -P "$PAPI_DIR"

builddir="$(date -I)"
PPROF_OBJ_DIR=/scratch/simbuerg/pprof/obj/${builddir}
if [ ! -d $PPROF_OBJ_DIR ] ; then
  mkdir $PPROF_OBJ_DIR
fi

./chimaira.py \
  --resultsdir $PPROF_OBJ_DIR \
  -P $PAPI_DIR \
  -L /usr \
  --llvm-prefix $INSTALL_LLVM_TO \
  --cpus-per-task 10 \
  $*
