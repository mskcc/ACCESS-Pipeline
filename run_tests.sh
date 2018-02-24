#!/usr/bin/env bash


output_dir=$1

if [ $# -eq 0 ]
  then
    echo "Please supply an output directory"
fi

for dir in `find ./test -type d` ; do
  echo "Running tests from ${dir}"

  if [[ "$dir" == "." ]]; then
    continue
  fi

  # Skip directory with test data
  if [[ $dir = *"test-data"* ]]; then
    echo "Skipping ${dir}"
    continue
  fi

  # Todo: Skipping untested directories
  if [[ $dir = *"__totest"* ]]; then
    echo "Skipping ${dir}"
    continue
  fi

  cd $dir ;

  for script in *.sh; do
    bash $script ${output_dir} ;
  done ;

  printf "\n\n\n"
  cd - ;
done
