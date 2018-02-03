#!/usr/bin/env bash



cwltoil \
    ${ROSLIN_PIPELINE_BIN_PATH}/cwl/${workflow_filename} \
    ${input_filename} \
    --jobStore file://${jobstore_path} \
    --defaultDisk 10G \
    --defaultMem 50G \
    --preserve-environment PATH PYTHONPATH \
    --no-container \
    --disableCaching \
    --realTimeLogging \
    --maxLogFileSize 0 \
    --writeLogs	${output_directory}/log \
    --logFile ${output_directory}/log/cwltoil.log \
    --workDir ${ROSLIN_PIPELINE_BIN_PATH}/tmp \
    --outdir ${output_directory} ${restart_options} ${batch_sys_options} ${debug_options} \
    | tee ${output_directory}/output-meta.json

exit_code=$?
