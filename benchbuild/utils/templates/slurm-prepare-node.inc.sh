# Lock node dir preparation
exec 9> {lockfile}
flock -x 9 && {
  if [ ! -d '{prefix}' ]; then
    echo "$(date) [$(hostname)] copy LLVM to node"
    mkdir -p '{prefix}'
    tar xaf '{node_image}' -C '{prefix}'
  fi
  rm '{lockfile}'
}
exec 9>&-
