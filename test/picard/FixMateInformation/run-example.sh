#!/bin/bash


DD=$(date +%d)
MM=$(date +%m)
project="picard_fixmateinformation_test_$MM-$DD"
output_directory=`python -c "import os;print(os.path.abspath('/ifs/work/bergerm1/Innovation/sandbox/ian'))"`

# Run test pipeline
../../../pipeline-runner.sh \
    ${project} \
    ../../../cwl_tools/picard/FixMateInformation/1.96/FixMateInformation.cwl \
    inputs.yaml \
    ${output_directory} \
    singleMachine
