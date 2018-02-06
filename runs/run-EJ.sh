#!/bin/bash


project="results-EJ_2_6"

job_store_uuid=`python -c 'import uuid; print str(uuid.uuid1())'`

jobstore_base="/ifs/work/bergerm1/Innovation/sandbox/ian/${project}/tmp/"

# check if output directory already exists
if [ -d ${jobstore_base} ]
then
    echo "The specified output directory already exists: ${jobstore_base}"
    echo "Aborted."
    exit 1
fi

mkdir -p ${jobstore_base}

jobstore_path="${jobstore_base}/jobstore-${job_store_uuid}"

output_directory=`python -c "import os;print(os.path.abspath('/ifs/work/bergerm1/Innovation/sandbox/ian/${project}'))"`

# create output directory
mkdir -p ${output_directory}
mkdir -p ${output_directory}/log
mkdir -p ${output_directory}/tmp


cwltoil \
    ../workflows/innovation_pipeline.cwl \
    inputs-EJ.yaml \
    --batchSystem lsf \
    --preserve-environment PATH PYTHONPATH CMO_RESOURCE_CONFIG \
    --defaultDisk 10G \
    --defaultMem 50G \
    --outdir ${output_directory} \
    --writeLogs	${output_directory}/log \
    --logFile ${output_directory}/log/cwltoil.log \
    --no-container \
    --cleanWorkDir never \
    --disableCaching \
    --realTimeLogging \
    --workDir ${output_directory}/tmp \
    --jobStore file://${jobstore_path}
