#!/bin/bash

pipeline_name_version="variant/1.3.1"

roslin-runner.sh \
    -v ${pipeline_name_version} \
    -w innovation_pipeline.cwl \
    -i inputs-EN.yaml \
    -b lsf \
    -o /ifs/work/bergerm1/Innovation/sandbox/ian/outputs-EN--restarted \
    -r 83e27b66-077b-11e8-bf8b-8cdcd4013cd4
