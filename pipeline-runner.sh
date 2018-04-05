#!/bin/bash

##
# This script is used to run workflows from the command line.
# It does not submit jobs to worker nodes, as opposed to pipeline-submit, which uses bsub


# Parse Inputs:
project_name=$1
workflow=$2
inputs_file=$3
output_location=$4
batch_system=$5
job_store_uuid=$6


# Set output directory
output_directory="${output_location}/${project_name}"
jobstore_base="${output_directory}/tmp/"
jobstore_path="${jobstore_base}/jobstore-${job_store_uuid}"

# todo: Create "cleanup" step @ end of pipeline
printf "\n\n \033[31m Make sure you deleted the Abra scratch dir \n\n\ \033[m " > /dev/stderr

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

cmd="toil-cwl-runner \
    --outdir ${output_directory} \
    --batchSystem ${batch_system} \
    --preserve-environment PATH PYTHONPATH \
    --defaultDisk 10G \
    --defaultMem 10G \
    --no-container \
    --disableCaching \
    --writeLogs	${output_directory}/log \
    --logFile ${output_directory}/log/cwltoil.log \
    --workDir ${output_directory}/tmp \
    --jobStore file://${jobstore_path} \
    --cleanWorkDir onSuccess \
    --maxLogFileSize 20000000 \
    --logDebug \
    ${workflow} \
    ${inputs_file}"

printf "Running Toil with command:"
printf "${cmd}\n\n\n"

eval $cmd



# Arguments to research:
#    --realTimeLogging \
#    --rotateLogging \
# todo: in 3.15 this argument no longer works...?
#    --linkImports \
#    --stats \
#    2>&1 | awk '/Using the single machine batch system/ { system( "printf \"\n\n \033[31m WARNING: You are running on the head node \n\n\ \033[m \" > /dev/stderr" ) } { print $0 }'

# --js-console