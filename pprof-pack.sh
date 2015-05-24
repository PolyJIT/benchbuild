#!/bin/bash
#SBATCH -o /home/simbuerg/src/polyjit/pprof-study/results/pprof-pack-%j.out
#SBATCH -p idle
#SBATCH -A idle
#SBATCH -n 1
#SBATCH -c 1
#SBATCh --time "5:00"
#SBATCH --job-name=pprof-pack

SRCDIR=$1
EXPERIMENT=$2
TARGETS=(${*:5})

export CONFIG_NUM=$3
export CONFIG_ID="$4"

echo =================================================================
echo % PPROF Package Results
echo % Experiment: ${EXPERIMENT}
echo % Targets: ${TARGETS[@]}
echo % Job ID: ${SLURM_JOB_ID}
echo % Nodelist: ${SLURM_NODELIST}
echo =================================================================

make EXPERIMENT=$EXPERIMENT -C$SRCDIR ${TARGETS[@]}
