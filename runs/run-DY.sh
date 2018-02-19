#!/bin/bash


DD=$(date +%d)
MM=$(date +%m)
project="DY_$MM-$DD"
output_directory=`python -c "import os;print(os.path.abspath('/ifs/work/bergerm1/Innovation/sandbox/ian'))"`

# Run test pipeline
../pipeline-runner.sh \
    ${project} \
    ../workflows/innovation_pipeline.cwl \
    ./inputs-DY.yaml \
    ${output_directory} \
    lsf