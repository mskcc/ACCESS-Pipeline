#!/bin/bash

# Usage:

output_dir=$1
output_dir='/ifs/work/bergerm1/Innovation/sandbox/ian'

DD=$(date +%d)
MM=$(date +%m)
project="test_marianas-duplex_$MM-$DD"
output_directory=`python -c "import os;print(os.path.abspath('${output_dir}'))"`

../../pipeline-runner.sh \
    ${project} \
    ../../workflows/marianas/marianas_collapsing_workflow_duplex.cwl \
    inputs.yaml \
    ${output_directory} \
    singleMachine


# Simplex + Duplex

project="test_marianas-simplex-duplex_$MM-$DD"
output_directory=`python -c "import os;print(os.path.abspath('${output_dir}'))"`

../../pipeline-runner.sh \
    ${project} \
    ../../workflows/marianas/marianas_collapsing_workflow_simplex_duplex.cwl \
    inputs.yaml \
    ${output_directory} \
    singleMachine
