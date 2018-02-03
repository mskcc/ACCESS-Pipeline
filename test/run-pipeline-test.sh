#!/bin/bash

cwltoil \
    ../workflows/innovation_pipeline.cwl \
    inputs-pipeline-test.yaml \
    --batchSystem singleMachine \
    --preserve-environment PATH PYTHONPATH


# Additional options:
#
#    --batchSystem lsf --stats \
#    --restart \
#    --outDir .
#    --logDebug --cleanWorkDir never


#    --jobStore file://${jobstore_path} \
#    --defaultDisk 10G \
#    --defaultMem 50G \
#    --no-container \
#    --disableCaching \
#    --realTimeLogging \
#    --maxLogFileSize 0 \
#    --writeLogs	${output_directory}/log \
#    --logFile ${output_directory}/log/cwltoil.log \
#    --workDir ${ROSLIN_PIPELINE_BIN_PATH}/tmp \
