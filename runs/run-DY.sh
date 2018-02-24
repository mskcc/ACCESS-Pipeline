#!/bin/bash


output_dir=$1

DD=$(date +%d)
MM=$(date +%m)
project="DY_$MM-$DD"
output_directory=`python -c "import os;print(os.path.abspath('${output_dir}'))"`

# Run test pipeline
../pipeline-runner.sh \
    ${project} \
    ../workflows/innovation_pipeline.cwl \
    ./inputs-DY.yaml \
    ${output_directory} \
    lsf
