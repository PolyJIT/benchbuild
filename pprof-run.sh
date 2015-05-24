#!/bin/bash
#SBATCH -n 1
#SBATCH -p idle
#SBATCH -o /home/simbuerg/Projekte/pprof-study/tmp/pprof-%j.out
#SBATCH --job-name=pprof-sync
#SBATCH -c 8

SRCDIR=/home/simbuerg/Projekte/pprof-study
STUDYDIR=/local/hdd/simbuerg/pprof-study

sbatch --dependency=afterok:$SLURM_JOB_ID ./pprof-array.sh "${SRCDIR}" "${STUDYDIR}" $*
echo ":: Starting pprof"
echo "   Source Dir: ${SRCDIR}"
echo "   Execution in: ${STUDYDIR}"
