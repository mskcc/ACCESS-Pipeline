#!/bin/bash

# Usage:

output_dir=$1

DD=$(date +%d)
MM=$(date +%m)
project="test_innovation-samtools-fastq_$MM-$DD"
output_directory=`python -c "import os;print(os.path.abspath('${output_dir}'))"`

# Run test pipeline
../../pipeline-runner.sh \
    ${project} \
    ../../cwl_tools/innovation-samtools-fastq/innovation-samtools-fastq.cwl \
    inputs.yaml \
    ${output_directory} \
    singleMachine
