#!/bin/bash


output_dir=$1

DD=$(date +%d)
MM=$(date +%m)
project="abra_test_$MM-$DD"
output_directory=`python -c "import os;print(os.path.abspath('${output_dir}'))"`

# Run test pipeline
../../pipeline-runner.sh \
    ${project} \
    ../../cwl_tools/abra/2.07/abra.cwl \
    inputs.yaml \
    ${output_directory} \
    singleMachine
