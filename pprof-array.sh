#!/bin/bash
#SBATCH -o /home/simbuerg/src/polyjit/pprof-study/results/pprof-run-%j.out
#SBATCH --job-name=pprof-run
#SBATCH -p chimaira
#SBATCH -A cl
#SBATCH --get-user-env
#SBATCH --ntasks 1
#SBATCH --cpus-per-task 10
#SBATCH --hint=nomultithread
#SBATCH --array=1-84
#SBATCH --time="1-00:00"

# Call this script as follows:
# pprof-array.sh <srcdir>/ <studydir>/ "list of experiments" "list of targets" [config_num] [config_id]

opt_verbose=
opt_clean=
opt_clean_profiles=
opt_bootstrap=
while getopts ":bvcds:e:t:n:i:p:" opt; do
  case $opt in
    b)
      opt_bootstrap=1
      ;;
    v)
      opt_verbose=1
      ;;
    c)
      opt_clean=1
      ;;
    d)
      opt_clean_profiles=1
      ;;
    s)
      opt_srcdir="${OPTARG}"
      ;;
    e)
      opt_experiment="${OPTARG}"
      ;;
    t)
      opt_targets="${OPTARG}"
      ;;
    n)
      opt_config_num="${OPTARG}"
      ;;
    i)
      opt_config_id="${OPTARG}"
      ;;
    p)
      opt_preopt="${OPTARG}"
      ;;
    \?)
      echo "Invalid options: -$OPTARG" >&2
      exit 1
      ;;
    :)
      echo "Option -$OPTARG requires an argument." >&2
      exit 1
      ;;
  esac
done

# SETUP ENVIRONMENT
VERBOSE=$opt_verbose
SRCDIR=$opt_srcdir

builddir="/local/hdd/simbuerg/pprof-study"
if [ $opt_bootstrap ] ; then
  echo
  echo "Bootstrapping local hdd"
  rm -rf "$builddir"
  mkdir "$builddir"
  ln -sf "$builddir" "$SRCDIR/build"
  exit 0;
fi

# Fetch multiple experiments
read -a EXPERIMENTS <<< "$opt_experiment"

# Fetch all make targets from input string
read -a TARGETS <<< "$opt_targets"

# Get config id
CONFIG_NUM="$opt_config_num"
CONFIG_ID="$opt_config_id"

# Get all additional opt flags for preoptimization
PPROF_OPT_FLAGS="$opt_preopt"

lockfile="/tmp/pprof-rsync.lock"

# LLVM & POLLY
LD_LIBRARY_PATH=${HOME}/opt/llvm/Release/lib:${LD_LIBRARY_PATH}
LD_RUN_PATH=${HOME}/opt/llvm/Release/lib:${LD_RUN_PATH}
PATH=${HOME}/opt/llvm/Release/bin:${PATH}

# PAPI
LD_LIBRARY_PATH=${HOME}/opt/papi/lib:${LD_LIBRARY_PATH}
LD_RUN_PATH=${HOME}/opt/papi/lib:${LD_RUN_PATH}
PATH=${HOME}/opt/papi/bin:${PATH}

# Isl
LD_LIBRARY_PATH=${HOME}/opt/isl/lib:${LD_LIBRARY_PATH}
LD_RUN_PATH=${HOME}/opt/isl/lib:${LD_RUN_PATH}
PATH=${HOME}/opt/isl/bin:${PATH}

export LD_LIBRARY_PATH
export LD_RUN_PATH
export PATH
export VERBOSE

# Get the projects as array for indexing by task.
PROJECT_STRING=$(find . -mindepth 2 -type f -name "Makefile" -exec grep -l PROJECT {} \; | sort)
read -a PROJECT_ARRAY <<< $PROJECT_STRING
# The directory we want to call make in now. Format: domain/project
DIR_TO_MAKE=$(dirname ${PROJECT_ARRAY[${SLURM_ARRAY_TASK_ID} - 1]})

echo =================================================================
echo % PPROF Experiment\(s\): ${EXPERIMENTS[@]}
echo % Location: $DIR_TO_MAKE
echo % Preopt Flags: $PPROF_OPT_FLAGS
echo % Targets: ${TARGETS[@]}
echo % Task ID: ${SLURM_ARRAY_TASK_ID}
echo % Nodelist: ${SLURM_NODELIST}
echo =================================================================

# Run the experiments
export CONFIG_ID="${CONFIG_ID}"
export CONFIG_NUM=${CONFIG_NUM}

separator=
if [[ ! $CONFIG_NUM = "" ]];
then
	separator='_'
fi

export OPT_FLAGS="${PPROF_OPT_FLAGS}"

prj_dir_name=$(basename $DIR_TO_MAKE)
# Update our name to the test we are running
scontrol update JobID=$SLURM_JOB_ID name="$prj_dir_name (${TARGETS[@]})"

for exp in ${EXPERIMENTS[@]};
do
  export EXPERIMENT=${exp}
  # Clean project & result subdirs
  for target in ${TARGETS[@]};
  do
    [ $opt_clean ]          && make -C$SRCDIR/$DIR_TO_MAKE EXPERIMENT=${exp} \
                                    clean-${target}
    [ $opt_clean_profiles ] && make -C$SRCDIR/$DIR_TO_MAKE EXPERIMENT=${exp} \
                                    clean-prof-${target}

    make -C$SRCDIR/$DIR_TO_MAKE EXPERIMENT=${exp} ${target}
  done

  # Make the experiment
  # Sync back our results
  flock $lockfile \
          rsync -a "${SRCDIR}/build/${CONFIG_NUM}${separator}${exp}" \
	           "${SRCDIR}/results"

  # If we're the first task in the array, schedule a 'pack' job that packs
  # our results after the whole array is completed
  # We pack inside ${SRCDIR}: so it doesn't matter on which host we execute
  if [ $SLURM_ARRAY_TASK_ID -eq 1 ];
  then
	sbatch --dependency=afterany:${SLURM_ARRAY_JOB_ID} \
		./pprof-pack.sh "${SRCDIR}" ${exp} "${CONFIG_NUM}" \
				"${CONFIG_ID}" ${TARGETS[@]/#/pkg-}
  fi
done
