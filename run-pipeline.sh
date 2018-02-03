#!/usr/bin/env bash



cmd="cwltoil \
    ${ROSLIN_PIPELINE_BIN_PATH}/cwl/${workflow_filename} \
    ${input_filename} \
    --jobStore file://${jobstore_path} \
    --defaultDisk 10G \
    --defaultMem 50G \
    --preserve-environment PATH PYTHONPATH ROSLIN_PIPELINE_DATA_PATH ROSLIN_PIPELINE_BIN_PATH ROSLIN_EXTRA_BIND_PATH ROSLIN_PIPELINE_WORKSPACE_PATH ROSLIN_PIPELINE_OUTPUT_PATH ROSLIN_SINGULARITY_PATH CMO_RESOURCE_CONFIG \
    --no-container \
    --disableCaching \
    --realTimeLogging \
    --maxLogFileSize 0 \
    --writeLogs	${output_directory}/log \
    --logFile ${output_directory}/log/cwltoil.log \
    --workDir ${ROSLIN_PIPELINE_BIN_PATH}/tmp \
    --outdir ${output_directory} ${restart_options} ${batch_sys_options} ${debug_options} \
    | tee ${output_directory}/output-meta.json
exit_code=$?"

echo $cmd
