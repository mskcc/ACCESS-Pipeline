#!/bin/bash

# Parse Inputs:
project_name=$1
workflow=$2
inputs_file=$3
output_location=$4

# Create job-uuid
job_store_uuid=`python -c 'import uuid; print str(uuid.uuid1())'`

# Set output directory
output_directory="${output_location}/${project_name}"
jobstore_base="${output_directory}/tmp/"
jobstore_path="${jobstore_base}/jobstore-${job_store_uuid}"

# Check if output directory already exists
if [ -d ${output_directory} ]
then
    echo "The specified output directory already exists: ${output_directory}"
    exit 1
fi

# create output directory
mkdir -p ${output_directory}
mkdir -p ${output_directory}/log
mkdir -p ${output_directory}/tmp
mkdir -p ${jobstore_base}

toil-cwl-runner \
    --outdir ${output_directory} \
    --writeLogs	${output_directory}/log \
    --logFile ${output_directory}/log/cwltoil.log \
    --batchSystem singleMachine \
    --preserve-environment PATH PYTHONPATH CMO_RESOURCE_CONFIG \
    --defaultDisk 10G \
    --defaultMem 10G \
    --no-container \
    --disableCaching \
    --realTimeLogging \
    --workDir ${output_directory}/tmp \
    --jobStore file://${jobstore_path} \
    --cleanWorkDir never \
    ${workflow} \
    ${inputs_file}

#    --logDebug \