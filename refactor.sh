#!/bin/bash
repls=(
  's-%/$(PROJECT)$(BIN_EXT).profile.out:\ %/$(PROJECT)-%/$(PROFBIN_F):\ %/$(RUN_F)-'
  's-%/$(PROFBIN_F):\ $(RUN_F)-%/$(PROFBIN_F):\ %/$(RUN_F)-'
  's-${@D}-$(OUTDIR)-'
  's-$(PROJECT)$(BIN_EXT)$(PROFILE_EXT)-$(PROFBIN_F)-'
  's-$(PROJECT)$(TIME_EXT)-$(TIME_F)-'
  's-$(PROJECT).calls-$(CALLS_F)-'
  's-$(PROJECT).time-$(TIME_F)-'
  's-$(PROJECT).bin-$(BIN_F)-'
)
num_repls=${#repls[@]}

read -a files <<< $(find . -mindepth 3 -type f -name "Makefile" -exec grep -l PROJECT {} \; | sort)

for file in ${files[@]};
do
  for ((i=0; i<num_repls; i++));
  do
    sed -i "${repls[$i]}" $file
  done
done
