#!/usr/bin/env bash


for dir in `find ./test -type d` ; do
  echo "Running tests from ${dir}"

  if [[ "$dir" == "." ]]; then
    continue
  fi

  # Skip directory with test data
  if [[ $dir = *"test-data"* ]]; then
    continue
  fi

  # Todo: Skipping untested directories
  if [[ $dir = *"__totest"* ]]; then
    continue
  fi

  cd $dir ;

  for script in *.sh; do
    bash $script ;
  done ;

  cd - ;
done
