#!/bin/bash

pipeline_name_version="variant/1.3.1"

roslin-runner.sh \
    -v ${pipeline_name_version} \
    -w innovation_pipeline.scatter.cwl \
    -i inputs-EJ.yaml \
    -b lsf \
    -d \
    -o /ifs/work/bergerm1/Innovation/sandbox/ian/outputs-EJ-1-16-2018--debug
