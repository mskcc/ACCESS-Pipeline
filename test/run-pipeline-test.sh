#!/bin/bash


output_dir=$1

D=$(date +%d)
m=$(date +%m)
H=$(date +%H)
M=$(date +%M)
project="pipeline_test_${m}-${D}_${H}-${M}"
output_directory=`python -c "import os;print(os.path.abspath('${output_dir}'))"`
job_store_uuid=`python -c 'import uuid; print str(uuid.uuid1())'`

# Run test pipeline
../pipeline-runner.sh \
    ${project} \
    ../workflows/standard_pipeline.cwl \
    inputs.yaml \
    ${output_directory} \
    singleMachine \
    ${job_store_uuid}
