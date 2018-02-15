#!/bin/bash


DD=$(date +%d)
MM=$(date +%m)
project="abra_test_$MM-$DD"
output_directory=`python -c "import os;print(os.path.abspath('/ifs/work/bergerm1/Innovation/sandbox/ian'))"`

# Run test pipeline
../../pipeline-runner.sh \
    ${project} \
    ../../tools/abra/2.07/abra.cwl \
    inputs.yaml \
    ${output_directory}
