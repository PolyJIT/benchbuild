#!/bin/sh
INSTALL_LLVM_TO=/scratch/simbuerg/pprof/install
BUILD_LLVM_IN=/scratch/simbuerg/pprof
PAPI_DIR=${HOME}/opt/papi
export PPROF_OBJ_DIR=/scratch/simbuerg/pprof/obj/$(date -Ihours)

# Adjust these, if necessary
export PPROF_DB_PASS=pprof
export PPROF_USE_DATABASE=1
export PPROF_DB_PORT=32769
export PPROF_DB_HOST=debussy
export PPROF_TMP_DIR=/scratch/simbuerg/pprof/src
export PPROF_TESTINPUTS=/home/simbuerg/src/polyjit/pprof-test-data
export PPROF_CLUSTER_NODEDIR=/local/hdd/simbuerg
export PPROF_LIKWID_DIR=/usr
export LD_LIBRARY_PATH=$PAPI_DIR/lib:$LD_LIBRARY_PATH

# Setup
git pull
pip install . --user --upgrade
#pprof build -j 4 -B "$BUILD_LLVM_IN" -L "$PPROF_LIKWID_DIR" -P "$PAPI_DIR"

if [ ! -d $PPROF_OBJ_DIR ] ; then
  mkdir $PPROF_OBJ_DIR
fi

./chimaira.py \
  --resultsdir $PPROF_OBJ_DIR \
  -P $PAPI_DIR \
  -L /usr \
  --llvm-prefix $INSTALL_LLVM_TO \
  --cpus-per-task 2 \
  $*
