#!/bin/bash


DD=$(date +%d)
MM=$(date +%m)
project="gatk_indelrealignment_test_$MM-$DD"
output_directory=`python -c "import os;print(os.path.abspath('/ifs/work/bergerm1/Innovation/sandbox/ian'))"`

# Run test pipeline
../../pipeline-runner.sh \
    ${project} \
    ../../tools/gatk/IndelRealignment.cwl \
    inputs.yaml \
    ${output_directory}
