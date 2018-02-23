#!/bin/bash

# Usage:

output_dir=$1

DD=$(date +%d)
MM=$(date +%m)
project="test_fulcrum_$MM-$DD"
output_directory=`python -c "import os;print(os.path.abspath('${output_dir}'))"`

# Run test pipeline
../../pipeline-runner.sh \
    ${project} \
    ../../workflows/fulcrum/fulcrum_workflow.cwl \
    inputs.yaml \
    ${output_directory} \
    singleMachine
