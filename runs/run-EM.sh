#!/bin/bash

pipeline_name_version="variant/1.3.1"

roslin-runner.sh \
    -v ${pipeline_name_version} \
    -w innovation_pipeline.cwl \
    -i inputs-EM.yaml \
    -b lsf \
    -d \
    -o /ifs/work/bergerm1/Innovation/sandbox/ian/outputs-EM-2
