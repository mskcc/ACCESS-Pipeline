#!/bin/bash

# Parse Inputs:
project=$1
workflow=$2
inputs=$3

# Create job-uuid
job_store_uuid=`python -c 'import uuid; print str(uuid.uuid1())'`

# Set output directory
jobstore_base="/ifs/work/bergerm1/Innovation/sandbox/ian/${project}/tmp/"

# Check if output directory already exists
if [ -d ${jobstore_base} ]
then
    echo "The specified output directory already exists: ${jobstore_base}"
    echo "Aborted."
    exit 1
fi

# Create output directory
mkdir -p ${jobstore_base}

# Set jobstore path
jobstore_path="${jobstore_base}/jobstore-${job_store_uuid}"

output_directory=`python -c "import os;print(os.path.abspath('/ifs/work/bergerm1/Innovation/sandbox/ian/${project}'))"`

# create output directory
mkdir -p ${output_directory}
mkdir -p ${output_directory}/log
mkdir -p ${output_directory}/tmp


cwltoil \
    ${workflow} \
    ${inputs} \
    --batchSystem singleMachine \
    --preserve-environment PATH PYTHONPATH CMO_RESOURCE_CONFIG \
    --defaultDisk 10G \
    --defaultMem 50G \
    --outdir ${output_directory} \
    --writeLogs	${output_directory}/log \
    --logFile ${output_directory}/log/cwltoil.log \
    --no-container \
    --disableCaching \
    --realTimeLogging \
    --workDir ${output_directory}/tmp \
    --jobStore file://${jobstore_path} \
    --logDebug \
    --cleanWorkDir never
