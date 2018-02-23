#!/bin/bash

# Usage:

output_dir=$1

DD=$(date +%d)
MM=$(date +%m)
project="test_innovation-map-read-names-to-umis_$MM-$DD"
output_directory=`python -c "import os;print(os.path.abspath('${output_dir}'))"`

# Run test pipeline
../../pipeline-runner.sh \
    ${project} \
    ../../cwl_tools/innovation-map-read-names-to-umis/innovation-map-read-names-to-umis.cwl \
    inputs.yaml \
    ${output_directory} \
    singleMachine
