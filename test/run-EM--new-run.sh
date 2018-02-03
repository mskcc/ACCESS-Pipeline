#!/bin/bash

pipeline_name_version="variant/1.3.1"

roslin-runner.sh \
    -v ${pipeline_name_version} \
    -w innovation_pipeline.cwl \
    -i inputs-EM--new-run.yaml \
    -b lsf \
    -o /ifs/work/bergerm1/Innovation/sandbox/ian/outputs-EM--new-run--restarted \
    -r 9fe8b776-07bc-11e8-9244-8cdcd4013cd4
