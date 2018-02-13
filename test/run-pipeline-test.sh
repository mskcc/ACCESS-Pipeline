#!/bin/bash

# Usage:
# ./run-pipeline-test /output/location

output_location=$1

# Create output dir
DD=$(date +%d)
MM=$(date +%m)
project="pipeline_test_$MM-$DD"
output_directory=`python -c "import os;print(os.path.abspath('${output_location}/${project}'))"`

# Run test pipeline
./test-runner.sh \
    ${project} \
    ../workflows/innovation_pipeline.cwl \
    inputs-pipeline-test.yaml \
    ${output_directory}
