#!/bin/bash


output_dir=$1
output_dir='/ifs/work/bergerm1/Innovation/sandbox/ian'

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
