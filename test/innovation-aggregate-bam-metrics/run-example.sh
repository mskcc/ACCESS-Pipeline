#!/bin/bash


DD=$(date +%d)
MM=$(date +%m)
project="test_innovation-aggregate-bam-metrics_$MM-$DD"
output_directory=`python -c "import os;print(os.path.abspath('/ifs/work/bergerm1/Innovation/sandbox/ian'))"`

# Run test pipeline
../../pipeline-tester.sh \
    ${project} \
    ../../cwl_tools/innovation-aggregate-bam-metrics/innovation-aggregate-bam-metrics.cwl \
    inputs.yaml \
    ${output_directory}
