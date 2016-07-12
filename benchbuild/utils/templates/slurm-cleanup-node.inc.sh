# Cleanup the cluster node, after the array has finished.\n"
file=$(mktemp -q) && {
  cat << EOF > $file
#!/bin/sh
#SBATCH --nice={nice_clean}
#SBATCH -o /dev/null
exec 1>> {logfile}
exec 2>&1
echo "$(date) [$(hostname)] node cleanup begin"
rm -r "{prefix}"
rm "{lockfile}"
echo "$(date) [$(hostname)] node cleanup end"
EOF
  _inner_file=$(mktemp -q) && {
    cat << EOF > $_inner_file
#!/bin/bash
if [ ! -f '{lockfile}' ]; then
  touch '{lockfile}'
  echo "$(date) [$(hostname)] clean for $(hostname)"
  sbatch --time="15:00" --job-name="$(hostname)-cleanup" \
    -A {slurm_account} -p {slurm_partition} \
    --dependency=afterany:$SLURM_ARRAY_JOB_ID \
    --nodelist=$SLURM_JOB_NODELIST -n 1 -c 1 "$file"
fi
EOF
  }
  flock -x "{lockdir}" bash $_inner_file
  rm -f "$file"
  rm -f "$_inner_file""
}
